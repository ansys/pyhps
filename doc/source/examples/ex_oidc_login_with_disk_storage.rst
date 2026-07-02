.. _example_oidc_login_with_disk_storage:

OIDC Login with Disk Storage
=============================

This example demonstrates how to save OIDC tokens to disk with platform-specific security.

Storage locations:

- **Windows**: ``%USERPROFILE%\.ansys\hps_tokens.json`` (encrypted with DPAPI)
- **Unix/Linux**: ``~/.ansys/hps_tokens.json`` (file permissions 0o600)

Code
----

.. literalinclude:: ../../examples/oidc/login_with_disk_storage.py
   :language: python

Usage
-----

Run the example::

    cd examples/oidc
    python login_with_disk_storage.py

Output::

    Tokens saved to: C:\Users\username\.ansys\hps_tokens.json
    Token Expires In: 3600 seconds

Security
--------

Windows
~~~~~~~

On Windows, tokens are encrypted using DPAPI (Data Protection API), which provides user-scoped encryption.
The encrypted file is only readable by the user who encrypted it on the same computer.

Unix/Linux
~~~~~~~~~~

On Unix/Linux systems, the token file is created with restrictive permissions (0o600),
readable and writable only by the owner.

Notes
-----

- Tokens persist across script invocations
- Automatically loaded by :func:`ansys.hps.client.auth.api.oidc_login.load_tokens`
- For higher security, use :ref:`example_oidc_login_with_keyring` instead
