.. _example_oidc_basic_login:

Basic OIDC Login
================

This example demonstrates how to perform a basic OIDC login using the Authorization Code + PKCE flow.

The login process:

1. Opens your default browser to the OIDC provider's login page
2. You authenticate with your credentials
3. Redirects back with an authorization code
4. Exchanges the code for tokens
5. Tokens are kept in memory only (not persisted)

Code
----

.. literalinclude:: ../../examples/oidc/basic_login.py
   :language: python

Usage
-----

Run the example::

    cd examples/oidc
    python basic_login.py

Output::

    Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI...
    Token Expires In: 3600 seconds

Notes
-----

- Tokens are kept in memory only and are not persisted to disk
- The token will be lost when the script exits
- For persistent storage, use :ref:`example_oidc_login_with_keyring` or :ref:`example_oidc_login_with_disk_storage`
