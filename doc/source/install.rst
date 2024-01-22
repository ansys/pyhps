.. _installation:

Installation
============

Make sure you have ``Python 3`` and that the expected version is available from your command line. You can check this by running:

.. code:: 

    python --version

If you do not have Python, please install the latest 3.x version from `python.org <https://python.org>`_.

Additionally, make sure you have ``pip`` available. You can check this by running:

.. code:: 

    pip --version

If pip isn't already installed, please refer to the `Installing Packages Tutorial <https://packaging.python.org/tutorials/installing-packages/>`_ from the Python Packaging Authority.


As long as PyHPS is a private PyAnsys package not published to PyPI yet, you can execute

.. code:: 

    python -m pip install git+https://github.com/ansys-internal/pyhps

The following dependencies are automatically installed through ``pip`` (if not already available):

- requests_
- marshmallow_
- marshmallow_oneofschema_
- python-keycloak_
- pydantic_

.. _requests: https://pypi.org/project/requests/
.. _marshmallow: https://pypi.org/project/marshmallow/
.. _marshmallow_oneofschema: https://pypi.org/project/marshmallow-oneofschema/
.. _cachetools: https://pypi.org/project/cachetools/
.. _python-keycloak: https://pypi.org/project/python-keycloak/
.. _pydantic: https://pypi.org/project/pydantic/
