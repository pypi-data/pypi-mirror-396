##############################################################################
#
#    Redner Odoo module
#    Copyright © 2024, 2025 XCG SAS <https://orbeet.io/>
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

from odoo.tests import TransactionCase

from ..utils.mimetype import b64_to_extension, get_file_extension


class TestMimetype(TransactionCase):
    def test_gif(self):
        data = b"R0lGODlhAQABAAAAACw="
        self.assertEqual(b64_to_extension(data), ".gif")
        self.assertEqual(get_file_extension(base64.decodebytes(data)), ".gif")

    def test_png(self):
        data = (
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAW"
            b"gmWQ0AAAAASUVORK5CYII="
        )
        self.assertEqual(b64_to_extension(data), ".png")
        self.assertEqual(get_file_extension(base64.decodebytes(data)), ".png")

    def test_svg(self):
        data = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>'
        self.assertEqual(b64_to_extension(base64.encodebytes(data)), ".svg")
        self.assertEqual(get_file_extension(data), ".svg")
