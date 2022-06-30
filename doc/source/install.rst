.. _installation:

Installation
============

Make sure you have ``Python 3`` and that the expected version is available from your command line. You can check this by running:

.. parsed-literal::

    $ python --version

If you do not have Python, please install the latest 3.x version from `python.org <https://python.org>`_.

Additionally, make sure you have ``pip`` available. You can check this by running:

.. parsed-literal::

    $ pip --version

If pip isn't already installed, please refer to the `Installing Packages Tutorial <https://packaging.python.org/tutorials/installing-packages/>`_ from the Python Packaging Authority.


Installing ``ansys-dcs-client`` is as simple as, on Windows:

.. parsed-literal::

    $ pip install "%AWP_ROOT\ |version_no_dots|\ %\\dcs\\share\\python_client\\ansys_dcs_client-\ |client_version|\ -py3-none-any.whl"

on Linux:

.. parsed-literal::

    $ pip install /usr/ansys_inc/v\ |version_no_dots|\ /dcs/share/python_client/ansys_dcs_client-\ |client_version|\ -py3-none-any.whl


The following dependencies are automatically installed through ``pip`` (if not already available):

- requests_
- marshmallow_
- marshmallow_oneofschema_

.. _requests: https://pypi.org/project/requests/
.. _marshmallow: https://pypi.org/project/marshmallow/
.. _marshmallow_oneofschema: https://pypi.org/project/marshmallow-oneofschema/
