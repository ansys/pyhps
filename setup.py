import os

from setuptools import find_namespace_packages, setup

# We follow option 3 suggested by PyPA
# https://packaging.python.org/guides/single-sourcing-package-version/
# to get the package version.
root = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(root, "ansys", "hps", "client", "__version__.py"), "r") as f:
    exec(f.read(), about)

setup(
    name="ansys-pyhps",
    version=about["__version__"],
    url=about["__url__"],
    author="ANSYS, Inc.",
    author_email="pyansys.support@ansys.com",
    maintainer="PyAnsys developers",
    maintainer_email="pyansys.maintainers@ansys.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_file="LICENSE",
    description="A python client for Ansys HPC Platform Services",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    install_requires=[
        "requests>=2.21.0",
        "marshmallow>=3.0.0",
        "marshmallow_oneofschema>=2.0.1",
        "python-keycloak>=1.5.0,<=2.12.0",
        "backoff>=2.0.0",
        "pydantic>=1.10.0",
    ],
    python_requires=">=3.7",
    packages=find_namespace_packages(include=["ansys.*"]),
)
