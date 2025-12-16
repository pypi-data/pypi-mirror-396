##############################################################################
#
#    Redner Odoo module
#    Copyright © 2023 XCG SAS <https://orbeet.io/>
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

from unittest import mock

from odoo.tests import TransactionCase


class TestCommon(TransactionCase):
    """Common set-up elements between redner tests."""

    def setUp(self):
        """Override set-up to define redner connection settings."""
        super().setUp()
        set_param = self.env["ir.config_parameter"].set_param
        set_param("redner.account", "test-account")
        set_param("redner.api_key", "test-api-key")
        set_param("redner.server_url", "https://test-redner-url")

    @mock.patch("requests.sessions.Session.post")
    def _create_redner_template(self, requests_post_mock):
        """Create a redner template used in tests."""
        requests_post_mock.return_value = mock.Mock(
            status_code=200, json=lambda: {"name": "test-redner-id"}
        )
        values = self.env["redner.template"].default_get(["language"])
        values.update({"name": "test-name", "body": "hello {{ login }}"})
        return self.env["redner.template"].create(values)
