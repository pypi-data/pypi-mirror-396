from odoo import Command, models


class SubstitutionMixin(models.AbstractModel):
    _name = "substitution.mixin"
    _description = "Substitution Mixin"

    def action_get_substitutions(self):
        """
        Shift child substitutions up one level if their parent has a value_type.
        Example: order_line.test1.field1 becomes order_line.field1 if order_line.test1
        has a value_type. Handles multiple levels.
        Call by: action button `Get Substitutions from Render Report`
        """
        self.ensure_one()

        # Use a method to get the template, making it adaptable to different models
        template = self._get_template()
        if not template:
            return

        # Get template keywords
        keywords = template.get_keywords()
        if not keywords:
            return

        # Assign initial sequence based on keywords order
        sequence_map = {kw: (i + 1) * 10 for i, kw in enumerate(keywords)}

        # Step 1: Identify parents with defined value_type
        typed_parents = {
            sub.keyword for sub in self._get_substitutions() if sub.value_type
        }

        # Step 2: Build keyword remapping
        keyword_mapping = self._build_keyword_remapping(keywords, typed_parents)

        # Step 3: Prepare update commands
        commands = self._prepare_substitution_commands(
            keyword_mapping, keywords, sequence_map
        )

        # Apply changes if any
        if commands:
            self.write({self._get_substitution_field(): commands})

    def _get_substitution_field(self):
        """Abstract method to get the substitution field name; must be
        implemented by inheriting models.
        """
        raise NotImplementedError(
            "Method '_get_substitution_field' must be implemented."
        )

    def _get_template(self):
        """Abstract method to get the template; must be implemented by
        inheriting models.
        """
        raise NotImplementedError("Method '_get_template' must be implemented.")

    def _get_substitutions(self):
        """Abstract method to get the substitutions; must be implemented by
        inheriting models.
        """
        raise NotImplementedError("Method '_get_substitutions' must be implemented.")

    def _build_keyword_remapping(self, keywords, typed_parents):
        """
        Build mapping between original keywords and their remounted versions.
        Handles recursive remounting when multiple levels have defined value_types.

        :param keywords: List of original keywords from template
        :param typed_parents: Set of parent keywords with defined value_type
        :return: Dictionary mapping original keywords to remounted keywords
        """
        keyword_mapping = {}
        processed = set()

        for keyword in keywords:
            if keyword in processed:
                continue

            # Get remounted keyword after applying all parent type rules
            remounted = self._get_remounted_keyword(keyword, typed_parents)

            # Only add to mapping if it changed
            if remounted != keyword:
                keyword_mapping[keyword] = remounted
                processed.add(keyword)

        return keyword_mapping

    def _get_remounted_keyword(self, keyword, typed_parents):
        """
        Get the remounted version of a keyword by recursively removing typed parents.

        :param keyword: Original keyword to remount
        :param typed_parents: Set of parent keywords with defined value_type
        :return: Remounted keyword with typed parents removed
        """
        parts = keyword.split(".")
        modified = True
        current = keyword

        # Keep remounting until no more changes
        while modified:
            modified = False
            parts = current.split(".")

            # Check each potential parent in the path
            for i in range(1, len(parts)):
                parent = ".".join(parts[:i])

                # If this parent has a type, remount by removing it
                if parent in typed_parents:
                    prefix = ".".join(parts[: i - 1]) if i > 1 else ""
                    suffix = ".".join(parts[i:])

                    new_keyword = f"{prefix}.{suffix}" if prefix else suffix

                    if new_keyword != current:
                        current = new_keyword
                        modified = True
                        break  # Start over with new keyword

        return current

    def _prepare_substitution_commands(self, keyword_mapping, keywords, sequence_map):
        """
        Prepare commands to update, create, and delete substitutions.

        :param keyword_mapping: Dictionary mapping original keywords to remounted
          versions
        :param keywords: List of original keywords from template
        :param sequence_map: Dictionary mapping keywords to their sequence numbers
        :return: List of commands for write method
        """
        commands = []
        processed_keywords = set()
        substitutions = self._get_substitutions()

        def _build_substitution_vals(sub=None, keyword=None, sequence=None):
            """Helper to build substitution values dictionary."""
            if sub:
                # Use values from an existing substitution record
                return {
                    "keyword": keyword or sub.keyword,
                    "value_type": sub.value_type,
                    "converter": sub.converter,
                    "value": sub.value,
                    "template_id": sub.template_id.id if sub.template_id else False,
                    "ir_actions_report_id": sub.ir_actions_report_id.id
                    if sub.ir_actions_report_id
                    else False,
                    "sequence": sub.sequence,
                }
            # Default empty values
            return {
                "keyword": keyword,
                "value_type": "",
                "converter": False,
                "value": False,
                "sequence": sequence_map.get(keyword, 10)
                if sequence is None
                else sequence,
            }

        # Process remounted keywords
        for orig_key, new_key in keyword_mapping.items():
            orig_sub = substitutions.filtered(lambda s, ok=orig_key: s.keyword == ok)
            new_sub = substitutions.filtered(lambda s, nk=new_key: s.keyword == nk)

            # Handle original substitution exists
            if orig_sub:
                # Update or create remounted version
                if new_sub:
                    commands.append(
                        Command.update(
                            new_sub.id,
                            _build_substitution_vals(orig_sub),
                        )
                    )
                else:
                    commands.append(
                        Command.create(_build_substitution_vals(orig_sub, new_key))
                    )

                # Delete original
                commands.append(Command.unlink(orig_sub.id))
            else:
                # Create new remounted if it doesn't exist
                if not new_sub:
                    commands.append(
                        Command.create(_build_substitution_vals(keyword=new_key))
                    )

            processed_keywords.add(new_key)

        # Create missing original keywords that weren't remounted
        for keyword in keywords:
            if keyword not in keyword_mapping and keyword not in processed_keywords:
                existing = substitutions.filtered(lambda s, kw=keyword: s.keyword == kw)
                if not existing:
                    commands.append(
                        Command.create(_build_substitution_vals(keyword=keyword))
                    )
                processed_keywords.add(keyword)

        # Delete obsolete substitutions
        obsolete = substitutions.filtered(lambda s: s.keyword not in processed_keywords)
        for sub in obsolete:
            commands.append(Command.unlink(sub.id))

        return commands
