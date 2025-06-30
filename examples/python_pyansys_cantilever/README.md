# Running pyAnsys on HPS
This example shows how to run pyAnsys scripts on HPS. 

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

## uv
uv is used to run arbitrary python scripts in environments created on the fly. It can be installed 
and set up in the following way:

```bash
pip3 install --target=/ansys_inc/v252/uv uv # Install uv via pip
mkdir -p /shared/rep_file_storage/uv/uv_cache # Create cache dir
```

The uv application should then also be registered in the scaler with the following properties:

| **Property**      | **Value**                 |
|-------------------|---------------------------|
|   Name            |   uv                      | 
|   Version         |  0.6.14                   | 
| Installation Path | /ansys_inc/v252/uv        |
| Executable        | /ansys_inc/v252/uv/bin/uv |

and the following environment variable:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /shared/rep_file_storage/uv/uv_cache |

This will setup uv with the cache located in a shared folder, accessible from all nodes, such that
any package will only need to be downloaded once. However, if the bandwidth between this shared 
folder and the compute nodes is relatively slow, this can lead to long venv setup times (on 
pClusters, a dozen seconds is typical for reasonably large dependencies). 

### Node local cache

In cases where many short tasks are run, shorter runtimes can often be found by relocating the 
uv cache to node-local storage. In such a setup, each compute node has its own cache, meaning each 
node will have to download all dependencies individually. Once the required packages are cached, 
venv setup times will be on the order of 100 ms, 2 orders of magnitude faster than for the shared 
case. To use node-local cache, the cache dir must be specified differently from what's shown above:

1. Update the corresponding environment variable in the uv application registration:

| **Env Variable** | **Value**                            |
|------------------|--------------------------------------|
| UV_CACHE_DIR     | /tmp/scratch/uv_cache                |

### Airgapped setups

For airgapped setups where no internet connectivity is available, there are several options for a 
successful uv setup:

1. Pre-populate the uv cache with all desired dependencies.
2. Provide a local python package index, and set uv to use it. More information can be found
[here](https://docs.astral.sh/uv/configuration/indexes/). This index could then sit in a shared 
location, with node-local caching applied.
3. Use pre-generated virtual environments, see [here](https://docs.astral.sh/uv/reference/cli/#uv-venv)

In order to disable network access, one can either set the `UV_OFFLINE` environment variable, or 
use the `--offline` flag with many uv commands. 

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

## HPS Python Client
To run the example, a `ansys-hps-client` version released after 27 March 2025 is required. 


# Running the example
To run the example, execute the `project_setup.py` script, for example via `uv run project_setup.py`. 
The required packages are `ansys-hps-client` (released after 27 March 2025) and `typer`.

## Options
The example supports the following command line arguments:

| **Flag**               | **Example** | **Description**                                                              |
|------------------------|----------------------------------|---------------------------------------------------------|
| -U, --url              | --url=https://localhost:8443/hps |URL of the target HPS instance                           |
| -u, --username         | --username=repuser               |Username to log into HPS                                 |
| -p, --password         | --password=topSecret             |Password to log into HPS                                 |
| -n, --num-jobs         | --num-jobs=50                    | Number of design points to generate                     |
| -m, --num-modes        | --num-modes=3                    | Number of lowest Eigenfrequencies to calculate          |
| -f, --target-frequency | --target-frequency=100.0         | Frequency [Hz] to target for the lowest cantilever mode |
| -s, --split-tasks      | --split-tasks                    | Split each step into a different task                   |

Furthermore, it defines the following HPS parameters that are accessible via the HPS web interface:

| **Parameter**     | **Description**                                                    |
|-------------------|--------------------------------------------------------------------|
| canti_length      | Length of the cantilever [um]                                      |
| canti_width       | Width of the cantilever [um]                                       |
| canti_thickness   | Thickness of the cantilever [um]                                   |
| arm_cutoff_width  | By how much should the cantilever arm be thinned [um]              |
| arm_cutoff_length | Length of cantilever arm [um]                                      |
| arm_slot_width    | Width of the slot cut into the cantilever arm [um]                 |
| arm_slot          | Whether there is a slot in the cantilever arm                      |
| young_modulus     | Young Modulus of cantilever material [Pa]                          |
| density           | Density of cantilever material [kg/m^3]                            |
| poisson_ratio     | Poisson ratio of cantilever material                               |
| mesh_swept_layers | Number of layers to generate when sweeping the mesh                |
| num_modes         | Number of lowest lying Eigenfrequencies to calculate               |
| popup_plots       | Whether to show popup plots while running (requires a framebuffer) |
| port_geometry     | Port used by the Ansys GeometryService                             |
| port_mesh         | Port used by the Ansys Prime Server                                |
| port_mapdl        | Port used by the Ansys Mechanical APDL service                     |
| freq_mode_i       | Frequency of i-th Eigenmode [Hz], iϵ\{1,...,num_modes\}            |
| clean_venv        | Whether to clean up the (ephemeral) uv venv directory afterwards   |

# Logic of the example

The example is built up of several files; the logic of this organization shall be explained in the 
following.

The script `project_setup.py` orchestrates it all. It sets up a HPS project, uploads files, defines 
parameters and applies settings. All communication with HPS is done via this script.

The folder `exec_scripts` contains the execution scripts used to run the tasks. They all have the 
same basic function: First they write all HPS parameters to a `input_parameters.json` file, then they 
discover the available software and run the desired python script using uv, and finally they fetch 
parameters that may have been written to `output_parameters.json` by the executed python script, and 
send them back to the evaluator. There is an execution script `exec_combined.py` that is used when 
all stages are run in a single task, and three more execution scripts used to split the three stages 
into different tasks.

The folder `eval_scripts` contains the pyAnsys python scripts. There is one `eval_combined.py` script 
that combines all the functionality into one monolithic script, and there are three other eval scripts 
to split the three stages into three successive tasks. Each of the eval scripts first reads in the 
parameters supplied by the execution script in the `input_parameters.json` file, starts a pyAnsys 
service, and then runs the pyAnsys program. For more information on the content on this script, please 
check the pyAnsys documentation.