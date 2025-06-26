# Running arbitrary python scripts on HPS
This example shows how arbitrary python scripts can be run on HPS, by using UV to generate 
the required environments on the fly.

The example sets up a project that will plot `sin(x)` using numpy and matplotlib, and then save 
the figure to a file. After the run is completed, the generated ephemeral venv is cleaned up.

The main feature enabling UV to take care of the environment setup is the metadata header present 
in the `eval.py` script, which defines the dependencies:

```python
# /// script
# requires-python = "==3.12"
# dependencies = [
#     "numpy",
#     "matplotlib"
# ]
# ///
```

More information can be found [here (python.org)](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata) and [here (astral.sh)](https://docs.astral.sh/uv/guides/scripts/#running-a-script-with-dependencies).

# Prerequisites
In order for the example to run, `UV` must be installed and registered on the scaler/evaluator. 
On a pcluster, this can be done in the following way:

```bash
pip3 install --target=/ansys_inc/uv uv # Install UV via pip
mkdir -p /shared/rep_file_storage/uv/uv_cache # Create cache dir
```

Note that the directories `/ansys_inc/uv` and `/shared/rep_file_storage/uv/uv_cache` are shared 
directories, they are both accessible by all evaluators.

Next, the application must be registered in the scaler/evaluator with the following properties:

| **Property**      | **Value**                 |
|-------------------|---------------------------|
|   Name            |   Uv                      | 
|   Version         |  0.6.14                   | 
| Installation Path | /ansys_inc/uv             |
| Executable        | /ansys_inc/uv/bin/uv      |

and the following environment variable:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /shared/rep_file_storage/uv/uv_cache |

Note that the version should be adjusted to the case at hand. 

The above steps setup UV with the cache located in a shared folder, such that any dependency will 
only need to be downloaded once. However, if the bandwidth between this shared folder and the 
compute nodes is relatively slow, this can lead to long venv setuo times (on pclusters, a dozen 
seconds is typical for reasonably large dependencies).

Instead, UV can also be setup to use node local caching:

## Node local cache
In cases where many short tasks are run, shorter runtimes can often be found by relocating the 
UV cache to node local storage. In such a setup, each compute node has its own cache, meaning each 
node will have to download all dependencies individually. Once the required packages are cached, 
venv setup times will be on the order of 100 ms, 2 orders of magnitude faster than for the shared 
case. To use node-local cache, the cache dir must be set to a directory local to each node. On 
pclusters, for example, one could use the following value:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /tmp/scratch/uv_cache                |

## Airgapped setups
For airgapped setups where no internet connectivity is available, there are several options for a 
successful UV setup:

1. Pre-populate the UV cache with all desired dependencies.
2. Provide a local python package index, and set UV to use it. More information can be found
[here](https://docs.astral.sh/uv/configuration/indexes/). This index could then sit in a shared 
location, with node-local caching applied.
3. Use pre-generated virtual environments, see [here](https://docs.astral.sh/uv/reference/cli/#uv-venv)

In order to disable network access, one can either set the `UV_OFFLINE` environment variable, or 
use the `--offline` flag with many UV commands. 

# Running the example
To run the example, execute the `project_setup.py` script, for example via `uv run project_setup.py`.
This will setup a project with a number of jobs, and each job will generate a `plot.png` file.


## Options
The example supports the following command line arguments:

| **Flag**               | **Example** | **Description**                                                              |
|------------------------|----------------------------------|---------------------------------------------------------|
| -U, --url              | --url=https://localhost:8443/hps |URL of the target HPS instance                           |
| -u, --username         | --username=repuser               |Username to log into HPS                                 |
| -p, --password         | --password=topSecret             |Password to log into HPS                                 |
| -j, --num-jobs         | --num-jobs=10                    |Number of jobs to generate                               |

## Files
The relevant files of the example are:

- `project_setup.py`: Handles all communication with the HPS instance. Defines the project and 
generates the jobs.
- `eval.py`: The script that is evaluated on HPS. Contains the code to plot a sine, and then save 
the figure.
- `exec_script.py`: Execution script that uses UV to run the evaluation script. Also cleans up the 
venv generated by UV.