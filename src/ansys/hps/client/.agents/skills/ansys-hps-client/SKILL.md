---
name: ansys-hps-client
description: Best practices for writing code with ansys-hps-client (pyhps), the Python client for Ansys HPC Platform Services. Use when working with HPS projects, jobs, tasks, files, evaluators, live log streaming, WebSocket monitoring, or any ansys.hps.client API.
---

# ansys-hps-client (pyhps)

Python client for Ansys HPC Platform Services (HPS). Manages HPC workflows: define simulations as projects, submit parametric jobs, monitor task execution, stream live logs and metrics, and retrieve results.

**For live solver monitoring (MonitorClient timeout, job reset, residual parsing):** see also `hps-solver-monitoring` (shared patterns) and solver-specific skills: `hps-fluent-monitoring`, `hps-mapdl-monitoring`, `hps-aedt-monitoring`.

## Installing

```bash
pip install ansys-hps-client
```

## Four API namespaces

| Namespace | Class | Purpose |
|-----------|-------|---------|
| **JMS** (Job Management Service) | `JmsApi`, `ProjectApi` | Projects, jobs, tasks, files, parameters — primary API |
| **RMS** (Resource Management Service) | `RmsApi` | Query evaluators, compute resources, analyze requirements |
| **RCS** (Resource Configuration Service) | `RcsApi` | Register/unregister evaluator instances |
| **Monitor** | `MonitorClient` | Stream live logs and metrics over WebSocket; query historical logs via REST |

## Authentication and connecting

```python
from ansys.hps.client import Client

# Username/password (most common)
client = Client(
    url="https://myserver:8443/hps",
    username="repuser",
    password="repuser",
)

# With an existing access token
client = Client(url="https://myserver:8443/hps", access_token="<token>")

# Client credentials (service accounts — no refresh token)
client = Client(
    url="https://myserver:8443/hps",
    grant_type="client_credentials",
    client_id="my-service",
    client_secret="<secret>",
)
```

`Client` stores an authenticated `requests.Session`, auto-refreshes the token on 401, and passes `verify=None` by default (uses system CA store). Set `verify=False` to skip TLS verification (also sets `disable_security_warnings=True`).

## OIDC browser login

For interactive scenarios where a user should authenticate via their browser (no password in the terminal). Uses Authorization Code + PKCE flow.

### Basic browser login

```python
from ansys.hps.client import Client
from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens, load_tokens, refresh_tokens

# Opens browser, waits for callback, returns token dict
tokens = browser_login("https://myserver:8443/hps")

# Pass tokens directly to Client — tokens stay in memory only
client = Client(url="https://myserver:8443/hps", access_token=tokens["access_token"])
```

For self-signed / local servers:

```python
tokens = browser_login("https://localhost:8443/hps", verify_ssl=False)
```

### Token storage

Only the **refresh token** is ever persisted; access tokens always stay in memory.

```python
# memory (default) — not persisted, lost on process exit
save_tokens(tokens, hps_url="https://myserver:8443/hps", storage="memory")

# disk — platform-encrypted
#   Windows: %USERPROFILE%\.ansys\hps\hps_tokens.json  (DPAPI)
#   Unix/Linux: ~/.ansys/hps/hps_tokens.json  (mode 0o600)
path = save_tokens(tokens, hps_url="https://myserver:8443/hps", storage="disk")

# keyring — system credential manager (requires `pip install keyring`)
#   Windows: Credential Manager
#   macOS: Keychain
#   Linux: Secret Service
save_tokens(tokens, hps_url="https://myserver:8443/hps", storage="keyring")

# Custom keyring service name (or set HPS_OIDC_KEYRING_SERVICE_NAME env var)
save_tokens(tokens, hps_url="...", storage="keyring", service_name="my-app")
```

### Loading saved tokens and refreshing

`refresh_tokens` also needs `verify_ssl=False` on self-signed servers — it hits the token endpoint over HTTPS:

```python
# Load from the backend where they were saved
saved = load_tokens(storage="disk")       # or "keyring"
if saved:
    # Refresh using the saved refresh_token
    new_tokens = refresh_tokens(
        hps_url="https://myserver:8443/hps",
        storage="disk",
        verify_ssl=False,   # required for self-signed certs, same as browser_login
    )
    client = Client(url="...", access_token=new_tokens["access_token"])
```

### Full login-with-persistence pattern

```python
from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens, load_tokens, refresh_tokens

HPS_URL = "https://myserver:8443/hps"
VERIFY  = False   # set to True or a CA-bundle path for properly signed certs

# Try loading + refreshing saved tokens first
tokens = None
saved = load_tokens(storage="keyring")
if saved:
    tokens = refresh_tokens(hps_url=HPS_URL, storage="keyring", verify_ssl=VERIFY)

# Fall back to interactive browser login
if not tokens:
    tokens = browser_login(HPS_URL, verify_ssl=VERIFY)
    save_tokens(tokens, hps_url=HPS_URL, storage="keyring")

client = Client(url=HPS_URL, access_token=tokens["access_token"], verify=VERIFY)
```

### CLI login (one-off / terminal)

The module ships a CLI entry point — useful for grabbing a fresh token without writing a script:

```bash
# Login and save to system keyring (Credential Manager on Windows, Keychain on macOS)
python -m ansys.hps.client.auth.api.oidc_login \
    --url https://myserver:8443/hps \
    --use-keyring

# Self-signed certificate — add --insecure
python -m ansys.hps.client.auth.api.oidc_login \
    --url https://myserver:8443/hps \
    --use-keyring \
    --insecure

# Save to disk instead of keyring
python -m ansys.hps.client.auth.api.oidc_login \
    --url https://myserver:8443/hps \
    --save-to-disk \
    --insecure

# Just refresh already-saved tokens (no browser)
python -m ansys.hps.client.auth.api.oidc_login \
    --url https://myserver:8443/hps \
    --use-keyring \
    --refresh-only

# Print the access token to stdout (useful for piping into other tools)
python -m ansys.hps.client.auth.api.oidc_login \
    --url https://myserver:8443/hps \
    --use-keyring \
    --insecure \
    --print-token
```

Tokens saved via `--use-keyring` are automatically picked up by `refresh_tokens(storage="keyring")` in subsequent scripts.

### Client-side token persistence for refresh cycles

`Client` can persist refreshed tokens automatically via its `token_storage` parameter:

```python
client = Client(
    url="https://myserver:8443/hps",
    access_token=tokens["access_token"],
    refresh_token=tokens["refresh_token"],
    token_storage="keyring",   # "memory" (default) | "disk" | "keyring"
)

# Diagnostics for the last persistence attempt
print(client.last_token_persistence_result)
# {'requested_storage': 'keyring', 'storage_used': 'keyring',
#  'fallback_used': False, 'persisted': True, 'path': None, 'error': None}
```

Set `token_storage_strict=True` to raise immediately if the selected backend is unavailable (default is `False`, which falls back silently to memory).

## Task definition templates

`TaskDefinitionTemplate` objects live at the JMS level (not inside a project). They are blueprints: they carry an execution script, output file definitions, software requirements, and a set of named parameters with defaults. You cannot run a template directly — you must materialise a `TaskDefinition` inside a project from it.

### Reading a template

```python
from ansys.hps.client.jms import JmsApi

jms_api = JmsApi(client)

# List all templates
templates = jms_api.get_task_definition_templates()

# Fetch one by id
template = jms_api.get_task_definition_templates(id="<template-id>")[0]
print(template.name, template.version)
```

### TemplateProperty — execution_context values

`template.execution_context` is a `dict[str, TemplateProperty]`. Each value is **not** a plain dict or JSON string — it is a `TemplateProperty` object:

```python
prop = template.execution_context["filling_height"]
prop.default      # "28"   — always a string/bool/int/None; the actual type is in prop.type
prop.type         # "string" | "bool" | "int"
prop.description  # human-readable description
prop.value_list   # allowed values, or [] for free input
```

Build the `execution_context` dict for a `TaskDefinition` from template defaults:

```python
exec_ctx = {
    k: v.default
    for k, v in template.execution_context.items()
    if v.default is not None
}
```

### TemplateSoftware — software_requirements values

`template.software_requirements` is a `list[TemplateSoftware]`. Each item has `.name` and `.versions` (a list). Convert to the flat dict form expected by `TaskDefinition`:

```python
sw_reqs = [
    {"name": s.name, "version": s.versions[0]}
    for s in template.software_requirements
]
```

### Submitting a job from a template

Full pipeline — works for any template, in any existing or new project:

```python
import warnings
from datetime import datetime, timezone
from ansys.hps.client.jms import JmsApi, ProjectApi, Project
from ansys.hps.client.jms.resource.task_definition import TaskDefinition
from ansys.hps.client.jms.resource.job_definition import JobDefinition
from ansys.hps.client.jms.resource.job import Job
from ansys.hps.client.jms.resource.file import File

jms_api = JmsApi(client)

# ── 1. Fetch template ──────────────────────────────────────────────────────
template = jms_api.get_task_definition_templates(id="<template-id>")[0]

# ── 2. Resolve or create project ──────────────────────────────────────────
# Use an existing project:
project_api = ProjectApi(client, "<project-id>")

# Or create a new one:
# project = jms_api.create_project(Project(name="my-project", active=True))
# project_api = ProjectApi(client, project.id)

# ── 3. Copy the execution script from the template into the project ────────
# Returns a File whose .id becomes execution_script_id in the TaskDefinition.
exec_file = project_api.copy_execution_script(template)

# ── 4. Create output File objects ─────────────────────────────────────────
# Template.output_files lists them but they are NOT created automatically.
# Must create File objects in the project and collect their ids.
# The template's output_files are TemplateOutputFile objects with the same
# fields as File (name, type, evaluation_path, monitor, collect).
output_files = project_api.create_files([
    File(
        name=f.name,
        type=f.type,
        evaluation_path=f.evaluation_path,
        monitor=f.monitor,
        collect=f.collect,
    )
    for f in template.output_files
])
output_file_ids = [f.id for f in output_files]

# ── 5. Build execution_context and software_requirements from template ─────
exec_ctx = {k: v.default for k, v in template.execution_context.items()
            if v.default is not None}
sw_reqs  = [{"name": s.name, "version": s.versions[0]}
            for s in template.software_requirements]

# ── 6. Create TaskDefinition ───────────────────────────────────────────────
[td] = project_api.create_task_definitions([TaskDefinition(
    name="my-task",
    use_execution_script=True,
    execution_script_id=exec_file.id,
    execution_level=0,
    execution_context=exec_ctx,
    environment={},
    software_requirements=sw_reqs,
    resource_requirements={"distributed": False},
    worker_context={},
    store_output=True,
    num_trials=1,
    output_file_ids=output_file_ids,
)])

# ── 7. Create JobDefinition ────────────────────────────────────────────────
[jd] = project_api.create_job_definitions([
    JobDefinition(name="my-job-def", active=True, task_definition_ids=[td.id])
])

# ── 8. Submit Job ──────────────────────────────────────────────────────────
[job] = project_api.create_jobs([
    Job(name="my-job", job_definition_id=jd.id, eval_status="pending")
])
print(f"Job submitted: {job.id}  status={job.eval_status}")
```

### Overriding individual parameters

Pass only the keys you want to change; the rest keep the template default:

```python
exec_ctx["filling_height"] = "35"   # override before step 6
exec_ctx["viscosity"] = "0.005"
```

### Listing and filtering templates

```python
# Filter by name client-side (no server-side name filter on this endpoint)
sim_templates = [t for t in jms_api.get_task_definition_templates()
                 if "simulation" in t.name.lower()]
```

## JMS — Job Management Service

### Project lifecycle

```python
from ansys.hps.client.jms import JmsApi, ProjectApi, Project

jms_api = JmsApi(client)

# Create (replace=True silently overwrites an existing project with the same name)
project = jms_api.create_project(Project(name="my-sim", active=True, priority=1), replace=True)

project_api = ProjectApi(client, project.id)

# Look up later
project = jms_api.get_project_by_name("my-sim")
project_api = ProjectApi(client, project.id)
```

### Resource hierarchy

```
Project
 ├── File            — input/output file descriptors (src= for upload path, evaluation_path= for runtime path)
 ├── ParameterDefinition  — typed parameters (Float/Int/Bool/String)
 ├── ParameterMapping     — maps parameters to file content
 ├── TaskDefinition       — one execution step: command, SW requirements, resource requirements, file I/O
 ├── JobDefinition        — groups TaskDefinitions + ParameterDefinitions into a study template
 └── Job                  — one parametric run (holds values dict); contains Task(s)
      └── Task            — the actual execution unit; status tracked here
```

### Files

```python
from ansys.hps.client.jms import File

files = project_api.create_files([
    # Input file — src is the local path used for upload
    File(name="script", src="/local/path/run.py", evaluation_path="run.py", type="text/plain"),
    # Output file — no src; collect=True downloads after execution, monitor=True streams live
    File(name="results", evaluation_path="output/*.csv", type="text/plain", collect=True, monitor=True),
])
file_ids = {f.name: f.id for f in files}
```

`src` accepts a string path or a binary file-like object. It is only used during file creation and is never returned by the API.

### Task definitions

```python
from ansys.hps.client.jms import (
    TaskDefinition, Software, ResourceRequirements, SuccessCriteria, HpcResources
)

task_def = TaskDefinition(
    name="run-solver",
    execution_command="%executable% -i input.dat",
    software_requirements=[Software(name="MAPDL", version="2024 R2")],
    resource_requirements=ResourceRequirements(
        platform="linux",
        num_cores=4,
        memory=8 * 1024**3,   # bytes
        disk_space=10 * 1024**3,
    ),
    input_file_ids=[file_ids["script"]],
    output_file_ids=[file_ids["results"]],
    success_criteria=SuccessCriteria(return_code=0, require_all_output_files=True),
    max_execution_time=3600.0,
    num_trials=1,
)
[task_def] = project_api.create_task_definitions([task_def])
```

For HPC clusters, add `hpc_resources=HpcResources(num_cores_per_node=32, queue="short", exclusive=True)` inside `ResourceRequirements`.

### Job definitions and jobs

```python
from ansys.hps.client.jms import JobDefinition, Job

[job_def] = project_api.create_job_definitions([
    JobDefinition(name="parametric-study", active=True, task_definition_ids=[task_def.id])
])

# Submit N jobs
jobs = project_api.create_jobs([
    Job(name=f"run-{i}", eval_status="pending", job_definition_id=job_def.id)
    for i in range(10)
])
```

### Monitoring and querying results

```python
# Filter by status; select only the fields you need for speed
jobs = project_api.get_jobs(eval_status="evaluated", fields=["id", "name", "values", "fitness"])

for job in jobs:
    print(job.name, job.fitness, job.values)

# Tasks for a specific job
tasks = project_api.get_tasks(job_id=job.id)
for task in tasks:
    print(task.eval_status, task.elapsed_time)
```

`eval_status` lifecycle: `pending` → (evaluator picks up) → `prolog` → `running` → `evaluated` | `failed` | `aborted`

### Downloading output files

```python
files = project_api.get_files(id=task.output_file_ids)
for f in files:
    local_path = project_api.download_file(file=f, target_path="/local/results/")
```

### Long-running async operations

Copy, archive, and restore return an `Operation`. Use `monitor_operation` to wait for completion:

```python
op = project_api.copy_project(wait=False)
jms_api.monitor_operation(op.id, max_time=300)  # polls with exponential backoff

# Archive / restore (requires JMS >= 1.2.0)
project_api.archive_project("/backups/project.tar.gz", include_job_files=True)
restored = jms_api.restore_project("/backups/project.tar.gz")
```

## Monitor — live log and metric streaming

`MonitorClient` connects to the HPS monitor service over WebSocket and REST. All streaming methods return generators — iterate them in a `for` loop or pass `max_messages` to limit how many are consumed.

### Creating a MonitorClient

```python
import ssl
from ansys.hps.client import Client
from ansys.hps.client.monitor import MonitorClient

client = Client(url="https://myserver:8443/hps", username="repuser", password="repuser")

# Default — server must have a trusted TLS certificate
monitor = MonitorClient(client=client)

# Self-signed / local server — disable WebSocket TLS verification
monitor = MonitorClient(
    client=client,
    ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
)
```

`MonitorClient` is a dataclass; use keyword arguments. The WebSocket URL is derived automatically from `client.url` (https → wss).

### Discover what topics exist

```python
topics = monitor.list_topics()  # dict[str, list[str]] — tag key → known values
for key, values in topics.items():
    print(key, values)
```

High-cardinality tags (`timestamp`, `time`) are excluded by default. Pass `exclude_noisy=False` to include them.

### Stream service logs

```python
from ansys.hps.client.monitor import ClientType

# Well-known service types
ClientType.JMS          # "ansys.rep.jms"
ClientType.EVALUATOR    # "ansys.rep.evaluator"
ClientType.FILE_TAIL    # "ansys.rep.evaluator.file_tail"
ClientType.SCALING      # "ansys.rep.scaling"
ClientType.HOUSEKEEPER  # "ansys.rep.housekeeper"

# Stream indefinitely (Ctrl-C to stop)
for msg in monitor.stream_service_logs(ClientType.JMS):
    print(msg["message"])

# Collect a fixed number
msgs = list(monitor.stream_service_logs(ClientType.HOUSEKEEPER, max_messages=50))
```

### Stream task logs (stdout / tailed files)

```python
# All tailed files for a task
for msg in monitor.stream_task_logs(task_id="<task-id>"):
    print(msg.get("message"))

# Narrow to a specific file
for msg in monitor.stream_task_logs(task_id="<task-id>", file_path="file.out"):
    print(msg.get("message"))
```

### Stream task process tree

`msg["message"]` is a **JSON string** encoding a root process node with nested `children`. Use `msg.parsed_message` to decode it automatically — never access `msg.get("processes", [])` (that key does not exist).

```python
# Stream live as snapshots arrive
for snap in monitor.stream_task_process_tree(task_id="<task-id>"):
    root = snap.parsed_message   # decoded dict with "pid", "name", "children", etc.
    if root and "pid" in root:
        print(root["pid"], root.get("name"), root.get("cpu_percentage"))

# Collect snapshots (returns a list)
snapshots = monitor.get_task_process_tree(task_id="<task-id>", max_messages=200)
for snap in snapshots:
    root = snap.parsed_message
    if root:
        print(root.get("pid"), root.get("name"))
```

### Stream host CPU/memory for a running task

`project_id` is required unless omitted — the client then auto-resolves it from task-log messages. `msg["message"]` is a JSON string; use `msg.parsed_message` to decode it.

```python
for update in monitor.stream_task_host_resources(
    task_id="<task-id>",
    project_id="<project-id>",   # optional — omit to auto-resolve
    max_messages=100,
):
    payload = update.parsed_message or {}
    cpu = payload.get("cpu", {}).get("usage")          # float string, e.g. "12.5"
    mem = payload.get("virtual_memory", {}).get("percent")
    print(float(cpu) if cpu is not None else None, float(mem) if mem is not None else None)
```

### Stream scheduler job status (Slurm / LSF)

```python
for status in monitor.stream_scheduler_job_status(task_definition_id="<taskdef-id>"):
    print(status)
```

### Query historical logs via REST

```python
# Build info
info = monitor.get_build_info()

# Query with filters (tag keys prefixed automatically)
response = monitor.query_logs(filters={
    "client_type": ClientType.JMS,
    "level": "ERROR",
})
for msg in response.messages:
    print(msg["message"])
```

### Infer project_id from a task

When you only have a `task_id` and need its `project_id`:

```python
project_id = monitor.resolve_project_id_for_task(task_id="<task-id>")
```

### MonitorMessage

All streaming and query methods yield `MonitorMessage` objects. They implement `Mapping[str, Any]` so you can use them like dicts:

```python
msg["message"]          # log text
msg["tags"]             # dict of filter tags (task_id, project_id, client_type, …)
msg.get("level")        # log level if present
msg.to_dict()           # plain dict copy
```

### Build custom filter templates

```python
from ansys.hps.client.monitor.api.monitor_api import build_filter_templates

templates = build_filter_templates(["client_type", "task_id"])
# templates["rest"]      — REST query path + params
# templates["websocket"] — WebSocket subscribe command payload
```

## RMS — Resource Management Service

```python
from ansys.hps.client.rms import RmsApi
from ansys.hps.client.rms.models import AnalyzeRequirements

rms_api = RmsApi(client)

# List available evaluators
evaluators = rms_api.get_evaluators()
for ev in evaluators:
    print(ev.name, ev.platform, ev.host_name)

# Check whether a task definition's requirements can be satisfied
task_defs = project_api.get_task_definitions(id=task_def.id, as_objects=False)
td = task_defs[0]
response = rms_api.analyze(
    requirements=AnalyzeRequirements(
        project_id=project.id,
        software_requirements=td["software_requirements"],
        resource_requirements=td["resource_requirements"],
    ),
    analytics=True,
)
print(response.evaluators)   # list of matching evaluators
```

## Key conventions

### `as_objects` parameter
All `get_*` methods accept `as_objects=True` (default, returns resource objects) or `as_objects=False` (returns raw dicts). Use raw dicts when you need to pass data directly to another API call (e.g., RMS `analyze`).

### Query parameters
`get_*` methods forward extra keyword arguments as query params: `limit`, `offset`, `sort`, `fields`, and any filterable field name.

```python
# Latest 5 failed jobs, only id and name returned
jobs = project_api.get_jobs(eval_status="failed", limit=5, sort="-creation_time", fields=["id", "name"])
```

### Marshmallow (JMS) vs Pydantic (RMS/RCS)
- **JMS** resources (`Project`, `Job`, `File`, etc.) are Marshmallow-backed — instantiate directly with keyword args.
- **RMS/RCS** models (`EvaluatorRegistration`, `AnalyzeRequirements`, etc.) are Pydantic — standard Pydantic instantiation and validation.

### `missing` sentinel
JMS resource fields default to `marshmallow.missing`, not `None`. A field set to `missing` is omitted from serialization (not sent to the server). Check with `from marshmallow import missing; field_value is missing`.

### all_fields
`Client(all_fields=True)` (the default) appends `fields=all` to every request, returning every available field. Set `all_fields=False` to receive only default fields (faster for large result sets).

## Full project setup pattern

```python
from ansys.hps.client import Client
from ansys.hps.client.jms import (
    JmsApi, ProjectApi,
    Project, File, TaskDefinition, JobDefinition, Job,
    Software, ResourceRequirements, SuccessCriteria,
)

client = Client(url="https://myserver:8443/hps", username="repuser", password="repuser")
jms_api = JmsApi(client)

# 1. Project
project = jms_api.create_project(Project(name="demo", active=True), replace=True)
project_api = ProjectApi(client, project.id)

# 2. Files
files = project_api.create_files([
    File(name="script", src="run.py", evaluation_path="run.py", type="text/plain"),
    File(name="results", evaluation_path="results.txt", collect=True),
])
fid = {f.name: f.id for f in files}

# 3. Task definition
[td] = project_api.create_task_definitions([TaskDefinition(
    name="run",
    execution_command="python run.py",
    software_requirements=[Software(name="Python", version="3.10")],
    resource_requirements=ResourceRequirements(num_cores=1, memory=2 * 1024**3),
    input_file_ids=[fid["script"]],
    output_file_ids=[fid["results"]],
    success_criteria=SuccessCriteria(return_code=0),
)])

# 4. Job definition
[jd] = project_api.create_job_definitions([
    JobDefinition(name="study", active=True, task_definition_ids=[td.id])
])

# 5. Submit jobs
project_api.create_jobs([
    Job(name=f"run-{i}", eval_status="pending", job_definition_id=jd.id)
    for i in range(5)
])

# 6. Query results (poll until done)
import time
while True:
    done = project_api.get_jobs(eval_status="evaluated")
    pending = project_api.get_jobs(eval_status="pending")
    print(f"Done: {len(done)}, pending: {len(pending)}")
    if not pending:
        break
    time.sleep(10)
```
