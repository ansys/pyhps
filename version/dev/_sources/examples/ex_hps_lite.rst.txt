.. _example_hps_lite:

Connect to hps-lite
===================

This short example creates a PyHPS client from a locally discoverable hps-lite
instance. See the User Guide section :ref:`user_guide` for discovery options
and environment variables.

.. code-block:: python

    from ansys.hps.client import create_hps_lite_client

    client = create_hps_lite_client()
    print(client.url)
