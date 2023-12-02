from datetime import datetime

import jwt
from docusign_esign import ApiClient

DS_KEY = "dca430d2-61d3-4e00-b032-9776a2c7e05b"
DS_ACCOUNT_ID = "b8d3ee4c-f351-4cb9-8d70-8adc612a8139"
DS_SECRET = "6d5d6f4c-7457-4780-bd18-6accf9ffe539"
DS_TENANT_ID = "9d18e6e9-230c-4d30-84f0-11a7f1737fcf"
DS_PRIVATE_KEY_PATH = "/Users/lakhdar.benamer/pet-adopt/private.key"
DS_OAUTH_SERVER = "account-d.docusign.com"


class EmptyClientAccounts(Exception):
    pass


class DocuSign:
    def __init__(self):
        self.auth_client = self.get_auth_client()
        self.token = self.get_jwt()
        self.account = self.get_account(self.token)
        self.account_id = self.account.account_id
        self.base_path = self.account.base_uri + "/restapi"
        print(self.base_path, self.account_id)

    @property
    def api_client(self):
        api_client = ApiClient()
        api_client.host = self.base_path
        api_client.set_default_header(
            header_name="Authorization", header_value=f"Bearer {self.token}"
        )
        return api_client

    @property
    def _private_key(self):
        with open(DS_PRIVATE_KEY_PATH) as f:
            return f.read().encode("ascii").decode("utf-8")

    def get_account(self, token):
        try:
            user_info = self.auth_client.get_user_info(token)
            return user_info.get_accounts()[0]
        except IndexError:
            EmptyClientAccounts("Failed to retreive docusign account")

    def get_jwt(self):
        response = self.auth_client.request_jwt_user_token(
            client_id=DS_KEY,
            user_id=DS_TENANT_ID,
            oauth_host_name=DS_OAUTH_SERVER,
            private_key_bytes=self._private_key,
            expires_in=3600,
            scopes=["signature", "impersonation"],
        )
        return response.access_token

    def get_auth_client(self):
        auth_client = ApiClient()
        auth_client.set_base_path(DS_OAUTH_SERVER)
        auth_client.set_oauth_host_name(DS_OAUTH_SERVER)
        return auth_client
