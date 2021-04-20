# Google IAP authentication ![Upload Python Package](https://github.com/lmtani/iap-auth/workflows/Upload%20Python%20Package/badge.svg?branch=master)

This module contains a helper class to make requests to an app running behind a Google Identity-Aware Proxy. The code was obtained from the Google [Programmatic authentication](https://cloud.google.com/iap/docs/authentication-howto#iap_make_request-python) document.


### Install

```bash
pip install iap-auth
```

### Usage

#### With application default credentials

If running outside Google Cloud Platform you need to specify env var GOOGLE_APPLICATION_CREDENTIALS to point to your authorized service account.

```python
from iap_auth import IapClient

CLIENT_ID = '<your-project-client-id>.apps.googleusercontent.com'
URL = 'https://your-iap-protected-website.com.br'
METHOD = 'GET'
kwargs = {}

client = IapClient(CLIENT_ID)
resp = client.make_iap_request(URL, method=METHOD, **kwargs)

# resp is a requests.Response object.
```

#### Authenticating a user account

This way users do not need to have a service account or Google SDK installed. You'll need to [create an OAuth 2.0 client ID](https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_desktop_app) and then use this lib as follows:

```python
from iap_auth.user_client import UserAuth, UserIapClient

OAUTH_ID = "<desktop-app-oauth-id>.googleusercontent.com"
OAUTH_SECRET = "z6..desktop-app-oauth-secret..Ys1"
KEY_PATH = "/where/to/store/your/user-credentials.json"
IAP_OAUTH_ID = '<your-project-iap-client-id>.apps.googleusercontent.com'

URL = 'https://your-iap-protected-website.com.br'

user_auth = UserAuth(OAUTH_ID, OAUTH_SECRET, KEY_PATH)
client = UserIapClient(user_auth, IAP_OAUTH_ID)
resp = client.make_iap_request(URL, method=METHOD)

# resp is a requests.Response object.
```
