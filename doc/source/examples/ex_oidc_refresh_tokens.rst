.. _example_oidc_refresh_tokens:

Refresh OIDC Tokens
===================

This example demonstrates how to refresh tokens using the refresh_token grant.

The refresh token flow allows you to obtain a new access token without requiring
user re-authentication. This is useful when the access token expires but the refresh
token is still valid.

Code
----

.. literalinclude:: ../../examples/oidc/refresh_tokens_example.py
   :language: python

Prerequisites
--------------

You must have previously saved tokens using one of:

- :ref:`example_oidc_login_with_keyring`
- :ref:`example_oidc_login_with_disk_storage`

Usage
-----

Run the example::

    cd examples/oidc
    python refresh_tokens_example.py

Output::

    Refreshing tokens...
    New tokens saved to system keyring
    New token expires in: 3600 seconds
    New refresh token expires in: 86400 seconds

Workflow
--------

1. Loads current tokens from storage (keyring or disk)
2. Uses the refresh_token to obtain new tokens without user interaction
3. Saves the new tokens back to the same storage location

This allows your application to:

- Automatically refresh tokens when they expire
- Keep the refresh token synchronized across invocations
- Maintain a valid access token for API calls

Error Handling
--------------

If no saved tokens are found::

    No saved tokens found. Please run login first.

If refresh fails (e.g., refresh token expired)::

    Token refresh failed. You may need to login again.

Automation
----------

To automatically refresh tokens when needed, combine this with token expiration checking:

.. code-block:: python

    from ansys.hps.client.auth.api.oidc_login import (
        load_tokens,
        _is_token_expired,
        refresh_tokens,
        save_tokens
    )

    tokens = load_tokens()
    if tokens and _is_token_expired(tokens, buffer_seconds=300):
        # Refresh if expiring in next 5 minutes
        new_tokens = refresh_tokens()
        if new_tokens:
            save_tokens(new_tokens, new_tokens.get("hps_url"), storage="keyring")

Notes
-----

- Refresh tokens typically have a longer expiration time than access tokens
- If both access and refresh tokens expire, you must login again
- Always save refreshed tokens back to storage for consistency
