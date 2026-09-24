hps-mini
========

The hps-mini helpers discover a local hps-mini executable, query its connection
status, and create a :class:`ansys.hps.client.Client` connected to it.

Discovery checks an explicitly supplied path, the ``HPS_MINI_PATH`` environment
variable, the current directory, the ``binaries`` directory, and finally the
system ``PATH``. Set ``HPS_MINI_DATA_DIR`` to use a specific mini data directory.

.. module:: ansys.hps.client.mini

.. autosummary::
   :toctree: _autosummary

   HpsMini
   HpsMiniStatus
   HpsMiniError
   find_hps_mini
   get_hps_mini_status
   create_mini_client
