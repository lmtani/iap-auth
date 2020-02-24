# Google IAP authentication ![Upload Python Package](https://github.com/lmtani/iap-auth/workflows/Upload%20Python%20Package/badge.svg?branch=master)

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
CLIENT_ID = '<your-project-client-id.apps.googleusercontent.com'
URL = 'https://your-iap-protected-website.com.br'
METHOD = 'GET'
kwargs = {}

cli = IapClient(OAUTH_TOKEN_URI, IAM_SCOPE)
resp = cli.make_iap_request(URL, CLIENT_ID, method=METHOD, **kwargs)

# resp is a requests.Response object.
```

> If running outside Google Cloud Platform you need to specify env var GOOGLE_APPLICATION_CREDENTIALS to point to your authorized service account.
