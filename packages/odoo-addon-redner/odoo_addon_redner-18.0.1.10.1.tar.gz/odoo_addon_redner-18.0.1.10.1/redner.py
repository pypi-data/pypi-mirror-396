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

import logging
import time
from typing import Final
from urllib.parse import quote

from odoo import _
from odoo.exceptions import UserError
from requests import JSONDecodeError, Response, Session, codes

_logger = logging.getLogger(__name__)


class MissingRednerServerConfiguration(UserError):
    """Exception when redner configuration is missing"""


class RednerServerException(Exception):
    """Exception raised when there is a server exception"""


class Redner:
    __REDNER_API_PATH: Final[str] = "api/v1/"
    __MAX_REDNERD_TRIES: Final[int] = 3

    def __init__(self, api_key: str, server_url: str, account: str, timeout: float):
        """Initialize the API client

        Args:
           api_key(str): provide your Redner API key.
           server_url(str): Redner server URL or socket path.
               For example: http://localhost:30001/
           timeout(float): Timeout per Redner call, in seconds.
        """

        self.api_key = api_key
        self.account = account
        self.timeout = timeout
        self.is_socket = True
        self.session: Session
        self.server_url: str
        self.server_url_api: str

        if server_url.startswith("/"):
            # import here as this is an optional requirement
            import requests_unixsocket

            self.session = requests_unixsocket.Session()
            self.server_url = "http+unix://{}/".format(quote(server_url, safe=""))
        else:
            self.is_socket = False
            self.session = Session()
            self.server_url = server_url
        if not self.server_url.endswith("/"):
            self.server_url += "/"
        self.server_url_api = self.server_url + self.__REDNER_API_PATH

        self.templates = Templates(self)

    def call(self, path, http_verb="post", json=True, **params):
        """Call redner with the specified parameters.
        Delegate to ``call_impl``; this is a wrapper to have some retries
        before giving up as redner sometimes mistakenly rejects our queries.
        """

        for retry_counter in range(self.__MAX_REDNERD_TRIES):
            try:
                if json:
                    return self.call_impl_json(path, http_verb=http_verb, **params)
                return self.call_impl(path, http_verb=http_verb, **params)
            except Exception as error:
                if retry_counter == self.__MAX_REDNERD_TRIES - 1:
                    _logger.error("Redner error: %s", str(error))
                    raise error

    def call_impl_json(self, path, http_verb="post", **params):
        """Actually make the API call with the given params -
        this should only be called by the namespace methods
        This tries to unmarshal the response

        Args:
            path(str): URL path to query, e.g. '/template/'
            http_verb(str): http verb to use, default: 'post'
            params(dict): JSON payload

        Raises RednerServerException when the server returns a status code not starting
        with 2.
        """
        r = self.call_impl(path, http_verb, **params)
        _logger.debug("Redner: Received %s", r.text)

        try:
            response = r.json()
        except JSONDecodeError:
            # If we cannot decode JSON then it's an API error
            # having response as text could help debugging with sentry
            response = r.text

        if not str(r.status_code).startswith("2"):
            _logger.error("Bad response from Redner: %s", response)
            # Try to unpack the message for a more user-friendly experience
            if (
                all(hasattr(response, attr) for attr in ("keys", "__getitem__"))
                and "message" in response
            ):
                message = response["message"]
            else:
                message = response
            raise RednerServerException(_("Unexpected redner error: %r", message))

        return response

    def call_impl(self, path, http_verb="post", **params) -> Response:
        """Actually make the API call with the given params -
        this should only be called by the namespace methods

        Args:
            path(str): URL path to query, e.g. '/template/'
            http_verb(str): http verb to use, default: 'post'
            params(dict): JSON payload

        This method can raise anything; callers are expected to catch.
        Raise a MissingRednerServerConfiguration if there is no redner URL.
        """

        if not self.server_url_api:
            raise MissingRednerServerConfiguration(
                _(
                    "Cannot find redner config URL. "
                    "Please add it in ir.config_parameter"
                )
            )

        url = self.server_url_api + path

        _http_verb = http_verb.upper()
        _logger.info("Redner: Calling %s...", _http_verb)
        _logger.debug("Redner: Sending to %s > %s", url, params)
        start = time.time()

        r: Response = getattr(self.session, http_verb, self.session.post)(
            url,
            json=params,
            headers={"Rednerd-API-Key": self.api_key},
            timeout=self.timeout,
        )

        complete_time = time.time() - start
        _logger.info(
            "Redner: Received %s in %.2fms.",
            r.status_code,
            complete_time * 1000,
        )
        return r

    def ping(self):
        """Try to establish a connection to server"""
        # Ensure timeout is set to prevent indefinite hangs
        timeout = self.timeout if self.timeout is not None else 30
        conn = self.session.get(self.server_url_api, timeout=timeout)
        if conn.status_code != codes.ok:
            raise RednerServerException(
                _("Cannot Establish a connection to Redner server")
            )
        return conn

    def __repr__(self) -> str:
        return f"<Redner ({self.server_url},{self.account},{self.timeout}>"

    def get_template_url(self, redner_id: str) -> str | None:
        """Return the URL to access a template in Redner server."""
        if self.is_socket:
            return None
        return self.server_url + "template/" + self.account + "/" + redner_id


class Templates:
    def __init__(self, master):
        self.master = master

    def render(
        self,
        template_id,
        data,
        accept="text/html",
        body_format="base64",
        metadata=None,
    ):
        """Inject content and optionally merge fields into a template,
        returning the HTML that results.

        Args:
            template_id(str): Redner template ID.
            data(dict): Template variables.
            accept: format of a request or response body data.
            body_format (string): The body attribute format.
                Can be 'text' or 'base64'. Default 'base64',
            metadata (dict):

        Returns:
            Array of dictionaries: API response
        """

        if isinstance(data, dict):
            data = [data]

        params = {
            "accept": accept,
            "data": data,
            "template": {"account": self.master.account, "name": template_id},
            "body-format": body_format,
            "metadata": metadata or {},
        }
        return self.master.call("render", http_verb="post", **params)

    def account_template_list(self):
        """List templates from Redner made on the redner account

        Returns:
            list(templates): Redner template List.
        """
        return self.master.call(
            f"template/{self.master.account}",
            http_verb="get",
        )

    def account_template_read(self, redner_id):
        """Fetch a template from redner given it's id

        Args:
            redner_id(string): The redner template identifier.
        Returns:
            template: Redner template.
        """
        return self.master.call(
            f"template/{self.master.account}/{redner_id}",
            http_verb="get",
        )

    def account_template_preview(self, redner_id) -> Response:
        """Fetch a template preview from redner given it's id

        Args:
            redner_id(string): The redner template identifier.
        Returns:
            preview: Redner template preview in png.
        """
        return self.master.call(
            f"template/{self.master.account}/{redner_id}/preview.png",
            http_verb="get",
            json=False,
        )

    def account_template_add(
        self,
        language,
        body,
        name,
        description="",
        produces="text/html",
        body_format="text",
        locale="fr_FR",
        version="N/A",
    ):
        """Store template in Redner

        Args:
            name(string): Name of your template. This is to help the user find
                its templates in a list.
            description(string): Description of your template.
            language(string): Language your template is written with.
                Can be mustache, handlebar or od+mustache.
            body(string): Content you want to create.

            produces(string): Can be text/html or

            body_format (string): The body attribute format. Can be 'text' or
                'base64'. Default 'base64'

            locale(string):

            version(string):

        Returns:
            template: Redner template.
        """

        params = {
            "name": name,
            "description": description,
            "language": language,
            "body": body,
            "produces": produces,
            "body-format": body_format,
            "locale": locale,
            "version": version,
        }
        res = self.master.call(
            f"template/{self.master.account}",
            http_verb="post",
            **params,
        )
        return res

    def account_template_update(
        self,
        template_id,
        language,
        body,
        name="",
        description="",
        produces="text/html",
        body_format="text",
        locale="fr_FR",
        version="N/A",
    ):
        """Store template in Redner

        Args:
            template_id(string): Name of your template.
            This is to help the user find its templates in a list.
            name(string): The new template name (optional)
            description(string): Description of your template.
            language(string): Language your template is written with.
                Can be mustache, handlebar or od+mustache

            body(string): Content you want to create.

            produces(string): Can be text/html or

            body_format (string): The body attribute format. Can be 'text' or
                'base64'. Default 'base64'

            locale(string):

            version(string):

        Returns:
            template: Redner template.
        """
        params = {
            "name": name,
            "description": description,
            "language": language,
            "body": body,
            "produces": produces,
            "body-format": body_format,
            "locale": locale,
            "version": version,
        }
        res = self.master.call(
            f"template/{self.master.account}/{template_id}",
            http_verb="put",
            **params,
        )
        return res

    def account_template_delete(self, name: str):
        """Delete a given template name

        Args:
            name(string): Redner template Name.

        Returns:
            dict: API response.
        """
        return self.master.call(
            f"template/{self.master.account}/{name}", http_verb="delete"
        )

    def account_template_varlist(self, name: str):
        """Extract the list of variables present in the template.
        The list is not guaranteed to be accurate depending on the
        template language.

        Args:
            name(string): Redner template name.

        Returns:
            dict: API response.
        """

        params = {"account": self.master.account, "name": name}

        return self.master.call("varlist", **params)
