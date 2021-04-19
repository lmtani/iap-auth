from unittest import mock
from iap_auth import UserAuth


def test_user_auth_should_authenticate_if_no_user_credential_found(mocker):
    fake_oauth_id = ""
    fake_oauth_secret = ""
    fake_audience = ""
    credentials_path = "./credentials.json"
    mocker.patch.object(UserAuth, "_obtain_user_credentials")

    client = UserAuth(fake_oauth_id, fake_oauth_secret, fake_audience, credentials_path)
    client._user_credentials = "a"

    assert 1 == 2
