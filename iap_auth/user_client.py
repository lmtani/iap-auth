import json
import logging
from typing import Optional

import requests

from .user.auth import UserAuth
from .user.entities import Token


class UserIapClient:
    oauth2_token_endpoint = "https://oauth2.googleapis.com/token"
    _access_token: Optional[Token] = None

    def __init__(self, desktop_oauth_id: str, desktop_oauth_secret: str, target_audience: str, credentials: str):
        self._desktop_oauth_id = desktop_oauth_id
        self._desktop_oauth_secret = desktop_oauth_secret
        self._target_audience = target_audience
        self._store_path = credentials

    def make_iap_request(self, url, method="GET", **kwargs):
        auth = UserAuth(self._desktop_oauth_id, self._desktop_oauth_secret, self._store_path)
        user_credentials = auth.obtain_user_credentials()
        access_token = self._get_id_token_for_target_audience(user_credentials.refresh_token, self._target_audience)
        return self.http_request(
            method, url, headers={"Authorization": "Bearer {}".format(access_token.id_token)}, **kwargs
        )

    def _get_id_token_for_target_audience(self, refresh_token: str, audience: str):
        if self._access_token and self._access_token.is_token_valid():
            return self._access_token

        logging.debug("Getting id_token for requested audience.")
        data = self._prepare_request_body(refresh_token, audience)
        resp = self.http_request(
            "POST", self.oauth2_token_endpoint, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        self._access_token = Token.from_dict(resp.json())
        return self._access_token

    def _prepare_request_body(self, refresh_token, audience):
        return dict(
            client_id=self._desktop_oauth_id,
            client_secret=self._desktop_oauth_secret,
            refresh_token=refresh_token,
            grant_type="refresh_token",
            audience=audience,
        )

    @staticmethod
    def http_request(method, url, **kwargs):
        return requests.request(method, url, **kwargs)
