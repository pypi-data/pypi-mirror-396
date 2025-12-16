##############################################################################
#
#    Redner Odoo module
#    Copyright © 2016, 2025 XCG SAS <https://orbeet.io/>
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

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from ..converter import image

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    """Extended to add features of redner API"""

    _inherit = ["mail.template", "substitution.mixin"]
    _name = "mail.template"

    is_redner_template = fields.Boolean(string="Rendered by Redner", default=False)

    redner_tmpl_id = fields.Many2one(
        comodel_name="redner.template",
        string="Redner Template",
        domain=[("active", "=", True)],
    )

    redner_substitution_ids = fields.One2many(
        comodel_name="redner.substitution",
        inverse_name="template_id",
        string="Substitutions",
    )

    def _patch_email_values(self, values, res_id):
        conv = self.redner_substitution_ids.filtered(
            lambda r: r.depth == 0
        ).build_converter()

        instance = self.env[self.model].browse(res_id)

        values_sent_to_redner = conv.odoo_to_message({}, instance)

        try:
            res = self.redner_tmpl_id.redner.templates.render(
                self.redner_tmpl_id.redner_id, values_sent_to_redner
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
        values["body_html"] = (
            base64.b64decode(res[0]["body"]).decode("utf-8") if res else ""
        )
        values["body"] = values["body_html"]

        return values

    def _generate_template(self, res_ids, render_fields, find_or_create_partners=False):
        self.ensure_one()

        results = super()._generate_template(
            res_ids, render_fields, find_or_create_partners=find_or_create_partners
        )
        if not self.is_redner_template:
            return results

        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        if multi_mode:
            return {
                res_id: self._patch_email_values(values, res_id)
                for res_id, values in results.items()
            }
        return self._patch_email_values(results, res_ids[0])

    def render_variable_hook(self, variables):
        """Override to add additional variables in mail "render template" func"""
        variables.update({"image": lambda value: image(value)})
        return super().render_variable_hook(variables)

    # -------------------------------------------------------------------------
    # MIXIN METHODS
    # -------------------------------------------------------------------------

    def _get_substitution_field(self):
        """Return the substitution field name for mail.template."""
        return "redner_substitution_ids"

    def _get_template(self):
        """Get template for mail.template."""
        return self.redner_tmpl_id

    def _get_substitutions(self):
        """Get substitutions for mail.template."""
        return self.redner_substitution_ids
