"""Script to generate the RMS models from the OpenAPI spec."""

import argparse
import json
import os
import subprocess
import sys
import tempfile

import backoff

from ansys.hps.client import Client

parser = argparse.ArgumentParser()
parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
parser.add_argument("-u", "--username", default=os.environ.get("HPS_TEST_USERNAME", "repadmin"))
parser.add_argument("-p", "--password", default=os.environ.get("HPS_TEST_PASSWORD", "repadmin"))

args = parser.parse_args()

hps_url = args.url

# Authenticate, as the OpenAPI spec endpoint is not publicly accessible on all deployments.
client = Client(url=hps_url, username=args.username, password=args.password, verify=False)

file_name = "rms_openapi.json"
# Depending on the deployment, the RMS OpenAPI spec can be served either directly
# under /rms or under the versioned /rms/api/v1 prefix.
candidate_urls = [f"{hps_url}/rms/openapi.json", f"{hps_url}/rms/api/v1/openapi.json"]


@backoff.on_predicate(
    backoff.expo, lambda r: r.status_code == 404, max_time=60, jitter=backoff.full_jitter
)
def _get(url):
    # The RMS service can take a bit longer to come up than the rest of the gateway.
    return client.session.get(url)


spec = None
errors = []
for api_spec_url in candidate_urls:
    r = _get(api_spec_url)
    if r.status_code != 200:
        errors.append(f"{api_spec_url} -> HTTP {r.status_code}")
        continue
    try:
        data = r.json()
    except ValueError as e:
        errors.append(f"{api_spec_url} -> invalid JSON: {e}")
        continue
    if not isinstance(data, dict):
        errors.append(f"{api_spec_url} -> expected a JSON object, got {type(data).__name__}")
        continue
    spec = data
    break

if spec is None:
    sys.exit("Failed to fetch a valid OpenAPI spec:\n" + "\n".join(errors))

with tempfile.TemporaryDirectory() as tmpdirname:
    file_name = os.path.join(tmpdirname, file_name)
    with open(file_name, "w") as f:
        json.dump(spec, f)

    cmd = (
        f"datamodel-codegen --input {file_name} --input-file-type openapi "
        "--output src/ansys/hps/client/rms/models.py "
        "--output-model-type pydantic_v2.BaseModel "
        "--base-class ansys.hps.client.common.DictModel "
        "--custom-file-header-path rms_models.header "
        "--output-datetime-class datetime"  # to avoid AwareDatetime
    )
    print(f"* Generate models with the following command:\n {cmd}")
    subprocess.run(cmd, check=True, shell=True)

    cmd = "pre-commit run --files src/ansys/hps/client/rms/models.py"
    print(f"* Running pre-commit on models with the following command:\n {cmd}")
    subprocess.run(cmd, check=False, shell=True)
