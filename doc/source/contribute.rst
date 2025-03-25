.. _contribute:

==========
Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyHPS.
 
The following contribution information is specific to PyHPS.


Install in developer mode
-------------------------

Installing PyHPS in developer mode allows you to modify and enhance the source:

#. Clone the repository:

   .. code:: bash

      git clone https://github.com/ansys/pyhps

#. Access the directory where you have cloned the repository:

   .. code:: bash

      cd pyhps

#. Create a clean Python virtual environment and activate it:

   .. code:: bash
    
      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in a Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Install the package in editable mode with the required build system, documentation,
   and testing tools:

   .. code:: bash

      python -m pip install -U pip setuptools tox
      python -m pip install --editable .[tests,doc]

#. Verify your development installation:

   .. code:: bash

      tox

Test PyHPS
----------

PyHPS takes advantage of `tox`_. This tool allows you to automate common development
tasks (similar to ``Makefile``), but it is oriented towards Python development.

Using ``tox``
^^^^^^^^^^^^^

While ``Makefile`` has rules, ``tox`` has environments. In fact, ``tox``
creates its own virtual environment so that anything being tested is isolated
from the project to guarantee the project's integrity.

The following environment commands are provided:

- ``tox -e style``: Checks for coding style quality.
- ``tox -e py``: Checks for unit tests.
- ``tox -e py-coverage``: Checks for unit testing and code coverage.
- ``tox -e doc-<html/pdf>-<linux/windows>``: Checks for documentation building. For example, to generate html documentation on linux, run ``tox -e doc-html-linux``

Raw testing
^^^^^^^^^^^

If required, from the command line, you can call style commands like
`Black`_, `isort`_, and `Flake8`_. You can also call unit testing commands like `pytest`_.
However, running these commands do not guarantee that your project is being tested
in an isolated environment, which is the reason why tools like ``tox`` exist.

Code style
----------

As indicated in `Coding style <https://dev.docs.pyansys.com/coding-style/index.html>`_
in the *PyAnsys developer's guide*, PyHPS follows PEP8 guidelines. PyHPS
implements `pre-commit`_ for style checking.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  Add License Headers......................................................Passed

Documentation
-------------

For building documentation, you can manually run these commands:

.. code:: bash

    make -C doc html # for building documentation on linux

However, the recommended way of checking documentation integrity is to use
``tox``. For example, the following can be run on linux:

.. code:: bash

    tox -e doc-html-linux && your_browser_name doc/_build/html/index.html

Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m pip install -e .[build]
    python -m build
    python -m twine check dist/*


Generate or update JMS resources
--------------------------------

To generate Job Management Service (JMS) resources from the corresponding schemas, run this command::

  python generate_resources.py

To apply code styling standards to the generated code, run this command::
  
  pre-commit run --all-files

Generate or update RMS models
-----------------------------

To generate Resource Management Service (RMS) pydantic models, first download the RMS OpenAPI
specification and save it as ``rms_openapi.json`` in the root of the repository. Then, run the
data model generator with this command:

.. code:: bash

    datamodel-codegen --input .\rms_openapi.json --input-file-type openapi \
      --output src/ansys/hps/client/rms/models.py \
      --output-model-type pydantic_v2.BaseModel \
      --base-class ansys.hps.client.common.DictModel \
      --custom-file-header-path rms_models.header

Post issues
-----------
Use the `PyHPS Issues <https://github.com/ansys/pyhps/issues>`_
page to report bugs and request new features. When possible, use the issue
templates provided. If your issue does not fit into one of these templates,
click the link for opening a blank issue.

On the `PyHPS Discussions <https://github.com/ansys/pyhps/discussions>`_ page
or the `Discussions <https://discuss.ansys.com/>`_ page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

.. LINKS AND REFERENCES
.. _Black: https://github.com/psf/black
.. _isort: https://github.com/PyCQA/isort
.. _Flake8: https://flake8.pycqa.org/en/latest/
.. _pytest: https://docs.pytest.org/en/stable/
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
