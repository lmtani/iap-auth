from setuptools import setup

setup(
    name='iap-auth',
    version='0.0.1',
    description='Perform authentication for Google Cloud Identity Aware Proxy from a service account',
    url='git@github.com:lmtani/iap-auth.git',
    author='Lucas Taniguti',
    author_email='ltaniguti@gmail.com',
    license='unlicense',
    packages=['iap_auth'],
    install_requires=['requests_toolbelt', 'google-auth-oauthlib'],
    zip_safe=False
)
