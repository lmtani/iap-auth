import json
import logging
import webbrowser
from pathlib import Path

import requests
from .entities import UserCredentials


class UserAuth:
    """
    For more details:
        https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_desktop_app
    """

    oauth2_token_endpoint = "https://oauth2.googleapis.com/token"
    _user_credentials = None

    def __init__(self, desktop_oauth_id, desktop_oauth_secret, credentials):
        self._desktop_oauth_id = desktop_oauth_id
        self._desktop_oauth_secret = desktop_oauth_secret
        self._store_path = credentials

    def obtain_user_credentials(self) -> UserCredentials:
        if Path(self._store_path).is_file():
            return self._load_stored_credentials()
        else:
            return self._ask_user_to_login()

    def _load_stored_credentials(self):
        with open(self._store_path) as fh:
            return UserCredentials(**json.load(fh))

    def _ask_user_to_login(self):
        code = self._ask_for_authorization_code()
        user_credentials = self._get_credentials(code)
        self._store_user_credentials(user_credentials)
        return UserCredentials(**user_credentials)

    def _ask_for_authorization_code(self) -> str:
        logging.debug("Getting authorization code.")
        resource = "https://accounts.google.com/o/oauth2/v2/auth"
        default_params = (
            "&response_type=code&scope=openid%20email&access_type=offline&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        )

        url = f"{resource}?client_id={self._desktop_oauth_id}{default_params}"
        webbrowser.open_new(url)
        code = input("Please, login with your Google Account and paste here your authorization code: ")
        return code

    def _get_credentials(self, code: str):
        logging.debug("Getting user credentials.")
        data = dict(
            client_id=self._desktop_oauth_id,
            client_secret=self._desktop_oauth_secret,
            code=code,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            grant_type="authorization_code",
        )
        resp = self.http_request(
            "POST", self.oauth2_token_endpoint, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()

    def _store_user_credentials(self, user_credentials):
        with open(self._store_path, "w") as fh:
            json.dump(user_credentials, fh, indent=4)
        logging.info("User credentials stored at '%s'", self._store_path)

    @staticmethod
    def http_request(method, url, **kwargs):
        return requests.request(method, url, **kwargs)
