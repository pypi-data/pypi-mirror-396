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
import logging
import mimetypes

from odoo.tools.mimetypes import guess_mimetype

try:
    from magic import MagicException
except ImportError:

    class MagicException(Exception):  # type: ignore[no-redef]
        """Redefine the exception for compatibility if it does not exist"""


_logger = logging.getLogger(__name__)


# XXX not used in the module except in a test
def b64_to_extension(b64_string: bytes) -> None | str:
    # Can raise magic.MagicException if python-magic is installed
    try:
        # Decode the Base64 string into binary data
        binary_data = base64.b64decode(b64_string)
        # Use python-magic to determine the MIME type
        mime_type = guess_mimetype(binary_data)
        # Get the file extension from the MIME type
        return mimetypes.guess_extension(mime_type)
    except MagicException:
        _logger.warning("Error detecting file type", exc_info=True)
        return None


def get_file_extension(binary_data: bytes) -> str:
    """Determine the file extension from binary content.

    :param binary_data: Binary content of the file
    :return: File extension string (default: .odt)
    """
    file_type = guess_mimetype(binary_data)

    # Mapping MIME types to extensions
    mime_to_ext = {
        "application/vnd.oasis.opendocument.text": ".odt",
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",  # noqa: E501
    }
    if file_type in mime_to_ext:
        return mime_to_ext[file_type]
    extension = mimetypes.guess_extension(file_type)
    if extension is not None:
        return extension
    # Returning .odt seems a bad idea, so changed to no extension instead
    return ""
