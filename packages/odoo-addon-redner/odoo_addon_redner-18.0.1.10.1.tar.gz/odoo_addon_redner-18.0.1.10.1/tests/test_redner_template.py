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
from unittest.mock import ANY

from .common import TestCommon

TEMPLATE_URL = "https://test-redner-url/api/v1/template/test-account"


class Test(TestCommon):
    """Test redner template management & their HTTP calls."""

    @mock.patch("requests.sessions.Session.post")
    @mock.patch("requests.sessions.Session.put")
    @mock.patch("requests.sessions.Session.get")
    def test_http_calls(
        self,
        requests_get_mock,
        requests_put_mock,
        requests_post_mock,
    ):
        """Test HTTP calls while managing redner templates from Odoo."""

        # base template
        base_name = "test-name"
        base_template = {
            "name": base_name,
            "description": "description",
            "language": "mustache",
            "body": "test-body",
            "produces": "text/html",
            "body-format": "text",
            "locale": "en_US",
        }

        # updated template, with the name changed
        updated_name = "test-name-2"
        updated_template = {
            "name": updated_name,
            "description": "description",
            "language": "mustache",
            "body": "test-body",
            "produces": "text/html",
            "body-format": "text",
            "locale": "en_US",
        }

        locale_id = self.env["res.lang"].search([("code", "=", "en_US")], limit=1).id

        # POST mock
        success_post_mock = mock.Mock(status_code=201, json=lambda: base_template)
        requests_post_mock.return_value = success_post_mock
        # PUT mock
        success_put_mock = mock.Mock(status_code=200, json=lambda: updated_template)
        requests_put_mock.return_value = success_put_mock
        # GET mock
        success_get_mock = mock.Mock(status_code=200, json=lambda: base_template)
        requests_get_mock.return_value = success_get_mock

        # Create a template. Default "language" value needed, see ::create.
        values = self.env["redner.template"].default_get(["language"])
        values.update(
            {
                "name": base_name,
                "description": "description",
                "body": "test-body",
                "allow_modification_from_odoo": True,
                "locale_id": locale_id,
            }
        )
        redner_template = self.env["redner.template"].create(values)
        base_template["version"] = ANY
        updated_template["version"] = base_template["version"]
        requests_put_mock.assert_not_called()
        self.assertEqual(redner_template.redner_id, base_name)
        requests_post_mock.assert_called_once_with(
            TEMPLATE_URL,
            json=base_template,
            headers={"Rednerd-API-Key": "test-api-key"},
            timeout=20,
        )

        # trigger a get
        _ = redner_template.language  # Trigger lazy load
        requests_get_mock.assert_called_with(
            TEMPLATE_URL + "/" + base_name,
            json={},
            headers={"Rednerd-API-Key": "test-api-key"},
            timeout=20,
        )
        requests_post_mock.reset_mock()
        requests_get_mock.reset_mock()

        # Update template.
        redner_template.name = updated_name
        requests_post_mock.assert_not_called()
        requests_put_mock.assert_not_called()
        requests_put_mock.reset_mock()
