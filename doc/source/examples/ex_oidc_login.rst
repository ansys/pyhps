.. _example_oidc_login:

OIDC Authentication Examples
============================

This section demonstrates various approaches to OIDC (OpenID Connect) authentication
using the Authorization Code + PKCE flow with different token storage strategies.

.. contents::
   :local:
   :depth: 2

Basic OIDC Login
----------------

Demonstrates how to perform a basic OIDC login. Tokens are kept in memory only and
are not persisted.

The login process:

1. Opens your default browser to the OIDC provider's login page
2. You authenticate with your credentials
3. Redirects back with an authorization code
4. Exchanges the code for tokens
5. Tokens are kept in memory only (not persisted)

Code
~~~~

.. literalinclude:: ../../examples/oidc/basic_login.py
   :language: python

Usage
~~~~~

Run the example::

    cd examples/oidc
    python basic_login.py

Output::

    Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI...
    Token Expires In: 3600 seconds

Notes
~~~~~

- Tokens are kept in memory only and are not persisted to disk
- The token will be lost when the script exits
- For persistent storage, see the examples below


OIDC Login with System Keyring Storage
--------------------------------------

Demonstrates how to save OIDC tokens to the system credential manager for secure,
persistent storage. This is the **recommended storage method** for security.

The system credential manager varies by platform:

- **Windows**: Credential Manager
- **macOS**: Keychain
- **Linux**: Secret Service (via python-keyring)

Code
~~~~

.. literalinclude:: ../../examples/oidc/login_with_keyring.py
   :language: python

Prerequisites
~~~~~~~~~~~~~

Install the keyring package::

    pip install keyring

Usage
~~~~~

Run the example::

    cd examples/oidc
    python login_with_keyring.py

Output::

    Tokens saved to system keyring
    Token Expires In: 3600 seconds

Security Benefits
~~~~~~~~~~~~~~~~~

- Tokens are encrypted at rest in the system credential manager
- Credentials are managed by the operating system
- No plaintext files on disk
- Automatic cleanup when user logs out (on some systems)

Notes
~~~~~

- Requires the ``keyring`` package
- Falls back to disk storage if keyring is unavailable
- Tokens are automatically loaded from keyring by :func:`ansys.hps.client.auth.api.oidc_login.load_tokens`


OIDC Login with Disk Storage
----------------------------

Demonstrates how to save OIDC tokens to disk with platform-specific security.

Storage locations:

- **Windows**: ``%USERPROFILE%\.ansys\hps_tokens.json`` (encrypted with DPAPI)
- **Unix/Linux**: ``~/.ansys/hps_tokens.json`` (file permissions 0o600)

Code
~~~~

.. literalinclude:: ../../examples/oidc/login_with_disk_storage.py
   :language: python

Usage
~~~~~

Run the example::

    cd examples/oidc
    python login_with_disk_storage.py

Output::

    Tokens saved to: C:\Users\username\.ansys\hps_tokens.json
    Token Expires In: 3600 seconds

Security
~~~~~~~~

Windows
^^^^^^^

On Windows, tokens are encrypted using DPAPI (Data Protection API), which provides
user-scoped encryption. The encrypted file is only readable by the user who encrypted
it on the same computer.

Unix/Linux
^^^^^^^^^^

On Unix/Linux systems, the token file is created with restrictive permissions (0o600),
readable and writable only by the owner.

Notes
~~~~~

- Tokens persist across script invocations
- Automatically loaded by :func:`ansys.hps.client.auth.api.oidc_login.load_tokens`
- For higher security, use keyring storage instead


Load and Use Saved Tokens
-------------------------

Demonstrates how to load previously saved tokens and use them in API calls.

Tokens can be loaded from:

1. System keyring (if available and tokens were saved there)
2. Disk storage (if tokens were saved to disk)

Code
~~~~

.. literalinclude:: ../../examples/oidc/load_saved_tokens.py
   :language: python

Usage
~~~~~

First, save tokens using one of the login examples above. Then run this example::

    cd examples/oidc
    python load_saved_tokens.py

Output::

    Loaded tokens for: https://localhost:8443/hps
    Token is valid
    Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI...

Features
~~~~~~~~

- Automatically tries keyring first, then falls back to disk storage
- Checks token expiration with configurable buffer (default 60 seconds)
- Provides access token for use in API calls

Error Handling
~~~~~~~~~~~~~~

If no saved tokens are found, you'll see::

    No saved tokens found. Please run login first.

If tokens are expired or expiring soon::

    Token is expired or expiring soon. Please refresh.

In this case, see the token refresh example below.

Notes
~~~~~

- Tokens are automatically discovered from storage without configuration
- The buffer parameter (default 60s) provides a safety margin before expiration
- Use the ``Authorization`` header with the access token in API requests


Refresh OIDC Tokens
------------------

Demonstrates how to refresh tokens using the refresh_token grant. This allows you to
obtain a new access token without requiring user re-authentication.

The refresh token flow is useful when the access token expires but the refresh token
is still valid.

Code
~~~~

.. literalinclude:: ../../examples/oidc/refresh_tokens_example.py
   :language: python

Prerequisites
~~~~~~~~~~~~~

You must have previously saved tokens using one of the login examples above.

Usage
~~~~~

Run the example::

    cd examples/oidc
    python refresh_tokens_example.py

Output::

    Refreshing tokens...
    New tokens saved to system keyring
    New token expires in: 3600 seconds
    New refresh token expires in: 86400 seconds

Workflow
~~~~~~~~

1. Loads current tokens from storage (keyring or disk)
2. Uses the refresh_token to obtain new tokens without user interaction
3. Saves the new tokens back to the same storage location

This allows your application to:

- Automatically refresh tokens when they expire
- Keep the refresh token synchronized across invocations
- Maintain a valid access token for API calls

Error Handling
~~~~~~~~~~~~~~

If no saved tokens are found::

    No saved tokens found. Please run login first.

If refresh fails (e.g., refresh token expired)::

    Token refresh failed. You may need to login again.

Automation
~~~~~~~~~~

To automatically refresh tokens when needed, combine token expiration checking with
refresh:

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
~~~~~

- Refresh tokens typically have a longer expiration time than access tokens
- If both access and refresh tokens expire, you must login again
- Always save refreshed tokens back to storage for consistency
