import json
import logging
import webbrowser
from pathlib import Path
from typing import Dict, Optional

import requests

from .util import is_token_valid


class UserAuth:
    """
    This class will open your browser to use your Google Account and then will prompt you
    to provide an authentication code. After the first login, the credential will be stored
    in your home directory as ".iap-auth-credentials.json"

    Next time you call the client it will recover the stored credential.

    For more details:
        https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_desktop_app
    """

    oauth2_token_endpoint = "https://oauth2.googleapis.com/token"

    def __init__(self, desktop_oauth_id: str, desktop_oauth_secret: str, target_audience: str):
        self._desktop_oauth_id = desktop_oauth_id
        self._desktop_oauth_secret = desktop_oauth_secret
        self._target_audience = target_audience
        self._store_path = f"{str(Path.home())}/.iap-auth-credentials.json"

        self._user_credentials = None
        self._restore_stored_user_credentials()
        if not self._user_credentials:
            self.login()
        self._token_data: Optional[Dict[str, str]] = None

    @property
    def _id_token(self) -> Optional[str]:
        if self._token_data:
            return self._token_data["id_token"]
        return None

    @property
    def _refresh_token(self) -> Optional[str]:
        if self._user_credentials:
            return self._user_credentials["refresh_token"]
        return None

    def login(self):
        code = self._get_authorization_code()
        self._get_credentials(code)
        self._store_user_credentials()

    def _get_authorization_code(self):
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
        self._user_credentials = resp.json()

    def _store_user_credentials(self):
        with open(self._store_path, "w") as fh:
            json.dump(self._user_credentials, fh, indent=4)
        logging.info("User credentials stored at '%s'", self._store_path)

    def _restore_stored_user_credentials(self):
        if Path(self._store_path).is_file():
            with open(self._store_path) as fh:
                self._user_credentials = json.load(fh)

    def _get_id_token_for_target_audience(self, audience: str):
        logging.debug("Getting id_token for requested audience.")
        data = dict(
            client_id=self._desktop_oauth_id,
            client_secret=self._desktop_oauth_secret,
            refresh_token=self._refresh_token,
            grant_type="refresh_token",
            audience=audience,
        )
        resp = self.http_request(
            "POST", self.oauth2_token_endpoint, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        self._token_data = resp.json()

    def make_iap_request(self, url, method="GET", **kwargs):
        if not self._user_credentials:
            logging.error(
                "No user credentials. You need to use `UserAuth.login()` or provide in class constructor"
                "using `credentials` parameter."
            )
        if not is_token_valid(self._id_token):
            self._get_id_token_for_target_audience(self._target_audience)

        return self.http_request(method, url, headers={"Authorization": "Bearer {}".format(self._id_token)}, **kwargs)

    @staticmethod
    def http_request(method, url, **kwargs):
        return requests.request(method, url, **kwargs)
