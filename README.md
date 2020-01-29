# Google IAP authentication

This module contains a helper class to make requests to an app running behind a Google Identity-Aware Proxy. The code was obtained from the Google [Programmatic authentication](https://cloud.google.com/iap/docs/authentication-howto#iap_make_request-python) document.


### Install

```bash
pip install iap-auth
```

### Usage

```python
from iap_auth import IapClient

IAM_SCOPE = 'https://www.googleapis.com/auth/iam'
OAUTH_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'

cli = IapClient(OAUTH_TOKEN_URI, IAM_SCOPE)
resp = cli.make_iap_request(url, self.client_id, method=method, **kwargs)

# resp is a requests.Response object.
```

> If running outside Google Cloud Platform you need to specify env var GOOGLE_APPLICATION_CREDENTIALS to point to your authorized service account.
