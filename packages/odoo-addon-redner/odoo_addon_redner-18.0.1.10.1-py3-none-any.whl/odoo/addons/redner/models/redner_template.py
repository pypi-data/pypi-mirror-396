##############################################################################
#
#    Redner Odoo module
#    Copyright © 2016, 2024, 2025 XCG SAS <https://orbeet.io/>
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

import base64
import logging
from typing import Final, Literal

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.cache import ormcache

from ..redner import Redner
from ..utils.mimetype import get_file_extension

logger = logging.getLogger(__name__)

_redner: Redner | None = None
_redner_params: dict[str, str | int | None] = {}

LANGUAGE_MJML_MUSTACHE: Final[str] = "text/mjml|mustache"
LANGUAGE_TYPST_MUSTACHE: Final[str] = "text/typst|mustache"
LANGUAGE_OPENDOCUMENT_MUSTACHE: Final[str] = (
    "application/vnd.oasis.opendocument.text|od+mustache"
)
DEFAULT_LANGUAGE = LANGUAGE_MJML_MUSTACHE
COMPUTED_FIELDS = (
    "body",
    "description",
    "slug",
    "is_mjml",
    "language",
    "locale_id",
)
EDITABLE_FIELDS = (
    "redner_id",
    "name",
)


class RednerTemplate(models.Model):
    _name = "redner.template"
    _description = "Redner Template"

    source = fields.Selection(
        string="Source",
        selection=[
            ("redner", "Redner"),
            ("odoo", "Odoo"),
        ],
        required=True,
        default="odoo",
        help="Source of the template, created in Odoo or imported from Redner.",
        copy=False,
    )

    allow_modification_from_odoo = fields.Boolean(
        string="Allow modification from odoo",
        required=True,
        default=True,
        help=(
            "If Odoo can edit the template. If the source is redner,"
            " by default Odoo can't edit the template."
            "It is invisible and set to True if the source is Odoo."
        ),
    )

    preview = fields.Binary(
        string="Preview",
        default="New",
        compute="_compute_preview",
        help="This is a preview of the template",
    )

    name = fields.Char(
        string="Name",
        default="New",
        required=True,
        help=(
            "The name of the template. Once the template is created, "
            "updating the name is not allowed. To change the name, "
            "delete the template and create a new one."
        ),
    )

    description = fields.Char(
        string="Description",
        help="Description of the template",
        default="New",
        readonly=False,
        compute="_compute_template",
    )

    body = fields.Text(
        string="Template body",
        translate=True,
        help="Code for the mjml redner template must be added here",
        readonly=False,
        compute="_compute_template",
    )

    slug = fields.Char(
        string="Slug",
        readonly=False,
        compute="_compute_template",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        help=(
            "If unchecked, it will allow you to hide the template without removing it."
        ),
    )

    is_mjml = fields.Boolean(
        string="Is MJML",
        default=True,
        help="set to false if your template doesn't contain MJML",
        readonly=False,
        compute="_compute_template",
    )

    detected_keywords = fields.Text(
        string="Variables", readonly=True, compute="_compute_keywords"
    )

    language = fields.Selection(
        string="Language",
        selection=[
            ("text/html|mustache", "HTML + mustache"),
            (LANGUAGE_MJML_MUSTACHE, "MJML + mustache"),
            (LANGUAGE_TYPST_MUSTACHE, "Typst + mustache"),
            (
                LANGUAGE_OPENDOCUMENT_MUSTACHE,
                "OpenDocument + mustache",
            ),
        ],
        default="text/html|mustache",
        help="templating language",
        readonly=False,
        compute="_compute_template",
    )

    redner_id = fields.Char(string="Redner ID", readonly=True, index=True, copy=False)

    locale_id = fields.Many2one(
        comodel_name="res.lang",
        string="Locale",
        help="Translation language (ISO code).",
        readonly=False,
        required=True,
        default=lambda self: self.env["res.lang"]
        .search([("code", "=", self.env.user.lang)], limit=1)
        .id,
        compute="_compute_template",
    )

    template_data = fields.Binary(
        string="Libreoffice Template",
        readonly=False,
        compute="_compute_template_data",
        inverse="_inverse_template_data",
    )

    template_data_filename = fields.Char(
        string="Libreoffice Template Filename",
        compute="_compute_template_data_filename",
    )

    can_view_in_redner = fields.Boolean(compute="_compute_can_view_in_redner")

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends("body", "template_data")
    def _compute_keywords(self):
        for record in self:
            record.detected_keywords = "\n".join(record.template_varlist_fetch())

    @api.depends("body", "template_data")
    def _compute_preview(self):
        for record in self:
            if record.body or record.template_data:
                record.preview = self.get_preview(record.redner_id)
            else:
                record.preview = False

    def _compute_template(self):
        """
        Computes the template values for the records and applies cached or fetched data.
        """
        for record in self:
            if not record.id or not record.redner_id:
                continue

            # Fetch the cached template
            cached_template = self._get_template(record.redner_id)

            if not any([getattr(record, f) for f in COMPUTED_FIELDS]):
                # If all computed fields are undefined, populate them
                # from the cached template.
                for f in COMPUTED_FIELDS + EDITABLE_FIELDS:
                    if f in cached_template:
                        setattr(record, f, cached_template[f])
            else:
                # If at least one field is defined, populate only undefined fields
                for f in COMPUTED_FIELDS:
                    if not getattr(record, f):
                        setattr(record, f, cached_template.get(f, None))

    def _inverse_template_data(self):
        """
        Inverse function for `template_data`. Called when `template_data` is"
        manually set.
        """
        for record in self:
            if not record.template_data or not record.id or not record.language:
                continue
            try:
                # Update the external system with the new data
                self._set_cached_template(record.id, record.template_data)
            except Exception as e:
                logger.error("Failed to update template data in Redner: %s", e)
                raise ValidationError(
                    _(
                        "Unable to update the template data. Please check the logs "
                        "for more details."
                    )
                ) from e

    def _compute_template_data(self):
        for record in self:
            # Skip records that do not have a redner_id or are missing essential data
            if not record.id or not record.redner_id:
                continue

            if (
                not record.template_data
                and record.language == LANGUAGE_OPENDOCUMENT_MUSTACHE
            ):
                cached_template = self._get_template(record.redner_id)

                template_data = (
                    cached_template.get("template_data") if cached_template else None
                )
                if template_data:
                    try:
                        # Perform base64 encoding and store the result
                        record.template_data = base64.b64encode(template_data).decode(
                            "utf-8"
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to encode redner template data for record %s: %s",
                            record.id,
                            e,
                        )
                        continue  # Proceed with next record if encoding fails

    @api.depends("template_data")
    def _compute_template_data_filename(self):
        """Compute the template filename based on the template data"""
        for record in self:
            if not record.id or not record.redner_id or not record.template_data:
                record.template_data_filename = (
                    f"{record.name}.odt" if record.name else "template.odt"
                )
            else:
                try:
                    # Attempt to extract the file extension from the base64 data
                    ext = get_file_extension(record.template_data)
                    record.template_data_filename = f"{record.name}{ext}"

                except Exception:
                    logger.error("Error while computing template filename")
                    record.template_data_filename = False

    def _compute_can_view_in_redner(self):
        for template in self:
            template.can_view_in_redner = (
                template.redner_id
                and self.redner.get_template_url(template.redner_id) is not None
            )

    @property
    def redner(self):
        """
        Returns a Redner instance.
        Recomputes the instance if any system parameter changes.
        Uses a global variable to cache the instance across sessions.
        """
        global _redner, _redner_params

        # Fetch current system parameters
        config_model = self.env["ir.config_parameter"].sudo()
        current_params = {
            "api_key": config_model.get_param("redner.api_key"),
            "server_url": config_model.get_param("redner.server_url"),
            "account": config_model.get_param("redner.account"),
            "timeout": int(config_model.get_param("redner.timeout", default="20")),
        }

        # Check if parameters have changed or if _redner is None
        if _redner is None or _redner_params != current_params:
            _redner = Redner(
                current_params["api_key"],
                current_params["server_url"],
                current_params["account"],
                current_params["timeout"],
            )
            # Recompute the Redner instance
            _redner_params = current_params  # Update the stored parameters

        return _redner

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """Overwrite create to create redner template"""

        for vals in vals_list:
            # redner_id already filled in, no need to add the template
            if vals.get("redner_id", False):
                continue  # Continue processing the next record

            self._redner_template_add(vals)

        return super().create(vals_list)

    def _redner_template_add(self, vals):
        # Prepare template params according to the selected language.
        # Use template data field if the selected language is "od";
        # otherwise the body field is used.
        produces, language = (
            self.language if self else vals.get("language", DEFAULT_LANGUAGE)
        ).split("|")
        body, body_format = (
            (self.template_data if self else vals.get("template_data"), "base64")
            if language == "od+mustache"
            else (self.body if self else vals.get("body"), "text")
        )

        locale = (
            self.locale_id.code
            if self
            else self.env["res.lang"].browse(vals.get("locale_id")).code
        )

        # We depend on the API for consistency here
        # So raised error should not result with a created template
        if language and body:
            redner_template = self.redner.templates.account_template_add(
                language=language,
                body=body,
                name=self.name if self and self.name else vals.get("name"),
                description=self.description if self else vals.get("description"),
                produces=produces,
                body_format=body_format,
                version=fields.Datetime.to_string(fields.Datetime.now()),
                locale=locale if locale else "fr_FR",
            )
            vals["redner_id"] = redner_template["name"]

    def write(self, vals):
        """Overwrite write to update redner template"""

        # Determine if we should update redner or not
        should = self._should_update_redner(vals)

        # Perform the write operation
        ret = super().write(vals)

        # Update Redner templates if applicable
        if should:
            for record in self:
                if record.redner_id:
                    if record.allow_modification_from_odoo:
                        record._sync_with_redner()
                else:
                    vals_copy = vals.copy()
                    record._redner_template_add(vals_copy)
                    record.redner_id = vals_copy["redner_id"]

        return ret

    def unlink(self):
        """Overwrite unlink to delete redner template"""

        # We do NOT depend on the API for consistency here
        # So raised error should not result block template deletion
        for record in self:
            if record.redner_id and record.allow_modification_from_odoo:
                try:
                    self.redner.templates.account_template_delete(record.redner_id)
                except Exception as e:
                    logger.warning(
                        "Failed to delete Redner template with ID %s. Reason: %s",
                        record.redner_id,
                        e,
                    )
        # TODO why clear the cache?
        self.env.registry.clear_cache()
        return super().unlink()

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for template, vals in zip(self, vals_list, strict=True):
            if "name" not in default:
                vals["name"] = _("%s (copy)", template.name)
            template._redner_template_add(vals)
        return vals_list

    # ------------------------------------------------------------
    # ACTIONS / BUSINESS
    # ------------------------------------------------------------

    def _should_update_redner(self, vals):
        """
        Determine if Redner should be updated based on the modified fields.
        """
        for field in [*COMPUTED_FIELDS, "template_data"]:
            if field in vals:
                current_value = getattr(self, field)
                if vals[field] != current_value and vals[field]:
                    return True
        return False

    def _sync_with_redner(self):
        """
        Sync the current record's template with Redner.
        """
        self.ensure_one()
        try:
            # Check if 'language' is a valid string before splitting
            if isinstance(self.language, str) and "|" in self.language:
                produces, language = self.language.split("|")
            else:
                logger.warning(
                    "Invalid language format for record %s: %s",
                    self.id,
                    self.language,
                )
            body, body_format = (
                (self.template_data.decode(), "base64")
                if language == "od+mustache"
                else (self.body, "text")
            )

            # Use the existing `redner_id`
            redner_id = self.redner_id

            self._update_redner_template(
                template_id=redner_id,
                language=language,
                body=body,
                name=self.name,
                description=self.description,
                produces=produces,
                body_format=body_format,
                version=fields.Datetime.to_string(self.write_date),
                locale=self.locale_id.code,
            )
        except Exception as e:
            logger.error("Failed to sync with Redner template: %s", e)
            raise ValidationError(_("Failed to update Redner template, %s", e)) from e

    def _update_redner_template(self, **kwargs):
        """
        Perform the Redner `account_template_update` API call.

        :param kwargs: Payload for the `account_template_update` API.
        """
        try:
            self.redner.templates.account_template_update(**kwargs)
            # XXX why is the cache cleared?
            self.env.registry.clear_cache()
        except Exception as e:
            logger.error("Redner API update failed: %s", e)
            raise ValueError("Unable to update the Redner template.") from e

    # XXX Is the cache correctly reset when the template changes?
    @api.model
    @ormcache("redner_uid")
    def get_preview(self, redner_uid) -> bytes | Literal[False]:
        """
        Retrieve the preview of a Redner template by its ID.
        :return: False or a base64 encoded value of the preview
        """
        if not redner_uid:
            return False

        result = False
        try:
            response = self.redner.templates.account_template_preview(redner_uid)
            result = base64.b64encode(response.content)
        except Exception as e:
            logger.error(
                "Failed to get preview of Redner template with ID %s: %s", redner_uid, e
            )
        return result

    @api.model
    def _to_odoo_template(self, template):
        """
        Convert the external template to the Odoo format.
        """
        language = "{}|{}".format(template.get("produces"), template.get("language"))

        odoo_template = {
            "name": template.get("name"),
            "description": template.get("description", ""),
            "redner_id": template.get("name"),
            "locale_id": self.env["res.lang"].search(
                [("code", "=", template.get("locale", "fr_FR"))], limit=1
            ),
            "language": language,
            "slug": template.get("slug"),
            "is_mjml": language == LANGUAGE_MJML_MUSTACHE,
            "body": "",
            "template_data": False,
        }
        match template.get("body-format"):
            case "base64":
                body = base64.b64decode(template.get("body", ""))
            case _:
                body = template.get("body", "")
        if template.get("language") == "od+mustache":
            odoo_template["template_data"] = body
        else:
            odoo_template["body"] = body
        return odoo_template

    @api.model
    @ormcache("redner_uid")
    def _get_template(self, redner_uid):
        """
        Retrieves and caches the template from Redner for a given record.
        """
        if not redner_uid:
            return {}
        try:
            # Fetch the template from the external system
            template = self.redner.templates.account_template_read(redner_uid)
            # Convert the template to Odoo's format
            return self._to_odoo_template(template)
        except Exception as e:
            logger.error("Failed to read Redner template: %s", e)
            return {}

    # XXX Having a cache on a remote update seems like a good idea to avoid writing some
    #     changes.
    # XXX If the transaction is cancelled in Odoo, the changes are sent anyway.
    @ormcache("record_id", "new_template_data")
    def _set_cached_template(self, record_id, new_template_data):
        """
        Sets and caches the template in Redner for a given record.
        """
        record = self.browse(record_id)
        if not record.redner_id:
            # TODO Incorrect exception
            raise ValueError("The record must have a valid Redner ID.")

        try:
            produces, language = record.language.split("|")
            body, body_format = (
                (new_template_data.decode(), "base64")
                if language == "od+mustache"
                else (record.body, "text")
            )

            # Send the updated template to the external system
            self.redner.templates.account_template_update(
                template_id=record.redner_id,
                language=language,
                body=body,
                name=record.name,
                description=record.description,
                produces=produces,
                body_format=body_format,
                version=fields.Datetime.to_string(record.write_date),
                locale=record.locale_id.code,
            )

            # XXX why is the cache cleared?
            self.env.registry.clear_cache()

            return True
        except Exception as e:
            logger.error("Failed to set Redner template: %s", e)
            # TODO Incorrect exception
            raise ValueError("Unable to update the Redner template.") from e

    @api.model
    def get_keywords(self):
        """Return template redner keywords"""
        self.ensure_one()

        varlist = self.template_varlist_fetch()

        for name in varlist:
            while "." in name:
                name = name[: name.rfind(".")]
                if name not in varlist:
                    varlist.append(name)

        varlist.sort()

        return varlist

    @api.model
    @ormcache("self.redner_id")
    def template_varlist_fetch(self):
        """Retrieve the list of variables present in the template."""
        self.ensure_one()
        try:
            if not self.redner_id:
                return []

            return self.redner.templates.account_template_varlist(self.redner_id)

        except Exception as e:
            logger.warning("Failed to fetch account template varlist: %s", e)
            return []

    def view_in_redner(self):
        if self.redner_id:
            url = self.redner.get_template_url(self.redner_id)
            if url is not None:
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "new",
                }
        return None
