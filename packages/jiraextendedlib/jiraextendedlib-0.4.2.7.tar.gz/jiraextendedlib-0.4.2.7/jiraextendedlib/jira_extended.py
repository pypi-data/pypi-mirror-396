from jira import JIRA
from requests.auth import AuthBase
import requests
import json
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
    Union
)
from jira.resilientsession import ResilientSession, raise_on_error
from jira.resources import Resource

class IpassTokenAuth(AuthBase):
    """Bearer Token Authentication"""

    def __init__(self, token: str, personal_access_token: str, api_key: str):
        # setup any auth-related data here
        self._token = token
        self._personal_access_token = personal_access_token
        self._api_key = api_key

    def __call__(self, r: requests.PreparedRequest):
        # modify and return the request
        r.headers["Authorization"] = self._token
        r.headers["x-authorization"] = f"Bearer {self._personal_access_token}"
        r.headers["Api_key"] = self._api_key
        r.headers["Content-Type"] = 'application/json'
        return r

class JIRAExtended(JIRA):
    def __init__(self, token, personal_access_token, api_key, 
    options: Dict[str, Union[str, bool, Any]] = None, validate = False,
    timeout: Optional[Union[Union[float, int], Tuple[float, float]]] = None,
    default_batch_sizes: Optional[Dict[Type[Resource], Optional[int]]] = None
    ):

        # super(JIRAExtended, self).__init__(options=options, validate=validate, get_server_info = False, default_batch_sizes=default_batch_sizes)
        # Temporarily removed default_batch_sizes paramter to make the module compatible with jira libiray 3.2
        # https://github.com/pycontribs/jira/blob/3.2.0/jira/client.py#L398
        # https://github.com/pycontribs/jira/blob/3.3.2/jira/client.py#L391
        super(JIRAExtended, self).__init__(options=options, validate=validate, get_server_info=False)
        self._create_ipass_token_session(token, personal_access_token, api_key, timeout)

    def _create_ipass_token_session(
        self,
        token: str, personal_access_token: str, api_key: str,
        timeout: Optional[Union[Union[float, int], Tuple[float, float]]],
    ):
        """
        Creates token-based session.
        Header structure: "authorization": "Bearer <token_auth>"
        """
        self._session = ResilientSession(timeout=timeout)
        self._session.auth = IpassTokenAuth(token, personal_access_token, api_key)

    def update(self, issue_key, *args, **kwargs):
        issue = self.issue(issue_key)
        issue.self = self._get_latest_url(f"issue/{issue_key}")
        issue.update(*args, **kwargs)

    def assign_issue(self, issue: Union[int, str], assignee: Optional[str]) -> bool:
        """Assign an issue to a user.

        Args:
            issue (Union[int,str]): the issue ID or key to assign
            assignee (str): the user to assign the issue to.
              None will set it to unassigned. -1 will set it to Automatic.

        Returns:
            bool
        """
        url = self._get_latest_url(f"issue/{issue}/assignee")
        payload = {"name": assignee}
        r = self._session.put(url, data=json.dumps(payload))
        raise_on_error(r)
        return True
    
    def _get_latest_url(self, path: str, base: str = JIRA.JIRA_BASE_URL) -> str:
        """Returns the full url based on Jira base url and the path provided.
        Using the latest API endpoint.

        Args:
            path (str): The subpath desired.
            base (Optional[str]): The base url which should be prepended to the path

        Returns:
            str: Fully qualified URL
        """
        options = self._options.copy()
        options.update({"path": path, "rest_api_version": "2"})
        return base.format(**options)

    
