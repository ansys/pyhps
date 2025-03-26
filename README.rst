PyHPS
=====
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |ruff| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-hps-client?logo=pypi
   :target: https://pypi.org/project/ansys-hps-client
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-hps-client.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-hps-client
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/pyhps/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pyhps
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pyhps/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyhps/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pyhps/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyhps/main
   :alt: pre-commit.ci status

PyHPS is a Python client library for Ansys HPC Platform Services (HPS), which is
a set of technology components designed to help you manage the execution of simulations
while making use of your full range of computing assets.

PyHPS brings Ansys HPS to your Python app. Wrapping around Ansys HPS REST APIs, PyHPS
allows you to:

* Create projects and modify existing ones.
* Monitor and manage jobs.
* Run your own design exploration algorithms.
* Retrieve simulation results.

Documentation and issues
------------------------

Documentation for the latest stable release of PyHPS is hosted at
`PyHPS documentation <https://hps.docs.pyansys.com/version/dev/>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

The PyHPS documentation contains these sections:

- `Getting started <https://hps.docs.pyansys.com/version/dev/getting_started/index.html>`_: Explains
  how to install PyHPS in user mode.
- `User guide <https://hps.docs.pyansys.com/version/dev/user_guide/index.html>`_: Describes the basics
  of how to use PyHPS to interact with Ansys HPS.
- `Examples <https://hps.docs.pyansys.com/version/dev/examples/index.html>`_: Provides examples of how
  to interact with Ansys HPS in Python using PyHPS.
- `API reference <https://hps.docs.pyansys.com/version/dev/api/index.html>`_: Describes PyHPS functions,
  classes, methods, and their parameters and return values so that you can understand how to
  interact with them programmatically
- `Contribute <https://hps.docs.pyansys.com/version/dev/contribute.html>`_: Provides information on
  how to install PyHPS in developer mode and make contributions to the codebase and documentation.

On the `PyHPS Issues <https://github.com/ansys/pyhps/issues>`_ page, you can
create issues to report bugs and request new features. On the
`PyHPS Discussions <https://github.com/ansys/pyhps/discussions>`_ page or the
`Discussions <https://discuss.ansys.com/>`_ page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

License
-------

PyHPS is licensed under the MIT license.

PyHPS makes no commercial claim over Ansys whatsoever. This library extends the
functionality of Ansys HPC Platform Services by adding a Python interface to it
without changing the core behavior or license of the original software. The use
of PyHPS requires a legally licensed local copy of Ansys HPC Platform Services.

To get a copy of Ansys HPC Platform Services, see the `Ansys HPC Platform Services Guide <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/hpcplat/v000/en/rep_ug/rep_ug.html>`_
in the Ansys Help.
