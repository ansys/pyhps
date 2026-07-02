.. _example_oidc_login_with_keyring:

OIDC Login with System Keyring Storage
=======================================

This example demonstrates how to save OIDC tokens to the system credential manager
for secure, persistent storage.

The system credential manager varies by platform:

- **Windows**: Credential Manager
- **macOS**: Keychain
- **Linux**: Secret Service (via python-keyring)

This is the recommended storage method for security.

Code
----

.. literalinclude:: ../../examples/oidc/login_with_keyring.py
   :language: python

Prerequisites
--------------

Install the keyring package::

    pip install keyring

Usage
-----

Run the example::

    cd examples/oidc
    python login_with_keyring.py

Output::

    Tokens saved to system keyring
    Token Expires In: 3600 seconds

Security Benefits
------------------

- Tokens are encrypted at rest in the system credential manager
- Credentials are managed by the operating system
- No plaintext files on disk
- Automatic cleanup when user logs out (on some systems)

Notes
-----

- Requires the ``keyring`` package
- Falls back to disk storage if keyring is unavailable
- Tokens are automatically loaded from keyring by :func:`ansys.hps.client.auth.api.oidc_login.load_tokens`
