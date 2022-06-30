# Ansys pyrep - REP Python client #

Todo: Merge README.rst from pyansys template with README.md from dcs python client

[![Build Status](https://tfs.ansys.com:8443/tfs/ANSYS_Development/ANSYS-CH/_apis/build/status/DCS/DCS%20Python%20Client%20Win64)](https://tfs.ansys.com:8443/tfs/ANSYS_Development/ANSYS-CH/_build/latest?definitionId=5619)


Python clients for Ansys Distributed Compute Services (DCS).

## Installation

A wheel is available on the ANSYS PyPI repository. Installing it is as simple as:

```
pip install ansys-dcs-client --extra-index-url http://<username>:<encrypted_password>@canartifactory.ansys.com:8080/artifactory/api/pypi/pypi/simple --trusted-host canartifactory.ansys.com
```

The `--extra-index-url` allows `pip` to retrieve ``ansys-dcs-client`` from ANSYS private PyPI repository but still install public packages ``ansys-dcs-client`` depend on that may not be available there.

To install the latest development version add the `--pre` flag to the command above.


## Example Usage

```python
from ansys.rep.client.jms import Client

client = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")

# query a project
project = client.get_project(id="demo_project")

# get design points
jobs = project.get_jobs()

# set failed design points to pending
failed_dps = [dp for dp in jobs if dp.eval_status == "failed"]
for dp in failed_dps:
   dp.eval_status = "pending"
failed_dps = project.update_jobs(failed_dps)
```

## Development 

This package is currently developed with standard Python 3 
and standard packages downloaed from https://pypi.org/.

The source code is available [here](ttps://tfs.ansys.com:8443/tfs/ANSYS_Development/ANSYS-CH/_git/dcs-client). The TFS build definition can be found [here](https://tfs.ansys.com:8443/tfs/ANSYS_Development/ANSYS-CH/ANSYS-CH%20Team/_build/index?definitionId=2540&_a=completed). 

### Setup 

* Install standard Python 3
* Setup the project dev environment
  ```
  python build.py venv
  ```
  Remember to activate the virtual env.

### Run tests

From within the dev env, using `pytest`

```
python -m pytest
```

Or, using the build script 
```
python build.py tests
```

which will run something similar to

```
python -m pytest -v --junitxml test_results.xml --cov=ansys --cov-report=xml --cov-report=html
```

By default the integration tests try to connect to the local DCS server at `https:/127.0.0.1/dcs/` with default username and password. To specify different ones (e.g. on a build machine), please set the following environment variables:

| Variable              | Example Values on Windows            | Description                        |
|-----------------------|--------------------------------------|------------------------------------|
| DCS_TEST_URL          | https://212.126.163.153/dcs/         | DCS server URL                     |
| DCS_TEST_USERNAME     | tfsbuild                             | Username                           |
| DCS_TEST_PASSWORD     | tfsbuild                             | Password                           |

Few test assumes that the project `mapdl_motorbike_frame` already exists on the DCS server. 
In case, you can create such project running the script `examples/mapdl_motorbike_frame/project_setup.py`.   

### Create wheel package
   
   ```
   python build.py wheel
   ```

### Generate the documentation

   To generate the HTML documentation:

   ```
   python build.py documentation
   ```

## Update of the Ansys Version

There is a Python script `update_ansys_version_number.py` in the root folder of the repo that updates the version numbers.
Here is an example how to run it. The first argument is the internal ID, second argument is the external ID:

``` bash
>> python update_ansys_version_number.py 23.1 "2023 R1" 
```