import requests
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2 import id_token

from .util import is_token_valid


class IapClient:
    """
    Helper to make requests to applications behind a IAP. This class requires
    a Service Account from GCP environment or pointing a secret.json using
    GOOGLE_APPLICATION_CREDENTIALS environment variable.

    For more details:
        https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_service_account

    Args:
        oauth_id: Oauth server client id.
    """
    decoded_token: Dict[str, Any] = {}

    def __init__(self, oauth_id):
        self._oauth_id = oauth_id
        self._iap_token = None

    def make_iap_request(self, url, method="GET", **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 90

        if not is_token_valid(self.decoded_token.get("exp")):
            self._iap_token = id_token.fetch_id_token(Request(), self._oauth_id)
            self.decoded_token = id_token.verify_oauth2_token(self._iap_token, Request(), self._oauth_id)

        return requests.request(method, url, headers={"Authorization": "Bearer {}".format(self._iap_token)}, **kwargs)
