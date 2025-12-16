##############################################################################
#
#    Redner Odoo module
#    Copyright © 2025 XCG SAS <https://orbeet.io/>
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

from odoo import Command, api, fields, models


class ImportTemplate(models.TransientModel):
    """Wizard to import templates from the server."""

    _name = "redner.import_template.wizard"
    _description = "Wizard to import a template from the server"

    import_template_ids = fields.Many2many(
        "redner.import_template",
        "redner_import_template_redner_import_template_wizard_rel",
        "wizard_id",
        "template_id",
    )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)

        if "import_template_ids" in fields_list:
            self.env["redner.import_template"].sudo().populate()
            values["import_template_ids"] = [
                Command.link(t.id)
                for t in self.env["redner.import_template"].search([])
            ]
        return values
