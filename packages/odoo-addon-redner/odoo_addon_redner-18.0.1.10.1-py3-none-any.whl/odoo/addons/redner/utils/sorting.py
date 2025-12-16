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

import re


def parse_sorted_field(expression):
    """
    Extracts the field name and sort order from the expression `field.sorted("value")`.

    Returns (field_name, sort_order) if matched, otherwise (expression, None).
    """
    match = re.match(r'(\w+)\.sorted\("([^"]+)"\)', expression)
    return match.groups() if match else (expression, None)


def parse_fields_with_sort_directions(input_string: str):
    """
    Parses an input string to extract field names and their sort directions,
    returning a list of tuples where each tuple contains a field name and a boolean
    indicating the sort direction (True for descending, False for ascending).

    Fields without a specified sort direction are assumed to be sorted in ascending
    order.

    Example:
        >>> parse_fields_with_sort_directions("name asc,product_uom_qty desc")
        [('name', False), ('product_uom_qty', True)]
    """
    # Simplified regex pattern to capture field names and their sort orders
    pattern = r"(\w+)(\s+(asc|desc))?"

    # Extract all matches in the input string
    matches = re.findall(pattern, input_string)

    # Convert matches into the desired list of tuples, setting sort direction
    # based on the captured value.
    fields = [(field, order == "desc") for field, _, order in matches]

    return fields


class ModelSortKey:
    """
    A utility class to compare records based on specified fields and directions
    (ascending/descending).

    Attributes:
        fields (list of tuples): Each tuple contains a field name and a boolean
            indicating whether the sorting should be in descending order (True)
            or ascending order (False).
        values (tuple): Contains the actual values extracted from the records to
            be compared.

    Methods:
        __lt__(self, other): Less than comparison between two instances.
        __le__(self, other): Less than or equal to comparison between two instances.
        __gt__(self, other): Greater than comparison between two instances.
        __ge__(self, other): Greater than or equal to comparison between two instances.
    """

    def __init__(self, fields, values):
        self.fields = fields
        self.values = tuple(values)

    def __lt__(self, other):
        for (_, r), v, ov in zip(self.fields, self.values, other.values, strict=True):
            if v == ov:
                continue
            return (v < ov) != r  # Also: v > ov if r else v < ov.
        return False

    def __le__(self, other):
        for (_, r), v, ov in zip(self.fields, self.values, other.values, strict=True):
            if v == ov:
                continue
            return (v < ov) != r
        return True

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


def sortkey(order: str):
    """
    Generates a key function for sorting records based on the specified order string.

    Args:
        order (str): A comma-separated string specifying the fields to sort by and the
            direction (e.g., "name asc, lastname desc").

    Returns:
        A callable key function that can be passed to sorted() or similar functions to
        sort records according to the specified order.

    Example:
        >>> sortkey("name asc, lastname desc")
        <function sortkey.<locals>.key at 0x7f8b6c5d8a80>
    """
    fields = parse_fields_with_sort_directions(order)

    def key(record):
        """
        Constructs a ModelSortKey instance using the specified fields and the
        corresponding values from the record.

        Args:
            record (dict): A dictionary representing a single record.

        Returns:
            An instance of ModelSortKey ready to be used for comparisons during
            sorting.
        """
        return ModelSortKey(fields, [record[fieldname] for fieldname, _ in fields])

    return key
