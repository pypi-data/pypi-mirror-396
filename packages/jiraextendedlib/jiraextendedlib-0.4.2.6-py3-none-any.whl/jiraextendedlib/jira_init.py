import requests
import os
from jira import JIRA
from .jira_extended import JIRAExtended
# from st2common.util.api import get_full_public_api_url
# from st2client.client import Client
# from st2client.models import KeyValuePair
from typing import (
    Any,
    Dict,
    Optional,
    Type
)
from jira.resources import Resource


class JiraInit():

    def __init__(self, config) -> None:
        self.auth_token = None
        self.config = config
        self._client = None

    def get_client(self, default_batch_sizes: Optional[Dict[Type[Resource], Optional[int]]] = None):
        config = self.config
        options = {'server': config['url'], 'verify': config['verify']}

        auth_method = config['auth_method']

        if auth_method == 'oauth':
            rsa_cert_file = config['rsa_cert_file']
            rsa_key_content = self._get_file_content(file_path=rsa_cert_file)

            oauth_creds = {
                'access_token': config['oauth_token'],
                'access_token_secret': config['oauth_secret'],
                'consumer_key': config['consumer_key'],
                'key_cert': rsa_key_content
            }

            client = JIRA(options=options, oauth=oauth_creds)

        elif auth_method == 'basic':
            basic_creds = (config['username'], config['password'])
            client = JIRA(options=options, basic_auth=basic_creds,
                          validate=config.get('validate', False))

        elif auth_method == 'token':
            basic_creds = (config['token'])
            client = JIRA(options=options, token_auth=basic_creds,
                          validate=config.get('validate', False))

        elif auth_method == 'cookie':
            basic_creds = (config['username'], config['password'])
            client = JIRA(options=options, auth=basic_creds)

        elif auth_method == 'ipass':
            client = JIRAExtended(options=options,
                                  token=self._get_ims_token(store_token=False),
                                  personal_access_token=config['personal_access_token'],
                                  api_key=config['ipass_key'],
                                  validate=config.get('validate', False),
                                  default_batch_sizes=default_batch_sizes
                                  )

        else:
            msg = ('You must set auth_method to either "oauth", ',
                   '"basic", or "cookie" in your Jira pack config file.')
            raise Exception(msg)

        self._client = client
        return client

    def _get_ims_token(self, new_token=False, store_token=False):
        """Get the cloud API token
        Args:
            new_token (boolean): Need to get a new token
        Returns:
            Any: String, the token
        """
        st2_client = None
        if store_token:
            from st2common.util.api import get_full_public_api_url
            from st2client.client import Client

            auth_token = os.environ.get("ST2_ACTION_AUTH_TOKEN", None)
            api_url = get_full_public_api_url()
            st2_client = Client(api_url=api_url, token=auth_token)

            if not self.auth_token:
                try:
                    auth_token_kvp = st2_client.keys.get_by_name(name='ipass_auth_token')
                    if auth_token_kvp:
                        self.auth_token = auth_token_kvp.value
                except Exception as e:
                    raise Exception(
                        "Exception in retrieving value from datastore for key ipass_auth_token %s", e
                    )

        if new_token or not self.auth_token:
            config = self.config
            url = "{url}v1?grant_type=authorization_code&client_id={client_id}".format(url=config['ims_url'],
                                                                                       client_id=config[
                                                                                           'ims_client_id'])
            response = requests.post(url=url, data={'client_secret': config['ims_secret'], 'code': config['ims_code']})
            ims_response = response.json()
            if "access_token" in ims_response:
                self.auth_token = ims_response['access_token']
                if store_token:
                    from st2client.models import KeyValuePair
                    st2_client.keys.update(KeyValuePair(name='ipass_auth_token', value=self.auth_token))
            else:
                raise Exception("Ims authentication failed")
        return self.auth_token

    def reset_authentication(self, client):
        if type(client).__name__ == 'JIRAExtended':
            self._client._session.auth._token = self._get_ims_token(new_token=True, store_token=True)
