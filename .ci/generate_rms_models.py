"""Script to generate the RMS models from the OpenAPI spec."""

import argparse
import os
import subprocess
import tempfile

import requests

parser = argparse.ArgumentParser()
parser.add_argument("-U", "--url", default="https://localhost:8443/hps")

args = parser.parse_args()

hps_url = args.url

file_name = "rms_openapi.json"
api_spec_url = f"{hps_url}/rms/openapi.json"

r = requests.get(api_spec_url, verify=False)

with tempfile.TemporaryDirectory() as tmpdirname:
    file_name = os.path.join(tmpdirname, file_name)
    with open(file_name, "w") as f:
        f.write(r.text)

    cmd = (
        f"datamodel-codegen --input {file_name} --input-file-type openapi "
        "--output src/ansys/hps/client/rms/models.py "
        "--output-model-type pydantic_v2.BaseModel "
        "--base-class ansys.hps.client.common.DictModel "
        "--custom-file-header-path rms_models.header"
    )
    print(f"* Generate models with the following command:\n {cmd}")
    subprocess.run(cmd, check=True, shell=True)

    cmd = "pre-commit run --files src/ansys/hps/client/rms/models.py"
    print(f"* Running pre-commit on models with the following command:\n {cmd}")
    subprocess.run(cmd, check=False, shell=True)
