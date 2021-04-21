from pytest import fixture

from iap_auth.user_client import UserIapClient, UserAuth


@fixture(name="user_auth", scope="function")
def _user_auth() -> UserAuth:
    fake_oauth_id = "this-is-oauth_client_id"
    fake_oauth_secret = "this-is-oauth_client_secret"
    credentials_path = "./credentials.json"
    return UserAuth(fake_oauth_id, fake_oauth_secret, credentials_path)


@fixture()
def user_iap_client(user_auth) -> UserIapClient:
    fake_audience = "to-this-audience"
    return UserIapClient(user_auth, fake_audience)
