.. _example_oidc_load_saved_tokens:

Load and Use Saved Tokens
==========================

This example demonstrates how to load previously saved tokens and use them in API calls.

Tokens can be loaded from:

1. System keyring (if available and tokens were saved there)
2. Disk storage (if tokens were saved to disk)

Code
----

.. literalinclude:: ../../examples/oidc/load_saved_tokens.py
   :language: python

Usage
-----

First, save tokens using one of the login examples:

- :ref:`example_oidc_login_with_keyring`
- :ref:`example_oidc_login_with_disk_storage`

Then run this example::

    cd examples/oidc
    python load_saved_tokens.py

Output::

    Loaded tokens for: https://localhost:8443/hps
    Token is valid
    Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI...

Features
--------

- Automatically tries keyring first, then falls back to disk storage
- Checks token expiration with configurable buffer (default 60 seconds)
- Provides access token for use in API calls

Error Handling
--------------

If no saved tokens are found, you'll see::

    No saved tokens found. Please run login first.

If tokens are expired or expiring soon::

    Token is expired or expiring soon. Please refresh.

In this case, use :ref:`example_oidc_refresh_tokens` to refresh the tokens.

Notes
-----

- Tokens are automatically discovered from storage without configuration
- The buffer parameter (default 60s) provides a safety margin before expiration
- Use the ``Authorization`` header with the access token in API requests
