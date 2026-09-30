.. _example_hps_mini:

Connect to hps-mini
===================

This short example creates a PyHPS client from a locally discoverable hps-mini
instance. See the User Guide section :ref:`user_guide` for discovery options
and environment variables.

.. code-block:: python

    from ansys.hps.client import create_mini_client

    client = create_mini_client()
    print(client.url)
