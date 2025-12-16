##############################################################################
#
#    Redner Odoo module
#    Copyright © 2024 XCG SAS <https://orbeet.io/>
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

from ..utils.sorting import sortkey
from .common import TestCommon


class TestModelSortKey(TestCommon):
    def setUp(self):
        """Set up common objects used across multiple tests."""
        super().setUp()

        self.records = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]

    def test_single_field_asc(self):
        """Test sorting by a single field in ascending order."""
        key_func = sortkey("name asc")
        sorted_records = sorted(self.records, key=key_func)
        self.assertEqual(
            sorted_records,
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35},
            ],
        )

    def test_single_field_desc(self):
        """Test sorting by a single field in descending order."""
        key_func = sortkey("age desc")
        sorted_records = sorted(self.records, key=key_func)
        self.assertEqual(
            sorted_records,
            [
                {"name": "Charlie", "age": 35},
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
        )

    def test_multiple_fields(self):
        """Test sorting by multiple fields."""
        key_func = sortkey("name asc, age desc")
        sorted_records = sorted(self.records, key=key_func)
        self.assertEqual(
            sorted_records,
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35},
            ],
        )
