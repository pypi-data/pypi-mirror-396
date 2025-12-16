# TODO: set up chores
import json
from typing import Union, List, Literal, Deque
import logging
from datetime import datetime
from collections import deque
from urllib.parse import urlencode
from requests import Request, sessions
from pymementodb.library import Library
from pymementodb.entry import Entry
from pymementodb.exception import (MementoException,
                                   MementoUnauthorizedException,
                                   MementoBadRequestException,
                                   MementoNotAllowedException,
                                   MementoRateLimitException,
                                   MementoNotFoundException)
from .__version__ import __version__

logger = logging.getLogger(__name__)

"""Memento Database Python SDK

Memento Database Python SDK provides a simple interface to access Memento Database API.

"""


class Memento:
    """ The Memento class that provides all the functionality.

    """

    MEMENTO_VERSION = "v1"
    # Endpoint suffixes to make the request
    GET_LIBRARIES_SUFFIX = "libraries"
    GET_LIBRARY_SUFFIX = "libraries/{library_id}"
    GET_ENTRIES_SUFFIX = "libraries/{library_id}/entries"
    GET_ENTRY_SUFFIX = "libraries/{library_id}/entries/{entry_id}"
    EDIT_ENTRY_SUFFIX = "libraries/{library_id}/entries/{entry_id}"
    CREATE_ENTRY_SUFFIX = "libraries/{library_id}/entries"
    DELETE_ENTRY_SUFFIX = "libraries/{library_id}/entries/{entry_id}"

    # deque of all tokens provided to the different Memento instances
    # used to choose the token that satisfies the API rates limit
    _all_auth_tokens: Deque[str] = deque()

    def __init__(self, auth_token: str, server: str = 'https://api.mementodatabase.com/'):
        """

        Args:
            auth_token: tokens can be found in the desktop Memento app
            server: url of the Memento serve
        """
        self._auth_tokens = set()
        self.add_auth_token(auth_token)
        self.base_url = f'{server}{self.MEMENTO_VERSION}/'

    @staticmethod
    def _prepare_url_params(url_token: str, parameters: Union[dict, None] = None) -> str:
        if parameters is None:
            parameters = {}
        else:
            parameters = {param: value for param, value in parameters.items() if value is not None}
        parameters['token'] = url_token
        return "?"+urlencode(parameters)

    def _make_request(self, endpoint_suffix: str, method: Literal['GET', 'POST', 'PATCH', 'DELETE']='GET',
                      parameters: dict = None, body: dict = None, files = None):

        headers = {}
        if files is not None:
            headers = {'Content-Type': 'multipart/form-data; boundary=---BOUNDARY'}
        elif method in ['POST', 'PATCH']:
            headers = {'Content-Type': 'application/json'}

        while True:
            url = f'{self.base_url}{endpoint_suffix}' + self._prepare_url_params(self.auth_token, parameters)
            if body is not None:
                request_obj = Request(url=url, method=method, headers=headers, data=json.dumps(body), files=files)
            else:
                request_obj = Request(url=url, method=method, headers=headers, files=files)

            prep_req = request_obj.prepare()

            with sessions.Session() as session:
                response = session.send(prep_req)

            if response.status_code == 429 and 'API rate limit exceeded' in response.text:
                logger.debug(f'Auth token {self.auth_token}: rate limit exceeded.')
                self._rotate_auth_tokens()
            else:
                break

        if response.status_code in [200, 201, 204]:
            if response.content and hasattr(response.content, "decode"):
                return response.content.decode("utf-8")
            return response.content

        if response.status_code == 401:
            raise MementoUnauthorizedException("Please check your auth token", response=response)

        if response.status_code == 429:
            if 'API rate limit exceeded' in response.text:
                raise MementoRateLimitException("API rate limit exceeded", response=response)
            else:
                raise MementoNotAllowedException("You are not allowed to perform this operation", response=response)

        if response.status_code == 400:
            raise MementoBadRequestException("Please check your request", response=response)

        if response.status_code == 404:
            raise MementoNotFoundException("Required resource is not found", response)

        if response.status_code == 500:
            raise MementoException("Internal server error happened", response)

        raise MementoException("Unknown error happened", response)

    def add_auth_token(self, token: str) -> None:
        """Add more authorization tokens.

        Args:
            token: tokens can be found in the desktop Memento app

        Notes:
            API rates limits https://mementodatabase.docs.apiary.io/#introduction/api-limits are defined per token.

        """
        self._auth_tokens.add(token)
        if token not in self._all_auth_tokens:
            self._all_auth_tokens.appendleft(token)

    @property
    def auth_token(self) -> str:
        """Yields the authorization token.
        More specifically, the first token from the left in _all_auth_tokens that is also in _auth_tokens set.

        Returns:
            authorization token that was provided during the initialization or was added with add_auth_token()
        """
        for auth_token in self._all_auth_tokens:
            if auth_token in self._auth_tokens:
                return auth_token
        else:
            assert(False, 'None of instance auth tokens are present in class _all_auth_tokens variable.')

    def _rotate_auth_tokens(self) -> None:
        """Move the token currently used by the instance to the end of the _auth_tokens deque.
        The motivation is to keep in the front of the deque (and thus use) that tokens
        which have API rates left.

        """
        for i, auth_token in enumerate(self._all_auth_tokens):
            if auth_token in self._auth_tokens:
                del self._all_auth_tokens[i]
                self._all_auth_tokens.append(auth_token)
                break
        else:
            assert(False, 'None of instance auth tokens are present in class _all_auth_tokens variable.')

    def list_libraries(self) -> List[dict]:
        """Get the list of library info.

        Format of the library info:
            {'id': '<id>',
            'name': '<name>',
            'owner': '<owner>',
            'createdTime': datetime.datetime with tzinfo=datetime.timezone.utc,
            'modifiedTime': datetime.datetime with tzinfo=datetime.timezone.utc}

        Returns:
            list of dicts with library info
        """
        content = self._make_request(Memento.GET_LIBRARIES_SUFFIX)
        content = json.loads(content)

        for lib_info in content['libraries']:
            created_isoformat = lib_info['createdTime'].replace('Z', '+00:00')
            lib_info['createdTime'] = datetime.fromisoformat(created_isoformat)
            modified_isoformat = lib_info['modifiedTime'].replace('Z', '+00:00')
            lib_info['modifiedTime'] = datetime.fromisoformat(modified_isoformat)

        return content['libraries']

    def get_library(self, library_id: str) -> Library:
        """Get the specific library

        Args:
            library_id: id of the library which is queried

        Returns:
            library
        """
        content = self._make_request(Memento.GET_LIBRARY_SUFFIX.format(library_id=library_id))
        lib_data = json.loads(content)

        return Library(**lib_data)

    def get_entries(self, library_id: str, limit: int = None,
                    field_ids: List[int] = None, start_revision: int = None) -> List[Entry]:
        """Get the entries in the library.

        Entries are ordered by modification time.

        Args:
            library_id: id of the library for which the entries are queried
            limit (all by default): the maximum number of entries in the result
            field_ids (all by default): list of fields which values should be present in entries
            start_revision (olders by default): the oldest revision since which to include the entries

        Returns:
            list of entries
        """
        if field_ids is not None:
            field_ids = [str(id) for id in field_ids]
            field_ids = ','.join(field_ids)
        else:
            field_ids = 'all'

        if limit is None:
            # Memento server default value is 50
            # thus, set the limit explicitely to some huge number
            limit = 9999999

        content = self._make_request(Memento.GET_ENTRIES_SUFFIX.format(library_id=library_id),
                                     parameters={'pageSize': limit, 'fields': field_ids,
                                                 'startRevision': start_revision})
        content = json.loads(content)

        entries = [Entry(lib_id = library_id, **entry_data) for entry_data in content['entries']]

        return entries

    def get_entry(self, library_id: str, entry_id: str) -> Entry:
        """Get the specific entry.

        Args:
            library_id: id of the library for which the entry is queried
            entry_id: id of the entry that is queried

        Returns:
            entry
        """

        content = self._make_request(Memento.GET_ENTRY_SUFFIX.format(library_id=library_id, entry_id=entry_id))
        entry_data = json.loads(content)

        return Entry(lib_id = library_id, **entry_data)

    def edit_entry(self, library_id: str, entry_id: str, field_values: list) -> Entry:
        """Edit the specific entry.

        Datetime fields to be provided in the '2023-08-31T16:47:00+00:00' format.

        Args:
            library_id: id of the library from which the entry is edited
            entry_id: id of the entry that is edited
            field_values: the list of dictionaries with new field values,
                e.g., [{'id': <field id>, 'value': <field value>}, ...].

        Returns:
            edited entry
        """
        # TODO: check fields and correctly parse dt ones
        content = self._make_request(Memento.EDIT_ENTRY_SUFFIX.format(library_id=library_id, entry_id=entry_id),
                                     method='PATCH', body={'fields': field_values})
        entry_data = json.loads(content)

        return Entry(lib_id = library_id, **entry_data)

    def create_entry(self, library_id: str, field_values: list) -> Entry:
        """Create an entry.

        Datetime fields to be provided in the '2023-08-31T16:47:00+00:00' format.

        Args:
            library_id: id of the library in which the entry is created
            field_values: the list of dictionaries with new field values,
                e.g., [{'id': <field id>, 'value': <field value>}, ...].

        Returns:
            new entry
        """
        # TODO: check fields and correctly parse dt ones
        content = self._make_request(Memento.CREATE_ENTRY_SUFFIX.format(library_id=library_id), method='POST',
                                     body={'fields': field_values})
        entry_data = json.loads(content)

        return Entry(lib_id = library_id, **entry_data)

    def delete_entry(self, library_id: str, entry_id: str) -> None:
        """Delete the specific entry.

        Args:
            library_id: id of the library from which the entry is deleted
            entry_id: id of the entry that is deleted
        """
        self._make_request(Memento.DELETE_ENTRY_SUFFIX.format(library_id=library_id, entry_id=entry_id),
                                     method='DELETE')

    def search_entries(self) -> List[Entry]:
        # TODO: implement
        raise NotImplementedError()

    def upload_files(self) -> 'File':
        # TODO: implement
        raise NotImplementedError()
