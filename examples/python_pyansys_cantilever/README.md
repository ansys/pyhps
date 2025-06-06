# Running pyAnsys on HPS
This example shows how pyAnsys applications can be deployed to HPS. 

The application simulates a parametrized cantilever by chaining several pyAnsys packages:

1. Use pyAnsys Geometry to draw a cantilever design
2. Use pyPrimeMesh to apply a swept mesh to the cantilever design
3. Use pyMAPDL to calculate Eigenfrequencies of the cantilever, then display them as output 
parameters

The physical cantilever dimensions, as well as several mesh and simulation properties are 
parametrized.

# Prerequisites
There are several packages that need to be installed for the example to function. The precise paths 
and steps given in the following setup instructions are optimized for installation on a pCluster. 
They can easily be adapted to other systems. Also note that version numbers should be adjusted to 
reflect reality.

## UV
UV is used to run arbitrary python scripts in environments created on the fly. It can be installed 
and set up in the following way:

```bash
pip3 install --target=/ansys_inc/v252/uv uv # Install UV via pip
mkdir -p /shared/rep_file_storage/uv/uv_cache # Create cache dir
echo cache-dir = \"/shared/uv/uv_cache\" > /shared/rep_file_storage/uv/uv.toml # Set cache dir in config
```

The UV application should then also be registered in the scaler with the following properties:

| **Property**      | **Value**                 |
|-------------------|---------------------------|
|   Name            |   Uv                      | 
|   Version         |  0.6.14                   | 
| Installation Path | /ansys_inc/v252/uv        |
| Executable        | /ansys_inc/v252/uv/bin/uv |

and the following environment variables:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /shared/rep_file_storage/uv/uv_cache |
| UV_CONFIG_FILE   | /shared/rep_file_storage/uv/uv.toml  |

This will setup UV with the cache located in a shared folder, accessible from all nodes, such that
any package will only need to be downloaded once. However, if the bandwidth between this shared 
folder and the compute nodes is relatively slow, this can lead to long venv setup times (on 
pClusters, a dozen seconds is typical for reasonably large dependencies). 

### Node local cache

In cases where many short tasks are run, shorter runtimes can often be found by relocating the 
UV cache to node-local storage. In such a setup, each compute node has its own cache, meaning each 
node will have to download all dependencies individually. Once the required packages are cached, 
venv setup times will be on the order of 100 ms, 2 orders of magnitude faster than for the shared 
case. To use node-local cache, the cache dir must be specified differently from what's shown above:

1. Update the cache dir in the config file:
```bash
echo cache-dir = \"/tmp/scratch/uv_cache\" > /shared/rep_file_storage/uv/uv.toml # Set cache dir in config
```
2. Update the corresponding environment variable in the UV application registration:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /tmp/scratch/uv_cache                |

### Airgapped setups

For airgapped setups where no internet connectivity is available, there are several options for a 
successful UV setup:

1. Pre-populate the UV cache with all desired dependencies.
2. Provide a local python package index, and set UV to use it. More information can be found
[here](https://docs.astral.sh/uv/configuration/indexes/). This index could then sit in a shared 
location, with node-local caching applied.
3. Use pre-generated virtual environments, see [here](https://docs.astral.sh/uv/reference/cli/#uv-venv)

In order to disable network access, one can either set the `UV_OFFLINE` environment variable, or 
use the `--offline` flag with many UV commands. 

## Ansys Geometry Service
The Ansys Geometry Service must be installed for pyAnsys Geometry to function on a pCluster. This is done by 
applying the `-geometryservice` flag to the Ansys unified installer. The application should then be 
registered in the scaler as follows:

| **Property**      | **Value**                       |
|-------------------|---------------------------------|
| Name              | Ansys GeometryService           |
| Version           | 2025 R2                         |
| Installation Path | /ansys_inc/v252/GeometryService |

With the following environment variables:

| **Env Variable**            | **Value**                       |
|-----------------------------|---------------------------------|
| ANSRV_GEO_LICENSE_SERVER    | \<LICENSE@SERVER\>               |
| ANSYS_GEOMETRY_SERVICE_ROOT | /ansys_inc/v252/GeometryService |

## Ansys Prime Server
The Ansys Prime Server is automatically installed with Ansys 2023 R1 or later, and is needed for 
pyPrimeMesh. It should be registered in the scaler as:

| **Property**      | **Value**                       |
|-------------------|---------------------------------|
| Name              | Ansys Prime Server           |
| Version           | 2025 R2                         |
| Installation Path | /ansys_inc/v252/GeometryService |

With environment variables:

| **Env Variable**   | **Value**                          |
|--------------------|------------------------------------|
| AWP_ROOT252        | /ansys_inc/v252                    |
| ANSYS_PRIME_ROOT   | /ansys_inc/v252/meshing/Prime      |

## Ansys Mechanical APDL
This can be installed with the Ansys unified installer, and should be auto-detected by the scaler. 
Just two environment variables need to be added to the application registration for pyMAPDL to 
work properly:

| **Env Variable**   | **Value**                          |
|--------------------|------------------------------------|
| AWP_ROOT252        | /ansys_inc/v252                    |
| PYMAPDL_MAPDL_EXEC | /ansys_inc/v252/ansys/bin/ansys252 |

# Running the example

Pipeline ipsum dolor sit amet, kubernetes elit. Terraform apply sed do docker-compose up incididunt ut labore et Jenkins pipeline. Ut enim ad minim deploy, quis git push origin main exercitation helm upgrade laboris nisi ut ansible-playbook. CI/CD aute irure dolor in observability in grafana reprehenderit in monitoring velit esse error budget. Excepteur sint occaecat scaling non proident, sunt in culpa qui rollback deserunt mollit id SRE.

# Logic of the code

Pipeline ipsum dolor sit amet, kubernetes elit. Terraform apply sed do docker-compose up incididunt ut labore et Jenkins pipeline. Ut enim ad minim deploy, quis git push origin main exercitation helm upgrade laboris nisi ut ansible-playbook. CI/CD aute irure dolor in observability in grafana reprehenderit in monitoring velit esse error budget. Excepteur sint occaecat scaling non proident, sunt in culpa qui rollback deserunt mollit id SRE.