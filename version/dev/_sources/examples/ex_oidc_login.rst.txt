.. _example_oidc_login:

OIDC Authentication Examples
============================

The User Guide explains authentication methods, the OIDC Authorization Code +
PKCE flow, and token storage choices. See :doc:`../user_guide/authentication`
before running these examples.

The scripts in ``examples/oidc`` are complete runnable examples:

Basic login
-----------

Tokens are kept in memory for the current process.

.. literalinclude:: ../../../examples/oidc/basic_login.py
   :language: python

Run it from the repository root::

    python examples/oidc/basic_login.py

Keyring storage
---------------

Stores tokens in the operating system credential manager. Install ``keyring``
first::

    pip install keyring

.. literalinclude:: ../../../examples/oidc/login_with_keyring.py
   :language: python

Disk storage
------------

Stores tokens in a local file using platform-specific protection.

.. literalinclude:: ../../../examples/oidc/login_with_disk_storage.py
   :language: python

Load saved tokens
-----------------

.. literalinclude:: ../../../examples/oidc/load_saved_tokens.py
   :language: python

Refresh tokens
--------------

.. literalinclude:: ../../../examples/oidc/refresh_tokens_example.py
   :language: python
