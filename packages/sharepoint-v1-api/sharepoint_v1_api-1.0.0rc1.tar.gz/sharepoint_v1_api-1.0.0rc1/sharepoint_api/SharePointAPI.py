import os
import json
from datetime import timezone
import requests
from requests_ntlm import HttpNtlmAuth
from typing import List, Optional, Tuple
import re
import warnings

from .SharePointUser import SharePointUser
from .SharePointUserList import SharePointUserList
from .SharePointListItem import SharePointListItem, SharepointSiteCase
from .SharePointList import SharePointList, CasesList, TimeRegistrationList
from .SharePointLists import SharePointLists
from .SharePointSite import SharePointSite


class SharePointAPI:
    """High-level client for interacting with SharePoint sites.

    Provides methods for authentication, list management, file operations,
    and time-registration handling. All public interactions should be performed
    through an instance created via :meth:`_compact_init`.
    """

    @classmethod
    def _compact_init(cls, credentials: dict):
        """
        Initialise a :class:`SharePointAPI` instance from a credentials dictionary.

        Parameters
        ----------
        credentials : dict
            Mapping containing the keys ``username``, ``password`` and ``sharepoint_url``.
            An optional ``proxies`` key may be supplied to route HTTP requests through a proxy.

        Returns
        -------
        SharePointAPI
            A fully-initialised ``SharePointAPI`` object ready for use.

        Notes
        -----
        This method creates a new instance without invoking ``__init__`` directly,
        then calls ``__init__`` with the extracted values. The stored credentials
        are later used for NTLM authentication in all API calls.
        """
        # Future-warning: encourage use of pre-configured Session instead of credential-based init.
        warnings.warn(
            "SharePointAPI._compact_init will be deprecated in the next minor release (0.3.0). "
            "Prefer using the SharePointAPI constructor with a pre-configured requests.Session.",
            FutureWarning,
            stacklevel=2
        )

        username = credentials['username']
        password = credentials['password']
        sharepoint_url = credentials['sharepoint_url']
        proxies = {
        } if 'proxies' not in credentials else credentials['proxies']

        # Create a session that handles NTLM authentication.
        session = requests.Session()
        session.auth = HttpNtlmAuth(username, password)
        if proxies:
            session.proxies.update(proxies)

        # Create a new instance without calling __init__ directly.
        api = object.__new__(SharePointAPI)
        # Store the session and minimal required attributes.
        api.session = session
        api.sharepoint_url = sharepoint_url
        api.timezone = timezone.utc
        # Preserve empty credentials for fallback (not used when session is present).
        api.username = ''
        api.password = ''
        api.proxies = {}
        return api

    def __init__(self, username: str = '', password: str = '', sharepoint_url: str = '', proxies: dict = None, session: requests.Session = None):
        """
        Initialise the SharePointAPI client.

        Parameters
        ----------
        username : str, optional
            NTLM username. Ignored if ``session`` is provided.
        password : str, optional
            NTLM password. Ignored if ``session`` is provided.
        sharepoint_url : str, optional
            Base URL for SharePoint REST API.
        proxies : dict, optional
            Proxy configuration for ``requests``.
        session : requests.Session, optional
            Pre-configured ``requests.Session`` (e.g., custom authentication headers).
        """
        # Store initial values
        self.username = username
        self.password = password
        self.sharepoint_url = sharepoint_url
        self.proxies = proxies if proxies is not None else {}
        self.timezone = timezone.utc

        # Determine session creation strategy
        if session is not None:
            # Session supplied explicitly – ensure no legacy credentials are also provided.
            if username or password or proxies:
                warnings.warn(
                    "When providing a Session, username, password, and proxies are ignored and must not be set. "
                    "This usage will be deprecated in the next minor release (0.3.0).",
                    FutureWarning,
                    stacklevel=2
                )
            self.session = session
            # Clear legacy credential attributes
            self.username = ''
            self.password = ''
            self.proxies = {}
        elif username or password:
            # Create a session from provided NTLM credentials.
            sess = requests.Session()
            sess.auth = HttpNtlmAuth(username, password)
            if proxies:
                sess.proxies.update(proxies)
            self.session = sess
            # Clear legacy credential attributes
            self.username = ''
            self.password = ''
            self.proxies = {}
        else:
            # No session or credentials – warn about upcoming deprecation.
            warnings.warn(
                "Initialising SharePointAPI without a Session will be deprecated in the next minor release (0.3.0). "
                "Use the SharePointAPI constructor with a pre-configured Session.",
                FutureWarning,
                stacklevel=2
            )
            self.session = None

    def _is_valid_guid(self, guid: str) -> bool:
        """Validate that a string is a proper GUID."""
        pattern = r'^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$'
        return bool(re.fullmatch(pattern, guid))

    def _resolve_sp_list_url(self, sp_list) -> str:
        """
        Resolve ``sp_list`` (GUID, title or ``SharePointList`` instance) to a SharePoint
        list URL fragment.

        The returned string can be used as part of a REST API endpoint, e.g.:

        - For a ``SharePointList`` instance or GUID:
          ``/Web/Lists(guid'<guid>')``
        - For a list title:
          ``/Web/Lists/GetByTitle('<title>')``

        Returns
        -------
        str
            The URL fragment identifying the list.
        """
        # Case 1: already a SharePointList instance – use its GUID.
        if isinstance(sp_list, SharePointList):

            return f"/Web/Lists(guid\'{sp_list.guid}\')"

        # Case 2: string – could be GUID or title.
        if isinstance(sp_list, str):
            if self._is_valid_guid(sp_list):
                return f"/Web/Lists(guid\'{sp_list}\')"
            return f"/Web/Lists/GetByTitle('{sp_list}')"

        raise TypeError(
            'Invalid sp_list argument; expected SharePointList or str')

    def _handle_response(self, response: requests.Response, success_codes: List[int]) -> requests.Response:
        """
        Centralised HTTP response handling.

        Parameters
        ----------
        response : requests.Response
            The response object returned by ``requests``.
        success_codes : List[int]
            HTTP status codes that are considered successful for the caller.

        Returns
        -------
        requests.Response
            The original response if it is successful.

        Raises
        ------
        PermissionError
            Raised for HTTP 401 Unauthorized responses.
        FileNotFoundError
            Raised for HTTP 404 Not Found responses.
        ValueError
            Raised for HTTP 400 Bad Request responses.
        ConnectionError
            Raised for any other unexpected status codes.
        """
        status = response.status_code

        if status == 401:
            print('Request failed (401 Unauthorized):')
            print(f'URL: {response.request.url}')
            print(response.text)
            raise PermissionError(
                'Unauthorized (401) – authentication failed.')

        if status == 404:
            print('Request failed (404 Not Found):')
            print(f'URL: {response.request.url}')
            try:
                print(response.json()['error']['message']['value'])
            except Exception:
                print('No detailed error message')
            raise FileNotFoundError(
                'Resource not found (404) – see printed details.')

        if status == 400:
            print('Request failed (400 Bad Request):')
            print(response.text)
            raise ValueError('Bad request (400) – see printed details.')

        if status not in success_codes:
            print(f'Request failed (status {status}):')
            try:
                error_msg = response.json().get('error', {}).get('message', {}).get('value')
                if error_msg:
                    print(f'Error message: {error_msg}')
            except Exception:
                print(response.text)
            raise ConnectionError(
                f'Unexpected status code {status} – see printed details.')

        return response

    def _post_call(self, url: str, post_data: dict, form_digest_value: str | None = None, merge: bool = False) -> requests.Response:
        """
        Perform a POST request against the SharePoint REST API.

        Enhanced error handling:
        * Network-level errors (timeouts, DNS failures, etc.) are caught and re-raised as
          ``ConnectionError`` with a helpful message.
        * HTTP error codes are reported with status, URL and response body when available.
        * The method always returns a ``requests.Response`` on success (status 200, 201 or 204).

        Parameters
        ----------
        url : str
            The full endpoint URL.
        post_data : dict
            JSON-serialisable payload to send.
        form_digest_value : str | None, optional
            FormDigest required for POST/PUT/MERGE operations.
        merge : bool, optional
            If ``True`` the ``X-HTTP-Method: MERGE`` header is added.

        Returns
        -------
        requests.Response
            The successful response object.
        """
        # Build headers – start from any headers already present on the session,
        # then overlay the mandatory SharePoint headers (later keys win).
        base_headers = dict(self.session.headers) if getattr(
            self, 'session', None) else {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'accept': 'application/json;odata=verbose',
            'Content-type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Length': str(len(f'{post_data}')),
            'If-Match': '*'
        }
        # Merge – session headers are kept unless explicitly overridden.
        headers = {**base_headers, **headers}
        if form_digest_value is not None:
            headers['X-RequestDigest'] = f'{form_digest_value}'
        if merge:
            headers['X-HTTP-Method'] = 'MERGE'

        try:
            if not getattr(self, 'session', None):
                raise RuntimeError(
                    "Session not initialized. Provide a pre-configured Session via the SharePointAPI constructor.")
            response = self.session.post(
                url,
                headers=headers,
                json=post_data,
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            print(f'Network error during POST to {url}: {exc}')
            raise ConnectionError(
                f'Network error during POST request: {exc}') from exc

        # Centralised response handling
        return self._handle_response(response, [200, 201, 204])

    def _put_call(self, url: str, put_data: dict, form_digest_value: str | None = None, merge: bool = False) -> requests.Response:
        """
        Perform a PUT request against the SharePoint REST API.

        Enhanced error handling:
        * Network-level errors (timeouts, DNS failures, etc.) are caught and re-raised as
          ``ConnectionError`` with a helpful message.
        * HTTP error codes are reported with status, URL and response body when available.
        * The method always returns a ``requests.Response`` on success (status 200, 201 or 204).

        Parameters
        ----------
        url : str
            The full endpoint URL.
        put_data : dict
            JSON-serialisable payload to send.
        form_digest_value : str | None, optional
            FormDigest required for POST/PUT/MERGE operations.
        merge : bool, optional
            If ``True`` the ``X-HTTP-Method: MERGE`` header is added.

        Returns
        -------
        requests.Response
            The successful response object.
        """
        # Build headers – preserve any pre-configured session headers.
        base_headers = dict(self.session.headers) if getattr(
            self, 'session', None) else {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'accept': 'application/json;odata=verbose',
            'Content-type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Length': str(len(f'{put_data}')),
            'If-Match': '*'
        }
        headers = {**base_headers, **headers}
        if form_digest_value is not None:
            headers['X-RequestDigest'] = f'{form_digest_value}'
        if merge:
            headers['X-HTTP-Method'] = 'MERGE'

        try:
            if not getattr(self, 'session', None):
                raise RuntimeError(
                    "Session not initialized. Provide a pre-configured Session via the SharePointAPI constructor.")
            response = self.session.put(
                url,
                headers=headers,
                json=put_data,
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            print(f'Network error during PUT to {url}: {exc}')
            raise ConnectionError(
                f'Network error during PUT request: {exc}') from exc

        # Centralised response handling
        return self._handle_response(response, [200, 201, 204])

    def _attachment_call(self, url: str, post_data: bytes | None = None, form_digest_value: str | None = None,
                         overwrite: bool = False, x_http_method: str | None = None) -> requests.Response:
        """
        Perform an attachment-related request (POST, PUT, DELETE) against the SharePoint REST API.

        Enhanced error handling:
        * Network-level errors (timeouts, DNS failures, etc.) are caught and re-raised as
          ``ConnectionError`` with a helpful message.
        * HTTP error codes are reported with status, URL and response body when available.
        * The method always returns a ``requests.Response`` on success (status 200 or 204).

        Parameters
        ----------
        url : str
            The full endpoint URL.
        post_data : bytes | None, optional
            Binary payload for the request (e.g., file content). If ``None`` a simple POST/DELETE is performed.
        form_digest_value : str | None, optional
            FormDigest required for POST/PUT/DELETE operations.
        overwrite : bool, optional
            If ``True`` the ``X-HTTP-Method: PUT`` header is added (used for overwriting files).
        x_http_method : str | None, optional
            Explicit HTTP method override (e.g., ``'DELETE'`` or ``'PUT'``). Takes precedence over ``overwrite``.
        """
        # Build base headers – start from session headers, then add the mandatory ones.
        base_headers = dict(self.session.headers) if getattr(
            self, 'session', None) else {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'accept': 'application/json;odata=verbose',
            'X-RequestDigest': f'{form_digest_value}'
        }
        headers = {**base_headers, **headers}

        # Determine effective X-HTTP-Method
        if overwrite:
            headers['X-HTTP-Method'] = "PUT"
        if x_http_method:
            method = x_http_method.lower()
            if method == 'delete':
                headers['X-HTTP-Method'] = "DELETE"
            elif method == 'put':
                headers['X-HTTP-Method'] = "PUT"
            else:
                print(f'X-HTTP-Method \"{x_http_method}\" is not implemented')
                raise ConnectionError(
                    f'Unsupported X-HTTP-Method: {x_http_method}')

        # Add Content-Length when payload present
        if post_data is not None:
            headers['Content-Length'] = str(len(post_data))

        try:
            if not getattr(self, 'session', None):
                raise RuntimeError(
                    "Session not initialized. Provide a pre-configured Session via the SharePointAPI constructor.")
            response = self.session.post(
                url,
                data=post_data,
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            print(f'Network error during attachment request to {url}: {exc}')
            raise ConnectionError(
                f'Network error during attachment request: {exc}') from exc

        # Centralised response handling (attachment calls consider 200 and 204 as success)
        return self._handle_response(response, [200, 204])

    def _get_call(self, url, *args, **kwargs) -> requests.Response:
        """
        Perform a GET request against the SharePoint REST API.

        Enhanced error handling:
        * Network-level errors (timeouts, DNS failures, etc.) are caught and re-raised as
          ``ConnectionError`` with a helpful message.
        * HTTP error codes are reported with status, URL and response body when available.
        * The method always returns a ``requests.Response`` on success (status 200).

        Parameters
        ----------
        url : str
            The full endpoint URL.
        """
        # Build headers – keep any custom session headers.
        base_headers = dict(self.session.headers) if getattr(
            self, 'session', None) else {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'accept': 'application/json;odata=verbose',
            'Content-type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        headers = {**base_headers, **headers}

        try:
            if not getattr(self, 'session', None):
                raise RuntimeError(
                    "Session not initialized. Provide a pre-configured Session via the SharePointAPI constructor.")
            response = self.session.get(
                url,
                headers=headers,
                timeout=30,
                *args,
                **kwargs
            )
        except requests.exceptions.RequestException as exc:
            print(f'Network error during GET to {url}: {exc}')
            raise ConnectionError(
                f'Network error during GET request: {exc}') from exc

        # Centralised response handling (GET expects 200)
        return self._handle_response(response, [200])

    def get_users(self, sharepoint_site, filters=None, select_fields=None):
        '''
            Returns a list of users from a given sharepoint_site.
            Optional ``filters`` can be provided to filter the users using OData syntax.
            Optional ``select_fields`` (list of strings) can be provided to limit the returned fields
            via the ``$select`` query option.
        '''
        # Build query arguments
        arguments = []

        if filters is not None:
            if not isinstance(filters, list):
                filter_string = self.py2sp_conditional(filters)
            else:
                filter_string = self.py2sp_conditional(' and '.join(filters))
            arguments.append(f'$filter={filter_string}')

        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            arguments.append(f'$select={select_string}')

        # Construct final URL
        base_url = f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/siteusers'
        if arguments:
            url = f'{base_url}?{"&".join(arguments)}'
        else:
            url = base_url

        r = self._get_call(url)

        users = []

        for user_settings in r.json()["d"]["results"]:
            users.append(SharePointUser(user_settings))

        return SharePointUserList(sharepoint_site, users)

    def get_group_users(self, sharepoint_site, group_name: str, filters=None, select_fields=None) -> SharePointUserList:
        """
        Retrieve users that are members of a SharePoint group, with optional OData filters
        and field selection.

        Parameters
        ----------
        sharepoint_site : str
            Identifier of the SharePoint site (e.g., 'mySite').
        group_name : str
            Exact name of the SharePoint group.
        filters : str or list, optional
            OData filter expression(s) to limit the returned users.
        select_fields : list or str, optional
            Fields to include in the response via the ``$select`` query option.

        Returns
        -------
        SharePointUserList
            A list-like container with :class:`SharePointUser` objects for each member.
        """
        # Build the request URL for the group's users.
        # SharePoint REST endpoint: /_api/web/sitegroups/GetByName('<group_name>')/users
        base_url = (
            f"{self.sharepoint_url}/cases/{sharepoint_site}"
            f"/_api/web/sitegroups/GetByName('{group_name}')/users"
        )

        # Build query arguments (filters / select)
        arguments = []

        if filters is not None:
            if not isinstance(filters, list):
                filter_string = self.py2sp_conditional(filters)
            else:
                filter_string = self.py2sp_conditional(' and '.join(filters))
            arguments.append(f"$filter={filter_string}")

        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            arguments.append(f"$select={select_string}")

        # Construct final URL
        if arguments:
            url = f"{base_url}?{'&'.join(arguments)}"
        else:
            url = base_url

        # Perform the GET request.
        r = self._get_call(url)

        # Parse the JSON payload – users are under ``d.results``.
        users = [
            SharePointUser(user_settings)
            for user_settings in r.json()["d"]["results"]
        ]

        # Return a ``SharePointUserList`` (consistent with other user-retrieval methods).
        return SharePointUserList(sharepoint_site, users)

    def get_user(self, sharepoint_site, user_id, select_fields=None):
        '''
            Returns a single user from a given sharepoint_site.
            If ``user_id`` is ``None`` an empty :class:`SharePointUser` instance is returned.
            Optional ``select_fields`` (list of strings) can be provided to limit the fields
            returned via the ``$select`` OData query option.
        '''
        if user_id is None:
            return SharePointUser()

        # Build the request URL, adding $select if needed.
        base_url = f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/getUserById({user_id})'
        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            url = f'{base_url}?$select={select_string}'
        else:
            url = base_url

        try:
            r = self._get_call(url)
        except ConnectionError:
            # If the user does not exist, return an empty user object for graceful handling.
            print(
                f"User with ID {user_id} does not exist in sharepoint_site {sharepoint_site}")
            return SharePointUser()

        # The endpoint returns the user object directly under the ``d`` key.
        user_settings = r.json()["d"]
        return SharePointUser(user_settings)

    # SP Lists

    def get_lists(self, sharepoint_site):
        '''
            Returns a list of lists from a given sharepoint_site
        '''
        r = self._get_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/Lists')

        _lists = []
        for list_props in r.json()["d"]["results"]:
            _lists.append(SharePointList(self, sharepoint_site, list_props))

        return SharePointLists(_lists)

    def get_site_metadata(self, sharepoint_site: str, select_fields: list[str] | None = None) -> dict:
        """
        Retrieve metadata of a SharePoint site.

        Parameters
        ----------
        sharepoint_site : str
            Identifier of the SharePoint site (e.g., 'mySite').
        select_fields : list[str] | None, optional
            List of fields to select from the site metadata via the ``$select`` OData query option.
            If omitted, all fields are returned.

        Returns
        -------
        dict
            Dictionary containing the site's metadata as returned by the SharePoint REST API.
        """
        # Base endpoint for site metadata
        endpoint = f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web'

        # Append $select query if specific fields are requested
        if select_fields:
            fields = ','.join(select_fields)
            endpoint = f'{endpoint}?$select={fields}'

        r = self._get_call(endpoint)
        return r.json()["d"]

    def get_site(self, sharepoint_site: str) -> SharePointSite:
        """
        Return a :class:`SharePointSite` object representing the given site.

        Parameters
        ----------
        sharepoint_site : str
            Identifier of the SharePoint site (e.g., ``'mySite'``).

        Returns
        -------
        SharePointSite
            A high-level wrapper around site-wide operations.
        """
        return SharePointSite(self, sharepoint_site)

    def get_list(self, sharepoint_site, sp_list, filters=None, top=1000, view_path=None, select_fields=None, SPListType: SharePointList = SharePointList) -> SharePointList:
        '''
            Returns a list from a given sharepoint_site using its guid

            Returns a subset of items from a list

            sharepoint_site:
            guid: the guid of the list to retrieve items from

            Optional ``select_fields`` (list of strings) can be provided to limit the fields
            returned for each list item via the ``$select`` OData query option.
        '''

        sp_list_url = self._resolve_sp_list_url(sp_list)

        r = self._get_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/{sp_list_url}')
        list_settings = r.json()["d"]

        arguments = []
        if filters is not None:
            if not isinstance(filters, list):
                filter_string = self.py2sp_conditional(filters)
                # print(filters)
                # raise('invalid search filters')
            else:

                filter_string = self.py2sp_conditional(' and '.join(filters))
            arguments.append(f'$filter={filter_string}')

        if view_path is not None:
            # Shows top x items
            arguments.append(f'$ViewPath={view_path}')

        if top is not None:
            # Shows top x items
            arguments.append(f'$top={top}')

        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            arguments.append(f'$select={select_string}')

        items = []
        if arguments:
            r = self._get_call(
                f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/{sp_list_url}/items?{"&".join(arguments)}')
            items = [SPListType.SPItem(self, sharepoint_site, item_settings)
                     for item_settings in r.json()["d"]["results"]]

        return SharePointList(self, sharepoint_site,
                              settings=list_settings, items=items)

    def get_list_by_name(self, sharepoint_site, sp_list_name: str, filters=None, top=1000, view_path=None, select_fields=None, SPListType: SharePointList = SharePointList) -> SharePointList:
        '''
            Returns a list from a given sharepoint_site filtering by list name

            Returns a subset of items from a list

            sharepoint_site: The sharepoint_site containing the list
            sp_list_name: the name of the list
            filters: query filters
            top: Maximum items to query from the list

            Optional ``select_fields`` (list of strings) can be provided to limit the fields
            returned for each list item via the ``$select`` OData query option.
        '''
        # Retrieve the list directly by its title using SharePoint REST API v1
        try:
            r = self._get_call(
                f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/Lists/GetByTitle('{sp_list_name}')")
        except ConnectionError:
            # The list was not found – provide a clear error message
            msg = f"List '{sp_list_name}' does not exist in sharepoint_site {sharepoint_site}"
            print(msg)
            raise ConnectionError(msg)

        sp_list = SPListType(self, sharepoint_site, r.json()["d"])

        guid = sp_list.guid

        arguments = []

        if filters is not None:
            if not isinstance(filters, list):
                filter_string = self.py2sp_conditional(filters)
            else:
                filter_string = self.py2sp_conditional(' and '.join(filters))
            arguments.append(f"$filter={filter_string}")

        if view_path is not None:
            arguments.append(f"$ViewPath={view_path}")

        if top is not None:
            arguments.append(f"$top={top}")

        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            arguments.append(f"$select={select_string}")

        r = self._get_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/Lists(guid'{guid}')/items?{'&'.join(arguments)}")
        items = [SPListType.SPItem(self, sharepoint_site, item_settings)
                 for item_settings in r.json()["d"]["results"]]
        sp_list.append_items(items)
        return sp_list

    def get_list_from_json(self, file_name, SPListType: SharePointList = SharePointList) -> SharePointList:
        '''
            Returns a list from a sharepoint_site based on a json file.

            file_name: the json file to load the list from

        '''
        try:
            with open(file_name, 'r') as fp:
                data_dict = json.load(fp)

            sharepoint_site = data_dict['sharepoint_site']
            guid = data_dict['GUID']

            cases = []
            for case in data_dict['cases']:
                settings = case["settings"]
                versions = None if "versions" not in case else case["versions"]
                cases.append(SPListType.SPItem(
                    self, sharepoint_site, settings, versions))

            return SPListType(self, sharepoint_site, data_dict['Settings'], cases)
        except FileNotFoundError as err:
            print(f"File '{file_name}' was not found")
            raise err
        except Exception as err:
            raise err

    # SP Item

    def get_list_metadata(self, sharepoint_site, sp_list, SPListType: SharePointList = SharePointList) -> SharePointList:
        """
        Retrieve only the metadata of a SharePoint list without fetching its items.
        Useful when only list properties (e.g., title, guid) are needed.
        """
        sp_list_url = self._resolve_sp_list_url(sp_list)
        # Otherwise, fetch minimal metadata using the GUID.
        r = self._get_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/{sp_list_url}')
        return SPListType(self, sharepoint_site, r.json()["d"])

    def get_item(self, sharepoint_site, sp_list, item_id, select_fields=None) -> SharePointListItem:
        '''
            Returns a single list item from a given sharepoint_site.
            Optional ``select_fields`` (list of strings) can be provided to limit the fields
            returned via the ``$select`` OData query option.
        '''

        # Resolve sp_list to URL fragment (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        # Build the request URL, adding $select if needed.
        if select_fields is not None:
            if isinstance(select_fields, list):
                select_string = ','.join(select_fields)
            else:
                select_string = str(select_fields)
            url = f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})?$select={select_string}'
        else:
            url = f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})'

        r = self._get_call(url)

        settings = r.json()["d"]
        return SharePointListItem(self, sharepoint_site, settings)

    def create_item(self, sharepoint_site, sp_list, data) -> SharePointListItem:
        # Uses either guid or SharePointList
        # Resolve sp_list to GUID (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})

        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items', data, form_digest_value)

        settings = r.json()["d"]
        return SharePointListItem(self, sharepoint_site, settings)

    def update_item(self, sharepoint_site, sp_list, item_id, data) -> None:
        '''
            Update a sharepoint item

            sharepoint_site: The sharepoint_site containing the item
            sp_list: The list containing the item
            item_id: The id of the item
            data: Data to push to the item
        '''
        # Resolve sp_list to GUID (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})

        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})', data, form_digest_value, merge=True)

        return r

    def attach_file(self, sharepoint_site, sp_list, item, file_name, file_content) -> dict:
        # Uses either guid or SharePointList
        # Resolve sp_list to GUID (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})
        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._attachment_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item.Id})/AttachmentFiles/add(FileName='{file_name}')", file_content, form_digest_value)

        return r.json()

    def get_item_versions(self, sharepoint_site, sp_list, item_id, select_fields: Optional[List[str]] = None) -> list:
        '''
            Returns a list of users from a given sharepoint_site
        '''

        # Resolve sp_list to GUID (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        if select_fields:
            r = self._get_call(
                f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})/versions?$select={",".join(select_fields)}')
        else:
            r = self._get_call(
                f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})/Versions')

        versions = r.json()["d"]['results']
        return versions

    # Cases

    def get_cases_list_from_json(self, file_name) -> CasesList:
        '''
            Returns a cases list from a sharepoint_site based on a json file.

            file_name: the json file to load the list from

        '''

        return self.get_list_from_json(file_name, SPListType=CasesList)

    def get_cases_list(self, sharepoint_site, sp_list, filters=None, top=1000, view_path=None, select_fields=None) -> CasesList:
        '''
            Returns a cases list from a given sharepoint_site using its guid

            Returns a subset of items from a list

            sharepoint_site: The sharepoint_site containing the list
            sp_list: the guid of the list to retrieve items from
            filters: query filters
            top: Maximum items to query from the list
        '''

        return self.get_list(sharepoint_site, sp_list, filters, top, view_path, select_fields, SPListType=CasesList)

    def get_cases_list_by_name(self, sharepoint_site, sp_list_name: str = 'Cases', filters=None, top=1000, view_path=None, select_fields=None) -> CasesList:
        '''
            Returns a cases list from a given sharepoint_site filtering by list name

            sharepoint_site: The sharepoint_site containing the list
            sp_list_name: the name of the list
            filters: query filters
            top: Maximum items to query from the list
        '''
        return self.get_list_by_name(sharepoint_site, sp_list_name, filters, top, view_path, select_fields, SPListType=CasesList)

    def get_case(self, sharepoint_site, sp_list, item_id) -> SharePointListItem:
        '''
            Returns a list of users from a given sharepoint_site
        '''

        # Resolve sp_list to GUID (and list object if needed)
        sp_list_url = self._resolve_sp_list_url(sp_list)

        r = self._get_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api{sp_list_url}/items({item_id})')

        settings = r.json()["d"]
        return SharepointSiteCase(self, sharepoint_site, settings)

    # Time Registration

    def get_time_registration_list_from_json(self, file_name) -> TimeRegistrationList:
        '''
            Returns a Time Registration list from a sharepoint_site based on a json file.

            file_name: the json file to load the list from

        '''

        return self.get_list_from_json(file_name, SPListType=TimeRegistrationList)

    def get_time_registration_list(self, sharepoint_site, sp_list, filters=None, top=1000, view_path=None, select_fields=None) -> TimeRegistrationList:
        '''
            Returns a Time Registration list from a given sharepoint_site using its guid

            Returns a subset of items from a list

            sharepoint_site: The sharepoint_site containing the list
            sp_list: the guid of the list to retrieve items from
            filters: query filters
            top: Maximum items to query from the list
        '''

        return self.get_list(sharepoint_site, sp_list, filters, top, view_path, select_fields, SPListType=TimeRegistrationList)

    def get_time_registration_list_by_name(self, sharepoint_site, sp_list_name: str, filters=None, top=1000, view_path=None, select_fields=None) -> TimeRegistrationList:
        '''
            Returns a Time Registration list from a given sharepoint_site filtering by list name

            sharepoint_site: The sharepoint_site containing the list
            sp_list_name: the name of the list
            filters: query filters
            top: Maximum items to query from the list
        '''
        return self.get_list_by_name(sharepoint_site, sp_list_name, filters, top, view_path, select_fields, SPListType=TimeRegistrationList)

    # SP Files

    def folder_exists(self, sharepoint_site, folder, in_doc_lib=True):
        """
        Check whether a folder exists in the given SharePoint site.

        Parameters
        ----------
        sharepoint_site : str
            The SharePoint site identifier.
        folder : str
            The folder name (relative to the document library if ``in_doc_lib`` is True).
        in_doc_lib : bool, optional
            If True, the folder path is prefixed with ``DocumentLibrary``. Defaults to True.

        Returns
        -------
        bool
            ``True`` if the folder exists, ``False`` otherwise.
        """
        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._get_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('/cases/{sharepoint_site}/{folder}')/ListItemAllFields")

        return False if ("ListItemAllFields" in r.json()["d"] and r.json()["d"]["ListItemAllFields"] is None) else True

    def create_new_folder(self, sharepoint_site, folder, new_folder, in_doc_lib=True):
        '''
            Creates a new folder
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})
        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._post_call(f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/web/folders",
                            form_digest_value=form_digest_value,
                            post_data={
            "ServerRelativeUrl": f'/cases/{sharepoint_site}/{folder}/{new_folder}',
        }
        )

        return r.status_code

    def get_files(self, sharepoint_site, folder, in_doc_lib=True):
        '''
            Returns a list of files from a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._get_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('/cases/{sharepoint_site}/{folder}')/Files")

        return r.json()["d"]["results"]

    def get_file_content(self, sharepoint_site, folder, file, in_doc_lib=True):
        '''
            Downloads and saves a file from a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._get_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('/cases/{sharepoint_site}/{folder}')/Files('{file}')/$value")
        return r._content

    def download_file(self, sharepoint_site, folder, file, out_file=None, in_doc_lib=True):
        '''
            Downloads and saves a file from a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        if not out_file:
            out_file = file

        file_content = self.get_file_content(
            sharepoint_site, folder, file, in_doc_lib)

        with open(out_file, 'wb') as f:
            f.write(file_content)

    def upload_file_content(self, sharepoint_site, folder, file, file_content, overwrite=False, in_doc_lib=True):
        '''
            Uploads a file to a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})
        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._attachment_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('/cases/{sharepoint_site}/{folder}')/Files/add(url='{file}',overwrite={str(overwrite).lower()})",
            file_content,
            form_digest_value)
        return r.json()

    def upload_file(self, sharepoint_site, folder, file, in_file=None, overwrite=False, in_doc_lib=True):
        '''
            Uploads a file to a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        if not in_file:
            in_file = file
        with open(in_file, 'rb') as f:
            file_content = f.read()

        return self.upload_file_content(sharepoint_site, folder, file, file_content, overwrite, False)

    def delete_file(self, sharepoint_site, folder, file, in_doc_lib=True):
        '''
            Uploads a file to a folder in a given sharepoint_site
        '''

        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})
        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        r = self._attachment_call(
            url=f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('/cases/{sharepoint_site}/{folder}')/Files('{file}')",
            post_data=None,
            form_digest_value=form_digest_value,
            x_http_method='DELETE')

    def copy_file(self, sharepoint_site, folder, file, out_folder=None, out_file=None, overwrite=False, in_doc_lib=True):
        """
        Copy a file within a SharePoint site.

        Parameters
        ----------
        sharepoint_site : str
            The SharePoint site identifier.
        folder : str
            Source folder (relative to the document library if ``in_doc_lib`` is True).
        file : str
            Name of the file to copy.
        out_folder : str, optional
            Destination folder. If omitted, defaults to the source folder.
        out_file : str, optional
            Destination file name. If omitted, defaults to ``'copy of ' + file``.
        overwrite : bool, optional
            Overwrite the destination file if it already exists. Defaults to ``False``.
        in_doc_lib : bool, optional
            Whether the operation is within the document library. Defaults to ``True``.

        Returns
        -------
        None
            The method performs the copy operation via SharePoint REST API.
        """
        if in_doc_lib:
            folder = os.path.join("DocumentLibrary", folder)

        if not out_file:
            out_file = 'copy of '+file

        if not out_folder:
            out_folder = folder

        r = self._post_call(
            f'{self.sharepoint_url}/cases/{sharepoint_site}/_api/contextinfo', {})
        form_digest_value = r.json(
        )["d"]["GetContextWebInformation"]["FormDigestValue"]

        in_path = f"/cases/{sharepoint_site}/{folder}"
        out_path = f"/cases/{sharepoint_site}/{out_folder}/{out_file}"

        r = self._attachment_call(
            f"{self.sharepoint_url}/cases/{sharepoint_site}/_api/Web/GetFolderByServerRelativeUrl('{in_path}')/Files('{file}')/copyto(strnewurl='{out_path}',boverwrite={str(overwrite).lower()})",
            None,
            form_digest_value)

    # STATIC METHODS

    @staticmethod
    def py2sp_conditional(conditional: str):
        """
        Convert a Python conditional expression to SharePoint OData query syntax.

        Parameters
        ----------
        conditional : str
            A conditional expression using Python comparison operators.

        Returns
        -------
        str
            The expression with operators replaced by their OData equivalents.
        """
        return conditional.replace('==', 'eq').replace('!=', 'ne').replace('>=', 'ge').replace('<=', 'le').replace('>', 'gt').replace('<', 'lt')
