from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='iap-auth',
    version='0.0.2',
    description='Perform authentication for Google Cloud Identity Aware Proxy from a service account',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/lmtani/iap-auth',
    author='Lucas Taniguti',
    author_email='ltaniguti@gmail.com',
    license='unlicense',
    packages=['iap_auth'],
    install_requires=['requests_toolbelt', 'google-auth-oauthlib'],
    zip_safe=False
)
