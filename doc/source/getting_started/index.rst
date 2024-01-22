.. _getting_started:

Getting started
===============

This section describes how to install PyHPS in user mode. If you are interesting in contributing
to PyHPS, see :ref:`contribute` for information on installing in developer mode.

Prerequisites
-------------

You must have Python 3.x and pip_ installed.

#. To see if a Python 3.x version is installed and available from your command line,
   run this command:

   .. code:: 

       python --version

#. If you do not have a Python 3.x version installed, install the latest 3.x version from the
   Python organization's `Downloads <https://python.org>`_ page.

#. To see if you have ``pip`` installed, run this command:

   .. code:: 

       pip --version

#. If you do not have ``pip`` installed, see `Installing Packages <https://packaging.python.org/tutorials/installing-packages/>`_
   in the *Python Packaging User Guide*.

#. To ensure that you have the latest version of ``pip``, run this command:

   .. code:: 

       python -m pip install -U pip


Installation
------------

Because PyHPS is a private PyAnsys package not yet published to PyPI, install it by
running this command:

.. code:: 

    python -m pip install git+https://github.com/ansys-internal/pyhps

``pip`` automatically installs any of these package dependencies that are not already installed:

- requests_
- marshmallow_
- marshmallow_oneofschema_
- python-keycloak_
- pydantic_

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
.. _requests: https://pypi.org/project/requests/
.. _marshmallow: https://pypi.org/project/marshmallow/
.. _marshmallow_oneofschema: https://pypi.org/project/marshmallow-oneofschema/
.. _cachetools: https://pypi.org/project/cachetools/
.. _python-keycloak: https://pypi.org/project/python-keycloak/
.. _pydantic: https://pypi.org/project/pydantic/
