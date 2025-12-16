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

import json
import mimetypes
from urllib.parse import parse_qs

from odoo import _
from odoo.addons.web.controllers.report import (
    ReportController as BaseReportController,
)
from odoo.http import (
    content_disposition,
    request,
    route,
    serialize_exception,
)
from odoo.tools import html_escape
from werkzeug import exceptions


class ReportController(BaseReportController):
    """Add redner report downloads within report controllers.
    Much of this code comes from OCA modules, the latest one being report_xlsx.
    """

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter != "redner":
            return super().report_routes(
                reportname=reportname,
                docids=docids,
                converter=converter,
                **data,
            )
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(",")]
        if data.get("options"):
            data.update(json.loads(data.pop("options")))
        if data.get("context"):
            # Ignore 'lang' here, because the context in data is the
            # one from the webclient *but* if the user explicitly wants to
            # change the lang, this mechanism overwrites it.
            data["context"] = json.loads(data["context"])
            if data["context"].get("lang"):
                del data["context"]["lang"]
            context.update(data["context"])

        ir_action = request.env["ir.actions.report"]
        action_redner_report = ir_action.get_from_report_name(
            reportname, "redner"
        ).with_context(**context)
        if not action_redner_report:
            raise exceptions.HTTPException(
                description=_(
                    "Redner action report not found for report_name %s",
                    reportname,
                )
            )
        res, filetype = action_redner_report._render(reportname, docids, data)
        filename = action_redner_report.gen_report_download_filename(docids, data)
        if not filename.endswith(filetype):
            filename = f"{filename}.{filetype}"
        content_type = mimetypes.guess_type("x." + filetype)[0]
        http_headers = [
            ("Content-Type", content_type),
            ("Content-Length", len(res)),
            ("Content-Disposition", content_disposition(filename)),
        ]
        return request.make_response(res, headers=http_headers)

    @route()
    def report_download(self, data, context=None, token=None):
        """This function is used by 'action_manager_report.js' in order to
        trigger the download of a pdf/controller report.

        :param data: a javascript array JSON.stringified containing report
            internal url ([0]) and type [1]
        :returns: Response with an attachment header
        """
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        if "redner" not in report_type:
            return super().report_download(data, context=context, token=token)
        try:
            reportname = url.split("/report/redner/")[1].split("?")[0]
            docids = None
            if "/" in reportname:
                reportname, docids = reportname.split("/")

            if docids:
                # Generic report:
                response = self.report_routes(
                    reportname,
                    docids=docids,
                    converter="redner",
                    context=context,
                )
            else:
                # Particular report:
                # decoding the args represented in JSON
                data = list(parse_qs(url.split("?")[1]).items())
                if "context" in data:
                    context, data_context = (
                        json.loads(context or "{}"),
                        json.loads(data.pop("context")),
                    )
                    context = json.dumps({**context, **data_context})
                response = self.report_routes(
                    reportname, converter="redner", context=context, **data
                )
            return response
        except Exception as e:
            se = serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            return request.make_response(html_escape(json.dumps(error)))
