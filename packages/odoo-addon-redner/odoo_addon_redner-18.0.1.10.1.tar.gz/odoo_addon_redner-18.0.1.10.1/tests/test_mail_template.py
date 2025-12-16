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

import base64
from unittest import mock

from .common import TestCommon


class Test(TestCommon):
    """Test redner integration into email generation."""

    def setUp(self):
        """Override set-up to prepare an email template used in tests."""
        super().setUp()
        self.email_template = self.env["mail.template"].create(
            {
                "is_redner_template": True,
                "model_id": self.env.ref("base.model_res_users").id,
                "name": "test",
                "redner_tmpl_id": self._create_redner_template().id,
            }
        )

    @mock.patch("requests.sessions.Session.post")
    def test_email_generation(self, requests_post_mock):
        """Fill substitutions & generate an email."""

        # Fill the substitution table. We have 1 param: {{ login }}.
        requests_post_mock.return_value = mock.Mock(
            status_code=200, json=lambda: ["login"]
        )
        self.assertFalse(self.email_template.redner_substitution_ids)
        self.email_template.action_get_substitutions()
        requests_post_mock.assert_called_once_with(
            "https://test-redner-url/api/v1/varlist",
            json={"account": "test-account", "name": "test-redner-id"},
            headers={"Rednerd-API-Key": "test-api-key"},
            timeout=20,
        )
        requests_post_mock.reset_mock()
        substitution = self.email_template.redner_substitution_ids
        self.assertEqual(len(substitution), 1)
        self.assertEqual(substitution.keyword, "login")
        substitution.converter = "field"
        substitution.value = "login"

        # Generate an email with our test template for the demo user.
        requests_post_mock.return_value = mock.Mock(
            status_code=200,
            json=lambda: [{"body": base64.b64encode(b"test-rendered-email")}],
        )
        demo_user = self.env.ref("base.user_demo")
        email_id = self.email_template.send_mail(demo_user.id)
        requests_post_mock.assert_called_once_with(
            "https://test-redner-url/api/v1/render",
            json={
                "accept": "text/html",
                "data": [{"login": "demo"}],
                "template": {
                    "account": "test-account",
                    "name": "test-redner-id",
                },
                "body-format": "base64",
                "metadata": {},
            },
            headers={"Rednerd-API-Key": "test-api-key"},
            timeout=20,
        )
        email = self.env["mail.mail"].browse(email_id)
        self.assertEqual(email.body_html, "test-rendered-email")
        self.assertEqual(email.model, demo_user._name)
        self.assertEqual(email.res_id, demo_user.id)
