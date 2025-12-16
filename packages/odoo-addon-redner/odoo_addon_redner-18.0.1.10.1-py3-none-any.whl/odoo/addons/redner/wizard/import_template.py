from odoo import fields, models


# Using written records is necessary for the import action to work.
class TemplateListWizard(models.TransientModel):
    _name = "redner.import_template"
    _description = "Import Template"

    name = fields.Char(
        string="Name",
        required=True,
        help="Name of the redner template",
    )

    description = fields.Char(
        string="Description",
        help="Description of the template",
    )

    preview = fields.Binary(
        string="Preview",
        help="The PNG preview of the template",
    )

    def populate(self):
        """Make sure all available templates are present."""
        redner_template_model = self.env["redner.template"]

        redner_templates = (
            redner_template_model.redner.templates.account_template_list()
        )
        # Get the IDs of the templates that already exist in Odoo
        existing_templates_uid = (
            redner_template_model.with_context(active_test=False)
            .search([])
            .mapped("redner_id")
        )
        import_templates = {template.name: template for template in self.search([])}
        import_template_to_delete = self.env["redner.import_template"]
        redner_template_to_write = self.env["redner.import_template"]
        new_templates = []
        for redner_template in redner_templates:
            redner_template_name = redner_template["name"]
            if redner_template_name in existing_templates_uid:
                # Delete any redner.import_template already present with the name.
                if redner_template_name in import_templates:
                    import_template_to_delete |= import_templates[redner_template_name]
            else:
                if redner_template_name in import_templates:
                    redner_template_to_write |= import_templates[redner_template_name]
                else:
                    new_templates.append(
                        redner_template_model._to_odoo_template(redner_template)
                    )

        self.create(
            [
                {
                    "name": new_template["name"],
                    "description": new_template["description"],
                    "preview": redner_template_model.get_preview(new_template["name"]),
                }
                for new_template in new_templates
            ]
        )
        if redner_template_to_write:
            # Update write_create for later vacuum
            redner_template_to_write.write({})
        if import_template_to_delete:
            import_template_to_delete.unlink()

    def action_import_template(self):
        template = self.env["redner.template"].create(
            [
                {
                    # read template (otherwise no body, none provided when listing)
                    **self.env["redner.template"]._get_template(self.name),
                    "active": True,
                    "source": "redner",
                    "allow_modification_from_odoo": False,
                }
            ]
        )
        # Delete the wizard from available templates immediately
        self.sudo().unlink()
        return {
            "type": "ir.actions.act_window",
            "res_model": "redner.template",
            "view_mode": "form",
            "res_id": template.id,
            "target": "current",
        }
