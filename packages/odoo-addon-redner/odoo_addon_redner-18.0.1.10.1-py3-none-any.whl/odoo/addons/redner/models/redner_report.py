##############################################################################
#
#    Redner Odoo module
#    Copyright © 2016, 2024 XCG SAS <https://orbeet.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# Much of this is based on OCA's report_py3o module (11.0 branch).

import base64
import logging
import os
import tempfile
from contextlib import closing
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..utils import formats
from ..utils.formats import Formats

logger = logging.getLogger(__name__)

_pypdf2 = False
try:
    from pypdf import PdfWriter
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter

    _pypdf2 = True


class RednerReport(models.TransientModel):
    _name = "redner.report"
    _description = "Report Redner"

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report", required=True
    )

    def _postprocess_report(self, model_instance, result_path):
        if len(model_instance) == 1 and self.ir_actions_report_id.attachment:
            with open(result_path, "rb") as f:
                # we do all the generation process using files to avoid memory
                # consumption...
                # ... but odoo wants the whole data in memory anyways :)
                buffer = BytesIO(f.read())
                self.ir_actions_report_id.postprocess_redner_report(
                    model_instance, buffer
                )
        return result_path

    def _create_single_report(self, model_instances, data):
        """This function generates our redner report"""

        self.ensure_one()
        report_xml = self.ir_actions_report_id

        data = self._get_report_data(model_instances)
        metadata = report_xml.get_report_metadata()

        fformat = Formats().get_format(self.ir_actions_report_id.redner_filetype)

        try:
            res = report_xml.redner_tmpl_id.redner.templates.render(
                report_xml.redner_tmpl_id.redner_id,
                data,
                accept=fformat.mimetype,
                metadata=metadata,
            )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                _(
                    "We received an unexpected error from redner server. "
                    "Please contact your administrator"
                )
            ) from e

        content = base64.b64decode(res[0]["body"])

        # Use NamedTemporaryFile for secure temporary file creation
        # This prevents TOCTOU race condition vulnerabilities
        with tempfile.NamedTemporaryFile(
            suffix="." + report_xml.redner_filetype,
            prefix="redner-report-",
            delete=False,
        ) as tmp_file:
            tmp_file.write(content)
            report_file = tmp_file.name

        self._postprocess_report(model_instances, report_file)
        return report_file

    def _get_or_create_single_report(
        self, model_instance, data, existing_reports_attachment
    ):
        self.ensure_one()
        attachment = existing_reports_attachment.get(model_instance.id)
        if attachment and self.ir_actions_report_id.attachment_use:
            content = base64.decodebytes(attachment.datas)
            # Use NamedTemporaryFile for secure temporary file creation
            with tempfile.NamedTemporaryFile(
                suffix="." + self.ir_actions_report_id.redner_filetype,
                prefix="redner-cached-",
                delete=False,
            ) as tmp_file:
                tmp_file.write(content)
                report_file = tmp_file.name
            return report_file
        return self._create_single_report(model_instance, data)

    def _zip_results(self, reports_path):
        self.ensure_one()
        zfname_prefix = self.ir_actions_report_id.name
        # Use NamedTemporaryFile for secure temporary file creation
        with tempfile.NamedTemporaryFile(
            suffix=".zip", prefix="redner-zip-result-", delete=False
        ) as tmp_file:
            result_path = tmp_file.name
        # Create ZIP file at the secure path
        with ZipFile(result_path, "w", ZIP_DEFLATED) as zf:
            cpt = 0
            for report in reports_path:
                fname = "{}_{}.{}".format(
                    zfname_prefix,
                    cpt,
                    report.split(".")[-1],
                )
                zf.write(report, fname)

                cpt += 1
        return result_path

    @api.model
    def _merge_pdf(self, reports_path):
        """Merge PDF files into one.
        :param reports_path: list of path of pdf files
        :returns: path of the merged pdf
        """
        writer = PdfFileWriter() if _pypdf2 else PdfWriter()
        for path in reports_path:
            if _pypdf2:
                reader = PdfFileReader(path)
                writer.appendPagesFromReader(reader)
            else:
                writer.append(path)
        merged_file_fd, merged_file_path = tempfile.mkstemp(
            suffix=".pdf", prefix="report.merged.tmp."
        )
        with closing(os.fdopen(merged_file_fd, "wb")) as merged_file:
            writer.write(merged_file)
        return merged_file_path

    def _merge_results(self, reports_path):
        self.ensure_one()
        filetype = self.ir_actions_report_id.redner_filetype
        if not reports_path:
            return False, False
        if len(reports_path) == 1:
            return reports_path[0], filetype
        if filetype == formats.FORMAT_PDF:
            return self._merge_pdf(reports_path), formats.FORMAT_PDF
        return self._zip_results(reports_path), "zip"

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except OSError:
                logger.error("Error when trying to remove file %s", temporary_file)

    def create_report(self, res_ids, data):
        """Produce the report, return PDF data & file extension"""

        self.ensure_one()

        report_xml = self.ir_actions_report_id

        model_instances = self.env[report_xml.model].browse(res_ids)

        reports_path = []
        if len(res_ids) > 1 and report_xml.redner_multi_in_one:
            reports_path.append(self._create_single_report(model_instances, data))
        else:
            existing_reports_attachment = report_xml._get_attachments(res_ids)
            for model_instance in model_instances:
                reports_path.append(
                    self._get_or_create_single_report(
                        model_instance, data, existing_reports_attachment
                    )
                )

        result_path, filetype = self._merge_results(reports_path)
        reports_path.append(result_path)

        # Here is a little joke about Odoo
        # we do all the generation process using files to avoid memory
        # consumption...
        # ... but odoo wants the whole data in memory anyways :)

        with open(result_path, "r+b") as fd:
            res = fd.read()
        self._cleanup_tempfiles(set(reports_path))
        return res, filetype

    def _get_report_data(self, records):
        if not records:
            return {}

        floor_conv = self.ir_actions_report_id.substitution_ids.filtered(
            lambda sub: sub.depth == 0
        ).build_converter()
        ret = floor_conv.odoo_to_message({}, records) or {}

        filtered_lines = self.ir_actions_report_id.substitution_ids.filtered(
            lambda sub: (sub.depth == 1 and sub.keyword.startswith("records."))
        )
        if filtered_lines:
            down_conv = filtered_lines.build_converter()
            ret["records"] = [
                down_conv.odoo_to_message({}, record) for record in records
            ]

        return ret
