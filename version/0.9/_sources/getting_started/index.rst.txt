.. _getting_started:

Getting started
===============

This section describes how to install PyHPS in user mode. If you are interested in contributing
to PyHPS, see :ref:`contribute` for information on installing in developer mode.

Prerequisites
-------------

You must have pip_ and Python 3.9, 3.10, 3.11, or 3.12 installed.

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

To install PyHPS in user mode, run this command:

.. code:: bash

    python -m pip install ansys-hps-client

Dependencies
~~~~~~~~~~~~

PyHPS requires these packages as dependencies:

* `requests <https://pypi.org/project/requests/>`_
* `marshmallow <https://pypi.org/project/marshmallow/>`_
* `marshmallow_oneofschema <https://pypi.org/project/marshmallow-oneofschema/>`_
* `pydantic <https://pypi.org/project/pydantic/>`_
* `PyJWT <https://pypi.org/project/PyJWT/>`_

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/