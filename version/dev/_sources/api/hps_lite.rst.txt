hps-lite
========

The hps-lite helpers discover a local hps-lite executable, query its connection
status, and create a :class:`ansys.hps.client.Client` connected to it.

Discovery checks an explicitly supplied path, the ``HPS_LITE_PATH`` environment
variable, the current directory, the ``binaries`` directory, and finally the
system ``PATH``. Set ``HPS_LITE_DATA_DIR`` to use a specific hps_lite data directory.

.. module:: ansys.hps.client.hps_lite

.. autosummary::
   :toctree: _autosummary

   HpsLite
   HpsLiteStatus
   HpsLiteError
   find_hps_lite
   get_hps_lite_status
   create_hps_lite_client
