PyHPS
=====
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.7-blue
   :target: https://pypi.org/project/ansys-rep/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-rep.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-rep
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/pyansys/pyhps/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/pyansys/pyhps
   :alt: Codecov

.. |GH-CI| image:: https://github.com/pyansys/pyhps/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pyhps/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


A Python client library for the Ansys HPC Platform Services.

How to install
--------------

In order to install PyHPS, make sure you
have the latest version of `pip`_. To do so, run:

.. code:: bash

    python -m pip install -U pip

Then, as long as PyHPS is a private pyAnsys module not published to pypi yet, you can execute:

.. code:: bash

    python -m pip install git+https://github.com/pyansys/pyhps

.. TODO: Enable this once pyhps is published:  python -m pip install ansys-pyhps

Contribute
----------

Before contributing to the project, ensure that you are thoroughly
familiar with the `PyAnsys Developer's guide`_. You will 
need to follow these steps:

#. Clone this repository:

    .. code:: bash

        git clone https://github.com/pyansys/pyhps
        cd pyhps

#. Create a new Python environment and activate it:

    .. code:: bash

        # Create a virtual environment
        python -m venv .venv

        # Activate it in a POSIX system
        source .venv/bin/activate

        # Activate it in Windows CMD environment
        .venv\Scripts\activate.bat

        # Activate it in Windows Powershell
        .venv\Scripts\Activate.ps1

#. Make sure you have the latest required build system and doc, testing, and CI tools:

    .. code:: bash

        python -m pip install -U pip setuptools tox
        python -m pip install -e .[tests,doc]

#. Install the project in editable mode:

    .. code:: bash
    
        python -m pip install --editable .

How to testing
--------------

This project takes advantage of `tox`_. This tool allows to automate common
development tasks (similar to Makefile) but it is oriented towards Python
development. 

Using tox
^^^^^^^^^

As Makefile has rules, `tox`_ has environments. In fact, the tool creates its
own virtual environment so anything being tested is isolated from the project in
order to guarantee project's integrity. The following environments commands are provided:

- **tox -e style**: will check for coding style quality.
- **tox -e py**: checks for unit tests.
- **tox -e py-coverage**: checks for unit testing and code coverage.
- **tox -e doc**: checks for documentation building process.


Raw testing
^^^^^^^^^^^

If required, you can always call the style commands (`black`_, `isort`_,
`flake8`_...) or unit testing ones (`pytest`_) from the command line. However,
this does not guarantee that your project is being tested in an isolated
environment, which is the reason why tools like `tox`_ exist.


A note on pre-commit
^^^^^^^^^^^^^^^^^^^^

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool via:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Documentation
-------------

For building documentation, you can manually run:

.. code:: bash

    python archive_examples.py
    python -m sphinx -b html doc/source build/sphinx/html

The recommended way of checking documentation integrity is using:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m build
    python -m twine check dist/*


How to generate/update RMS models
---------------------------------


To generate RMS Pydantic models, first download the RMS openapi spec and save it as `rms_openapi.json` at the root of the repository.
Then, run the datamodel generator:

.. code:: bash
    
    datamodel-codegen --input .\rms_openapi.json --input-file-type openapi --output ansys/hps/client/rms/models.py --output-model-type pydantic_v2.BaseModel


Documentation, Issues, and Support
----------------------------------
Documentation for the latest stable release of PyHPS is hosted at `PyHPS documentation
<https://rep.docs.pyansys.com/dev/>`_.

On the `PyHPS Issues <https://github.com/ansys/pyhps/issues>`_ page,
you can create issues to report bugs and request new features. On the `PyHPS Discussions
<https://github.com/ansys/pyhps/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback. 

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
