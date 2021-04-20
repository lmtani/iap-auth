import json
import logging
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests


@dataclass
class Token:
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    expires_at: float

    @staticmethod
    def from_dict(data: dict):
        at = data["expires_in"] + datetime.now().timestamp()
        return Token(**data, expires_at=at)

    def is_token_valid(self):
        if self.expires_at > datetime.now().timestamp():
            return True
        return False


@dataclass
class UserCredentials:
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
    id_token: str

    @staticmethod
    def from_dict(data: dict):
        at = data["expires_in"] + datetime.now().timestamp()
        return Token(**data, expires_at=at)

    def is_token_valid(self):
        if self.expires_at > datetime.now().timestamp():
            return True
        return False


def http_request(method, url, **kwargs):
    return requests.request(method, url, **kwargs)


class UserAuth:
    """
    For more details:
        https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_desktop_app
    """

    oauth2_token_endpoint = "https://oauth2.googleapis.com/token"
    user_credentials = None

    def __init__(self, desktop_oauth_id, desktop_oauth_secret, credentials):
        self.desktop_oauth_id = desktop_oauth_id
        self.desktop_oauth_secret = desktop_oauth_secret
        self.store_path = credentials

    def obtain_user_credentials(self) -> UserCredentials:
        if Path(self.store_path).is_file():
            return self._load_stored_credentials()
        else:
            return self._ask_user_to_login()

    def _load_stored_credentials(self):
        with open(self.store_path) as fh:
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

        url = f"{resource}?client_id={self.desktop_oauth_id}{default_params}"
        webbrowser.open_new(url)
        code = input("Please, login with your Google Account and paste here your authorization code: ")
        return code

    def _get_credentials(self, code: str):
        logging.debug("Getting user credentials.")
        data = dict(
            client_id=self.desktop_oauth_id,
            client_secret=self.desktop_oauth_secret,
            code=code,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            grant_type="authorization_code",
        )
        resp = http_request(
            "POST", self.oauth2_token_endpoint, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()

    def _store_user_credentials(self, user_credentials):
        with open(self.store_path, "w") as fh:
            json.dump(user_credentials, fh, indent=4)
        logging.info("User credentials stored at '%s'", self.store_path)


class UserIapClient:
    oauth2_token_endpoint = "https://oauth2.googleapis.com/token"
    _access_token: Optional[Token] = None

    def __init__(self, user_auth: UserAuth, target_audience: str):
        self._user_auth = user_auth
        self._target_audience = target_audience

    def make_iap_request(self, url, method="GET", **kwargs):
        user_credentials = self._user_auth.obtain_user_credentials()
        access_token = self._get_id_token_for_target_audience(user_credentials.refresh_token, self._target_audience)
        return http_request(
            method, url, headers={"Authorization": "Bearer {}".format(access_token.id_token)}, **kwargs
        )

    def _get_id_token_for_target_audience(self, refresh_token: str, audience: str):
        if self._access_token and self._access_token.is_token_valid():
            return self._access_token

        logging.debug("Getting id_token for requested audience.")
        data = self._prepare_request_body(refresh_token, audience)
        resp = http_request(
            "POST", self.oauth2_token_endpoint, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        self._access_token = Token.from_dict(resp.json())
        return self._access_token

    def _prepare_request_body(self, refresh_token, audience):
        return dict(
            client_id=self._user_auth.desktop_oauth_id,
            client_secret=self._user_auth.desktop_oauth_secret,
            refresh_token=refresh_token,
            grant_type="refresh_token",
            audience=audience,
        )
