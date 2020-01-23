import requests
import google.auth
import google.auth.iam
import google.auth.app_engine
import google.oauth2.credentials
import google.oauth2.service_account
import requests_toolbelt.adapters.appengine
import google.auth.compute_engine.credentials
from google.auth.transport.requests import Request


class IapClient:
    """
    Helper to make requests to applications behind a IAP.

    Args:
    oauth_token_uri: Google Token endpoint.
    iam_scope: Google scope required (iam)
    """

    def __init__(self, oauth_token_uri, iam_scope):
        self.OAUTH_TOKEN_URI = oauth_token_uri
        self.IAM_SCOPE = iam_scope

    def make_iap_request(self, url, client_id, method="GET", **kwargs):
        """Makes a request to an application protected by Identity-Aware Proxy.

        Args:
        url: The Identity-Aware Proxy-protected URL to fetch.
        client_id: The client ID used by Identity-Aware Proxy.
        method: The request method to use
                ('GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE')
        **kwargs: Any of the parameters defined for the request function:
                    https://github.com/requests/requests/blob/master/requests/api.py
                    If no timeout is provided, it is set to 90 by default.

        Returns:
        The page body, or raises an exception if the page couldn't be retrieved.
        """
        if "timeout" not in kwargs:
            kwargs["timeout"] = 90

        bootstrap_credentials, _ = google.auth.default(scopes=[self.IAM_SCOPE])

        if isinstance(bootstrap_credentials, google.oauth2.credentials.Credentials):
            raise Exception("make_iap_request is only supported for service " "accounts.")
        elif isinstance(bootstrap_credentials, google.auth.app_engine.Credentials):
            requests_toolbelt.adapters.appengine.monkeypatch()

        bootstrap_credentials.refresh(Request())
        signer_email = bootstrap_credentials.service_account_email
        if isinstance(bootstrap_credentials, google.auth.compute_engine.credentials.Credentials):
            signer = google.auth.iam.Signer(Request(), bootstrap_credentials, signer_email)
        else:
            signer = bootstrap_credentials.signer

        service_account_credentials = google.oauth2.service_account.Credentials(
            signer, signer_email, token_uri=self.OAUTH_TOKEN_URI, additional_claims={"target_audience": client_id}
        )

        google_open_id_connect_token = self._get_google_open_id_connect_token(service_account_credentials)

        resp = requests.request(
            method, url, headers={"Authorization": "Bearer {}".format(google_open_id_connect_token)}, **kwargs
        )
        if resp.status_code == 403:
            raise Exception(
                "Service account {} does not have permission to "
                "access the IAP-protected application.".format(signer_email)
            )
        elif resp.status_code != 200:
            raise Exception(
                "Bad response from application: {!r} / {!r} / {!r}".format(resp.status_code, resp.headers, resp.text)
            )
        else:
            return resp

    def _get_google_open_id_connect_token(self, service_account_credentials):
        service_account_jwt = service_account_credentials._make_authorization_grant_assertion()
        request = google.auth.transport.requests.Request()
        body = {
            "assertion": service_account_jwt,
            "grant_type": google.oauth2._client._JWT_GRANT_TYPE,
        }
        token_response = google.oauth2._client._token_endpoint_request(request, self.OAUTH_TOKEN_URI, body)

        return token_response["id_token"]
