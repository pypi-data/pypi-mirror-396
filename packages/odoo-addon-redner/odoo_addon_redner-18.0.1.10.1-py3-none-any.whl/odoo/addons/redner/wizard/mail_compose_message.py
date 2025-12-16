from odoo import fields, models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    is_redner_template = fields.Boolean(related="template_id.is_redner_template")

    def _set_value_from_template(self, template_fname, composer_fname=False):
        """Override: Set composer value from its template counterpart, considering
        redner integration."""
        self.ensure_one()
        composer_fname = composer_fname or template_fname

        res = super()._set_value_from_template(
            template_fname, composer_fname=composer_fname
        )

        if self.is_redner_template and template_fname == "body_html":
            if self.composition_mode == "comment" and not self.composition_batch:
                res_ids = self._evaluate_res_ids()
                rendering_res_ids = res_ids or [0]  # Fallback to dummy ID

                template_rendered = self.template_id._patch_email_values(
                    {composer_fname: {}}, rendering_res_ids[0]
                )[composer_fname]

                self[composer_fname] = template_rendered
                return self[composer_fname]

        return res
