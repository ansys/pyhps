"""Script to generate the RMS models from the OpenAPI spec."""

import argparse
import os
import subprocess
import sys
import tempfile

import backoff
import yaml

from ansys.hps.client import Client

parser = argparse.ArgumentParser()
parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
parser.add_argument("-u", "--username", default=os.environ.get("HPS_TEST_USERNAME", "repadmin"))
parser.add_argument("-p", "--password", default=os.environ.get("HPS_TEST_PASSWORD", "repadmin"))

args = parser.parse_args()

hps_url = args.url

# Authenticate, as the OpenAPI spec endpoint is not publicly accessible on all deployments.
client = Client(url=hps_url, username=args.username, password=args.password, verify=False)

# The spec is served in different formats/paths depending on the deployment. The RMS Go
# service serves it as YAML at "openapi.json.yaml" despite the ".json" in the name.
candidate_urls = [
    f"{hps_url}/rms/openapi.json.yaml",
    f"{hps_url}/rms/openapi.json",
    f"{hps_url}/rms/api/v1/openapi.json",
]


@backoff.on_predicate(
    backoff.expo, lambda r: r.status_code == 404, max_time=60, jitter=backoff.full_jitter
)
def _get(url):
    # The RMS service can take a bit longer to come up than the rest of the gateway.
    return client.session.get(url)


spec_text = None
errors = []
for api_spec_url in candidate_urls:
    r = _get(api_spec_url)
    if r.status_code != 200:
        errors.append(f"{api_spec_url} -> HTTP {r.status_code}")
        continue
    try:
        # YAML is a superset of JSON, so this parses both formats.
        data = yaml.safe_load(r.text)
    except yaml.YAMLError as e:
        errors.append(f"{api_spec_url} -> invalid YAML/JSON: {e}")
        continue
    if not isinstance(data, dict):
        errors.append(f"{api_spec_url} -> expected a mapping, got {type(data).__name__}")
        continue
    spec_text = r.text
    break

if spec_text is None:
    sys.exit("Failed to fetch a valid OpenAPI spec:\n" + "\n".join(errors))

with tempfile.TemporaryDirectory() as tmpdirname:
    file_name = os.path.join(tmpdirname, "rms_openapi.yaml")
    with open(file_name, "w") as f:
        f.write(spec_text)

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
