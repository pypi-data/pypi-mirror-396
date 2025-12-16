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

from odoo import _, api, fields, models
from odoo.addons import converter
from odoo.exceptions import ValidationError

from ..converter import ImageDataURL, ImageFile
from ..utils.sorting import parse_sorted_field, sortkey

FIELD = "field"
CONSTANT = "constant"
MAIL_TEMPLATE = "mail_template"
MAIL_TEMPLATE_DESERIALIZE = "mail_template+deserialize"
IMAGE_FILE = "image-file"
IMAGE_DATAURL = "image-data-url"
RELATION_2MANY = "relation-to-many"
RELATION_PATH = "relation-path"

CONVERTER_SELECTION = [
    (MAIL_TEMPLATE, "Odoo Template"),
    (MAIL_TEMPLATE_DESERIALIZE, "Odoo Template + Eval"),
    (FIELD, "Field"),
    (IMAGE_FILE, "Image file"),
    (IMAGE_DATAURL, "Image data url"),
    (RELATION_2MANY, "Relation to many"),
    (RELATION_PATH, "Relation Path"),
    (CONSTANT, "Constant value"),
]

DYNAMIC_PLACEHOLDER_ALLOWED_CONVERTERS = (
    FIELD,
    MAIL_TEMPLATE,
    MAIL_TEMPLATE_DESERIALIZE,
)


class Substitution(models.Model):
    """Substitution values for a Redner email message"""

    _name = "redner.substitution"
    _inherit = ["mail.render.mixin"]
    _description = "Redner Substitution"

    keyword = fields.Char(string="Variable", help="Template variable name")

    template_id = fields.Many2one(comodel_name="mail.template", string="Email Template")

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report", string="Report"
    )

    model = fields.Char(
        "Related Report Model",
        related="ir_actions_report_id.model",
        index=True,
        store=True,
        readonly=True,
    )

    value = fields.Char(string="Expression")

    converter = fields.Selection(selection=CONVERTER_SELECTION)

    depth = fields.Integer(string="Depth", compute="_compute_depth", store=True)

    value_placeholder = fields.Char(compute="_compute_value_placeholder")

    hide_placeholder_button = fields.Boolean(
        compute="_compute_hide_placeholder_button", string="Hide Placeholder Button"
    )

    value_type = fields.Selection(
        selection=[
            ("", "Not specified"),
            ("simple", "Simple"),
        ],
        string="Value Type",
        default="",
        required=False,
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Substitution order, children are placed under their parent.",
    )

    @api.onchange("converter")
    def _onchange_converter(self):
        if self.converter:
            self.value = False

    @api.depends("converter")
    def _compute_value_placeholder(self):
        """Compute placeholder text based on conversion type"""
        placeholder_map = {
            FIELD: _("e.g: name or partner_id.name"),
            MAIL_TEMPLATE: _("e.g: {{object.partner_id.name}}"),
            MAIL_TEMPLATE_DESERIALIZE: _("e.g: {{ object.get_partner_info() | safe }}"),
            RELATION_PATH: _(
                "e.g: partner_id/category_id/name ou partner_id/child_ids[]"
            ),
            RELATION_2MANY: _("e.g: tax_ids"),
            CONSTANT: _("e.g: www.orbeet.io"),
        }
        for record in self:
            record.value_placeholder = placeholder_map.get(record.converter, _("N/A"))

    @api.depends("value")
    def _compute_render_model(self):
        for substitution in self:
            if substitution.ir_actions_report_id:
                substitution.render_model = substitution.model
            elif substitution.template_id:
                substitution.render_model = substitution.template_id.model_id.model
            else:
                substitution.render_model = False

    @api.depends("keyword")
    def _compute_depth(self):
        for record in self:
            record.depth = record.keyword.count(".")

    @api.depends("converter")
    def _compute_hide_placeholder_button(self):
        for record in self:
            record.hide_placeholder_button = (
                record.converter not in DYNAMIC_PLACEHOLDER_ALLOWED_CONVERTERS
            )

    def get_children(self):
        return self.search(
            [
                ("ir_actions_report_id", "=", self.ir_actions_report_id.id),
                ("keyword", "=like", self.keyword + ".%"),
                ("depth", "=", self.depth + 1),
            ]
        )

    def build_converter(self):
        """Build a converter dictionary from substitution records."""
        converters = {}
        for sub in self:
            if sub.converter:
                try:
                    key = sub.keyword.rsplit(".", 2)[-1]
                    conv = self._create_converter_by_type(sub)
                    converters[key] = conv
                except KeyError:
                    raise ValidationError(
                        _("invalid converter type: %s", sub.converter)
                    ) from None
        return converter.Model(converters)

    def _create_converter_by_type(self, sub):
        """Create appropriate converter based on type."""
        converter_map = {
            "mail_template": lambda: converter.MailTemplate(sub.value, False),
            "mail_template+deserialize": lambda: converter.MailTemplate(
                sub.value, True
            ),
            "constant": lambda: converter.Constant(sub.value),
            "field": lambda: self._create_field_or_image_converter(sub, is_image=False),
            "image-file": lambda: self._create_field_or_image_converter(
                sub, is_image=True
            ),
            "image-data-url": lambda: ImageDataURL(sub.value),
            "relation-to-many": lambda: self._create_relation_to_many_converter(sub),
            "relation-path": lambda: converter.relation(
                sub.value, sub.get_children().build_converter()
            ),
        }
        return converter_map[sub.converter]()

    def _create_field_or_image_converter(self, sub, is_image):
        """Create a converter for 'field' or 'image-file' types."""
        path, name = sub.value.rsplit(".", 1) if "." in sub.value else (None, sub.value)
        conv = ImageFile(name) if is_image else converter.Field(name)
        return converter.relation(path.replace(".", "/"), conv) if path else conv

    def _create_relation_to_many_converter(self, sub):
        """Create a converter for 'relation-to-many' type."""
        # Unpack the result of finding a field with its sort order into
        # variable names.
        value, sorted_field = parse_sorted_field(sub.value)
        # Use readonly=True since redner only needs Odoo→message conversion
        # for report generation (converter v7+ requires instance getter for
        # writable relations)
        return converter.RelationToMany(
            value,
            None,
            sortkey=sortkey(sorted_field) if sorted_field else None,
            converter=sub.get_children().build_converter(),
            readonly=True,
        )

    def create_converter_from_record(self):
        """
        Create a converter instance from a single substitution record.

        Returns:
            converter.BaseConverter: A converter instance based on the record's type,
                                    or None if no matching converter type found.

        Example:
            >>> sub = SubstitutionRecord(keyword="field.name", converter="field",
              value="partner.name")
            >>> conv = sub.create_converter_from_record()
            >>> isinstance(conv, converter.Field)
            True
            >>> conv.field_name
            'name'
        """
        converter_factories = {
            "field": lambda: converter.Field(self.value.split(".")[-1]),
            "constant": lambda: converter.Constant(self.value),
            # Extend with additional converter types as needed
        }

        return converter_factories.get(self.converter, lambda: None)()
