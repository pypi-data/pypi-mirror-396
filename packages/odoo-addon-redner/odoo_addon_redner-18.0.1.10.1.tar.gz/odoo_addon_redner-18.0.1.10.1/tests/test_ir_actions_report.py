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
    """Test redner integration into report generation."""

    def setUp(self):
        """Override set-up to prepare a report used in tests."""
        super().setUp()
        self.report = self.env["ir.actions.report"].create(
            {
                "attachment": 'object.login + ".html"',  # auto-save
                "model": "res.users",
                "name": "test-report",
                "redner_filetype": "html",
                "redner_tmpl_id": self._create_redner_template().id,
                "report_name": "test-report",
                "report_type": "redner",
            }
        )

    @mock.patch("requests.sessions.Session.post")
    def test_report_rendering(self, requests_post_mock):
        """Fill substitutions & render a redner report."""

        # Fill the substitution table. We have 1 param: {{ login }}.
        requests_post_mock.return_value = mock.Mock(
            status_code=200, json=lambda: ["login"]
        )
        self.assertFalse(self.report.substitution_ids)
        self.report.action_get_substitutions()
        requests_post_mock.assert_called_once_with(
            "https://test-redner-url/api/v1/varlist",
            json={"account": "test-account", "name": "test-redner-id"},
            headers={"Rednerd-API-Key": "test-api-key"},
            timeout=20,
        )
        requests_post_mock.reset_mock()
        substitution = self.report.substitution_ids
        self.assertEqual(len(substitution), 1)
        self.assertEqual(substitution.keyword, "login")
        substitution.converter = "field"
        substitution.value = "login"

        # Render our test report for the demo user.
        requests_post_mock.return_value = mock.Mock(
            status_code=200,
            json=lambda: [{"body": base64.b64encode(b"test-rendered-report")}],
        )
        demo_user = self.env.ref("base.user_demo")
        render_ret = self.report._render(self.report, [demo_user.id])
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
        self.assertEqual(len(render_ret), 2)
        self.assertEqual(render_ret[0], b"test-rendered-report")
        self.assertEqual(render_ret[1], "html")

        # Check attachment linked to the record (auto-save feature).
        attachment = self.env["ir.attachment"].search(
            [
                ("name", "=", "demo.html"),
                ("res_id", "=", demo_user.id),
                ("res_model", "=", demo_user._name),
            ]
        )
        self.assertEqual(len(attachment), 1)
        self.assertEqual(base64.b64decode(attachment.datas), b"test-rendered-report")
