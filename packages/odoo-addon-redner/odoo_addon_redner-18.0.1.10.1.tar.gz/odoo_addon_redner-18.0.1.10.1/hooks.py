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
import logging

_logger = logging.getLogger(__name__)


def post_load():
    """Post load hook"""
    try:
        from odoo.addons.account.models.account_move_send import AccountMoveSend

        old_default_mail_body = AccountMoveSend._get_default_mail_body

        def _get_default_mail_body(self, move, mail_template, mail_lang):
            if (
                not hasattr(mail_template, "is_redner_template")
                or not mail_template.is_redner_template
            ):
                return old_default_mail_body(self, move, mail_template, mail_lang)

            return mail_template._patch_email_values({}, move.id)["body_html"]

        AccountMoveSend._get_default_mail_body = _get_default_mail_body
    except ImportError:
        _logger.warning(
            "AccountMoveSend should be in "
            "odoo.addons.account.models.account_move_send but wasn't"
        )
