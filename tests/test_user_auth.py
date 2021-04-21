from datetime import datetime
from pathlib import Path
from unittest import mock

from pytest import MonkeyPatch

from iap_auth.user_client import Token, UserAuth, UserCredentials, UserIapClient


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


@mock.patch("requests.request")
@mock.patch.object(Path, "is_file", return_value=True)
def test_user_auth_should_negotiate_new_token_if_existing_one_is_expired(
    path_mock, requests, user_iap_client: UserIapClient, user_auth: UserAuth, monkeypatch: MonkeyPatch
):
    # Setup
    monkeypatch.setattr(
        user_auth,
        "_load_stored_credentials",
        lambda: UserCredentials(
            access_token="aaaasss",
            scope="iam",
            token_type="refresh",
            refresh_token="aaaa",
            expires_in=600,
            id_token="bbbb",
        ),
    )

    monkeypatch.setattr(
        user_iap_client,
        "_access_token",
        Token(
            id_token="id-token-aaaaaaaaaaaa",
            token_type="Bearer",
            access_token="access-token-aaaa",
            expires_in=600,
            expires_at=datetime.now().timestamp() - 50,
            scope="iam",
        ),
    )

    json_data = {
        "access_token": "not-used-in-iap",
        "expires_in": 10,
        "scope": "iam",
        "token_type": "Bearer",
        "id_token": "user-token",
    }
    requests.return_value = MockResponse(json_data, 200)

    # Call
    user_iap_client.make_iap_request("https://google.com.br")

    # Assert
    expected_id_token_for_audience_call = mock.call('POST', 'https://oauth2.googleapis.com/token', data='{"client_id": "this-is-oauth_client_id", "client_secret": "this-is-oauth_client_secret", "refresh_token": "aaaa", "grant_type": "refresh_token", "audience": "to-this-audience"}', headers={'Content-Type': 'application/json'})
    expected_iap_protected_resource_call = mock.call(
        "GET", "https://google.com.br", headers={"Authorization": "Bearer user-token"}
    )
    calls = [expected_id_token_for_audience_call, expected_iap_protected_resource_call]
    requests.assert_has_calls(calls, any_order=False)


@mock.patch("builtins.input", return_value="user/authorization-code")
@mock.patch("webbrowser.open_new")
@mock.patch("requests.request")
@mock.patch.object(Path, "is_file", return_value=False)
def test_user_auth_should_ask_for_user_credentials_if_no_one_found_in_path(
    path_mock,
    requests,
    webbrowser,
    input_mock,
    user_iap_client: UserIapClient,
    user_auth: UserAuth,
    monkeypatch: MonkeyPatch,
):
    # Setup

    json_data1 = {
        "access_token": "not-used-in-iap",
        "expires_in": 600,
        "scope": "iam",
        "token_type": "refresh",
        "refresh_token": "this-allows-reuse-this-credential",
        "id_token": "user-token",
    }
    json_data2 = {
        "access_token": "not-used-in-iap",
        "expires_in": 600,
        "scope": "iam",
        "token_type": "Bearer",
        "id_token": "user-token2",
    }
    desired_return = {"resp": "google.com.br-response"}
    requests.side_effect = [
        MockResponse(json_data1, 200),
        MockResponse(json_data2, 200),
        MockResponse(desired_return, 200),
    ]

    # Call
    user_iap_client.make_iap_request("https://google.com.br")

    # Assert
    expected_authorization_call = mock.call(
        "POST",
        "https://oauth2.googleapis.com/token",
        data='{"client_id": "this-is-oauth_client_id", "client_secret": "this-is-oauth_client_secret", "code": "user/authorization-code", "redirect_uri": "urn:ietf:wg:oauth:2.0:oob", "grant_type": "authorization_code"}',
        headers={"Content-Type": "application/json"},
    )
    expected_id_token_for_audience_call = mock.call(
        "POST",
        "https://oauth2.googleapis.com/token",
        data='{"client_id": "this-is-oauth_client_id", "client_secret": "this-is-oauth_client_secret", "refresh_token": "this-allows-reuse-this-credential", "grant_type": "refresh_token", "audience": "to-this-audience"}',
        headers={"Content-Type": "application/json"},
    )
    expected_iap_protected_resource_call = mock.call(
        "GET", "https://google.com.br", headers={"Authorization": "Bearer user-token2"}
    )
    calls = [expected_authorization_call, expected_id_token_for_audience_call, expected_iap_protected_resource_call]

    requests.assert_has_calls(calls, any_order=False)
