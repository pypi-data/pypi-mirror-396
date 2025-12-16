##############################################################################
#
#    Redner Odoo module
#    Copyright © 2016, 2025 XCG SAS <https://orbeet.io/>
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

import ipaddress
from urllib.parse import urlparse

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    redner_server_url = fields.Char(
        string="Redner Server URL",
        config_parameter="redner.server_url",
    )

    redner_account = fields.Char(
        string="Redner Account Name",
        config_parameter="redner.account",
    )

    redner_api_key = fields.Char(
        string="Redner API Key",
        config_parameter="redner.api_key",
    )

    @api.constrains("redner_server_url")
    def _check_redner_server_url(self):
        """Validate Redner server URL to prevent SSRF attacks on sensitive services"""
        for record in self:
            if not record.redner_server_url:
                continue

            url = record.redner_server_url

            # Unix sockets are safe (local filesystem access)
            if url.startswith("/"):
                continue

            try:
                parsed = urlparse(url)

                # Only allow HTTP/HTTPS protocols
                if parsed.scheme not in ("http", "https"):
                    raise ValidationError(
                        _(
                            "Redner server URL must use HTTP or HTTPS protocol."
                            "Got: %s",
                            parsed.scheme,
                        )
                    )

                hostname = parsed.hostname
                if not hostname:
                    raise ValidationError(
                        _("Redner server URL must include a valid hostname")
                    )

                # Block localhost/loopback (127.x.x.x, ::1) to prevent attacks
                # on local services like Redis, databases, etc.
                if hostname.lower() in ("localhost", "::1"):
                    raise ValidationError(
                        _(
                            "Redner server URL cannot use 'localhost'. "
                            "Use 127.0.0.1 or actual IP/domain if needed."
                        )
                    )

                # Check if hostname is an IP address for additional validation
                try:
                    ip = ipaddress.ip_address(hostname)

                    # Block 127.x.x.x range (loopback) - common attack target
                    if ip.is_loopback:
                        raise ValidationError(
                            _(
                                "Redner server URL cannot point to loopback addresses "
                                "(127.x.x.x, ::1). If Redner is on the same machine, "
                                "use a Unix socket path instead."
                            )
                        )

                    # Block link-local addresses (169.254.x.x, fe80::/10)
                    # These are auto-configured and shouldn't be used for services
                    if ip.is_link_local:
                        raise ValidationError(
                            _(
                                "Redner server URL cannot point to link-local "
                                "addresses (169.254.x.x). Use a proper static IP "
                                "or domain name."
                            )
                        )

                    # Warn about common cloud metadata endpoints
                    # (but don't block private IPs)
                    if str(ip).startswith("169.254.169.254"):
                        raise ValidationError(
                            _(
                                "Redner server URL cannot point to cloud metadata "
                                "service (169.254.169.254). This is a security risk."
                            )
                        )

                except ValueError:  # pylint: disable=except-pass
                    # hostname is a domain name, not an IP - this is generally safe
                    pass

            except ValueError as e:
                raise ValidationError(
                    _("Invalid Redner server URL format: %s", str(e))
                ) from e
