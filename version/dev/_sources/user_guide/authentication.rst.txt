Authentication
==============

PyHPS supports several authentication methods. Choose the method that matches
how your HPS deployment is configured.

Authentication methods
----------------------

- **Username and password**: authenticate directly against an HPS deployment
  that exposes a Keycloak service.
- **API key**: connect to a local or externally managed service using an API
  key without performing an OAuth exchange.
- **Access token**: use an access token that was obtained by another process.
- **OIDC Authorization Code + PKCE**: authenticate interactively through a
  browser and receive access and refresh tokens.

Username and password
---------------------

For an HPS deployment with username/password authentication:

.. code-block:: python

    from ansys.hps.client import Client

    client = Client(
        url="https://localhost:8443/hps",
        username="repuser",
        password="repuser",
    )

API key
-------

For a local service such as hps-lite, create a client with its API key:

.. code-block:: python

    from ansys.hps.client import Client

    client = Client(
        url="http://127.0.0.1:54143/hps",
        api_key="your-api-key",
    )

Do not print or commit API keys.

OIDC authentication
-------------------

OIDC (OpenID Connect) authentication uses the Authorization Code + PKCE flow:

1. PyHPS creates an authorization URL.
2. You authenticate with the identity provider in a browser.
3. The provider redirects back with an authorization code.
4. PyHPS exchanges the code for access and refresh tokens.
5. The access token is used for HPS API requests.
6. The refresh token can obtain a new access token later.

A basic interactive login looks like this:

.. code-block:: python

    from ansys.hps.client import Client
    from ansys.hps.client.auth.api.oidc_login import browser_login

    tokens = browser_login(
        "https://localhost:8443/hps",
        open_browser=True,
        verify_ssl=False,
    )

    client = Client(
        url=tokens["hps_url"],
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

Token storage
-------------

OIDC tokens can be kept in memory or persisted for later runs:

``memory``
    Tokens are lost when the process exits. This is convenient for short-lived
    scripts.

``keyring``
    Tokens are stored in the operating system credential manager. This is the
    recommended option for local applications. Install ``keyring`` first::

        pip install keyring

``disk``
    Tokens are stored in a local file. On Windows, DPAPI protects the token
    file; on Unix-like systems, the file is created with restrictive
    permissions.

For automatic token refresh, configure the client with the selected storage:

.. code-block:: python

    client = Client(
        url="https://localhost:8443/hps",
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_storage="keyring",
    )

Complete runnable scripts for each storage option, loading saved tokens, and
refreshing tokens are available in :ref:`example_oidc_login`.
