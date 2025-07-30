# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "ansys-hps-client @ git+https://github.com/ansys/pyhps.git@main",
#     "packaging",
#     "typer",
# ]
# ///

import logging
import os
import random
import sys

import typer
from packaging import version

import ansys.hps.client
from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import (
    BoolParameterDefinition,
    File,
    FitnessDefinition,
    FloatParameterDefinition,
    IntParameterDefinition,
    JmsApi,
    Job,
    JobDefinition,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def main(client, num_jobs, num_modes, target_frequency, split_tasks):
    log.debug("=== Create Project")
    jms_api = JmsApi(client)
    tasks_config = "Split" if split_tasks else "Combined"

    proj = jms_api.create_project(
        Project(
            name=f"Cantilever - {num_jobs} Designs - {tasks_config}",
            priority=1,
            active=True,
        ),
        replace=True,
    )
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Define Files")
    # Input files
    cwd = os.path.dirname(__file__)
    step_names = ["geometry", "mesh", "mapdl"]
    if not split_tasks:
        step_names = ["combined"]
    files = []
    for script_type in ["eval", "exec"]:
        for step_name in step_names:
            name = f"{script_type}_{step_name}"
            files.append(
                File(
                    name=f"{name}",
                    evaluation_path=f"{name}.py",
                    type="text/plain",
                    src=os.path.join(cwd, f"{script_type}_scripts", f"{name}.py"),
                )
            )
    # Output files
    files.extend(
        [
            File(
                name="cantilever_geometry",
                evaluation_path="cantilever.x_t",
                collect=True,
                type="text/plain",
            ),
            File(
                name="cantilever_mesh",
                evaluation_path="cantilever.cdb",
                collect=True,
                type="application/cdb",
            ),
        ]
    )
    files.append(
        File(name="canti_plot", evaluation_path="canti_plot.png", collect=True, type="image/png")
    )
    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("== Define Parameters")
    # Input parameters
    params = [
        FloatParameterDefinition(
            name="canti_length",
            lower_limit=20.0,
            upper_limit=1000.0,
            default=350.0,
            units="um",
            mode="input",
        ),
        FloatParameterDefinition(
            name="canti_width",
            lower_limit=10.0,
            upper_limit=500.0,
            default=50,
            units="um",
            mode="input",
        ),
        FloatParameterDefinition(
            name="canti_thickness",
            lower_limit=0.05,
            upper_limit=5.0,
            default=0.5,
            units="um",
            mode="input",
        ),
        FloatParameterDefinition(
            name="arm_cutoff_width",
            lower_limit=0.0,
            upper_limit=250.0,
            default=0.0,
            units="um",
            mode="input",
        ),
        FloatParameterDefinition(
            name="arm_cutoff_length",
            lower_limit=20.0,
            upper_limit=1000.0,
            default=0.0,
            units="um",
            mode="input",
        ),
        FloatParameterDefinition(
            name="arm_slot_width",
            lower_limit=0.0,
            upper_limit=200.0,
            default=0.0,
            units="um",
            mode="input",
        ),
        BoolParameterDefinition(name="arm_slot", default=False, mode="input"),
        FloatParameterDefinition(
            name="young_modulus",
            lower_limit=1e6,
            upper_limit=1e13,
            default=3.0e11,
            units="Pa",
            mode="input",
        ),
        FloatParameterDefinition(
            name="density",
            lower_limit=1e3,
            upper_limit=6e3,
            default=3200,
            units="kg/m^3",
            mode="input",
        ),
        FloatParameterDefinition(
            name="poisson_ratio",
            lower_limit=0.1,
            upper_limit=0.6,
            default=0.23,
            units="",
            mode="input",
        ),
        IntParameterDefinition(
            name="mesh_swept_layers",
            lower_limit=2,
            upper_limit=100,
            default=10,
            units="",
            mode="input",
        ),
        IntParameterDefinition(
            name="num_modes",
            default=num_modes,
            lower_limit=num_modes,
            upper_limit=num_modes,
            units="",
            mode="input",
        ),
        BoolParameterDefinition(name="popup_plots", default=False, mode="input"),
        IntParameterDefinition(name="port_geometry", default=50052, mode="input"),
        IntParameterDefinition(name="port_mesh", default=50052, mode="input"),
        IntParameterDefinition(name="port_mapdl", default=50052, mode="input"),
        BoolParameterDefinition(name="clean_venv", default=True, mode="input"),
    ]
    # Output parameters
    for i in range(num_modes):
        params.append(
            FloatParameterDefinition(name=f"freq_mode_{i + 1}", units="Hz", mode="output")
        )
    params = project_api.create_parameter_definitions(params)

    log.debug("=== Define Tasks")
    if split_tasks:
        task_def_geometry = TaskDefinition(
            name="geometry",
            software_requirements=[Software(name="uv"), Software(name="Ansys GeometryService")],
            resource_requirements=ResourceRequirements(
                num_cores=1.0,
                memory=2 * 1024 * 1024 * 1024,  # 2 GB
                disk_space=500 * 1024 * 1024,  # 500 MB
            ),
            execution_level=0,
            max_execution_time=500.0,
            num_trials=3,
            use_execution_script=True,
            execution_script_id=file_ids["exec_geometry"],
            input_file_ids=[file_ids["eval_geometry"]],
            output_file_ids=[file_ids["cantilever_geometry"], file_ids["canti_plot"]],
            success_criteria=SuccessCriteria(
                return_code=0,
                require_all_output_files=True,
            ),
        )
        task_def_mesh = TaskDefinition(
            name="mesh",
            software_requirements=[Software(name="uv"), Software(name="Ansys Prime Server")],
            resource_requirements=ResourceRequirements(
                num_cores=1.0,
                memory=8 * 1024 * 1024 * 1024,  # 8 GB
                disk_space=500 * 1024 * 1024,  # 500 MB
            ),
            execution_level=1,
            max_execution_time=500.0,
            num_trials=3,
            use_execution_script=True,
            execution_script_id=file_ids["exec_mesh"],
            input_file_ids=[file_ids["eval_mesh"], file_ids["cantilever_geometry"]],
            output_file_ids=[file_ids["cantilever_mesh"]],
            success_criteria=SuccessCriteria(
                return_code=0,
                require_all_output_files=True,
                # hpc_resources=HpcResources(exclusive=True),
            ),
        )
        task_def_mapdl = TaskDefinition(
            name="mapdl",
            software_requirements=[
                Software(name="uv"),
                Software(name="Ansys Mechanical APDL", version="2025 R2"),
            ],
            resource_requirements=ResourceRequirements(
                num_cores=2.0,
                memory=8 * 1024 * 1024 * 1024,  # 8 GB
                disk_space=500 * 1024 * 1024,  # 500 MB
                # hpc_resources=HpcResources(exclusive=True),
            ),
            execution_level=2,
            max_execution_time=500.0,
            num_trials=3,
            use_execution_script=True,
            execution_script_id=file_ids["exec_mapdl"],
            input_file_ids=[file_ids["eval_mapdl"], file_ids["cantilever_mesh"]],
            success_criteria=SuccessCriteria(
                return_code=0,
                require_all_output_parameters=True,
            ),
        )
        task_defs = project_api.create_task_definitions(
            [task_def_geometry, task_def_mesh, task_def_mapdl]
        )
    else:
        task_def_combined = TaskDefinition(
            name="combined",
            software_requirements=[
                Software(name="uv"),
                Software(name="Ansys GeometryService"),
                Software(name="Ansys Prime Server"),
                Software(name="Ansys Mechanical APDL", version="2025 R2"),
            ],
            resource_requirements=ResourceRequirements(
                num_cores=2.0,
                memory=8 * 1024 * 1024 * 1024,  # 8 GB
                disk_space=1000 * 1024 * 1024,  # 1 GB
                # hpc_resources=HpcResources(exclusive=True),
            ),
            execution_level=0,
            max_execution_time=1200.0,
            num_trials=3,
            use_execution_script=True,
            execution_script_id=file_ids["exec_combined"],
            input_file_ids=[file_ids["eval_combined"]],
            output_file_ids=[
                file_ids["cantilever_mesh"],
                file_ids["cantilever_geometry"],
                file_ids["canti_plot"],
            ],
            success_criteria=SuccessCriteria(
                return_code=0,
                require_all_output_parameters=True,
                require_all_output_files=True,
            ),
        )
        task_defs = project_api.create_task_definitions([task_def_combined])

    log.debug("== Define Fitness")
    fd = FitnessDefinition(error_fitness=2.0)
    fd.add_fitness_term(
        name="frequency",
        type="target_constraint",
        weighting_factor=1.0,
        expression=f"map_target_constraint(values['freq_mode_1'], \
            {target_frequency}, {0.01 * target_frequency}, {0.5 * target_frequency})",
    )

    log.debug("== Define Job")
    job_def = JobDefinition(
        name="JobDefinition.1",
        active=True,
        parameter_definition_ids=[p.id for p in params],
        task_definition_ids=[td.id for td in task_defs],
        fitness_definition=fd,
    )
    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh parameters
    params = project_api.get_parameter_definitions(job_def.parameter_definition_ids)
    params_by_name = {p["name"]: p for p in params}

    log.debug(f"== Create {num_jobs} Jobs")
    jobs = []
    for i in range(num_jobs):
        values = generate_parameter_values_for_job(i, params_by_name)
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}")
    return proj


def entrypoint(
    url: str = typer.Option("https://localhost:8443/hps", "-U", "--url"),
    username: str = typer.Option("repuser", "-u", "--username"),
    password: str = typer.Option("repuser", "-p", "--password"),
    num_jobs: int = typer.Option(20, "-n", "--num-jobs"),
    num_modes: int = typer.Option(3, "-m", "--num-modes"),
    freq_tgt: float = typer.Option(100.0, "-f", "--target-frequency"),
    split_tasks: bool = typer.Option(False, "-s", "--split-tasks"),
):
    log.debug("Arguments:")
    log.debug(
        f"{url}\n{username}, {password}\njobs: {num_jobs}\nmodes: {num_modes}\nfreq: {freq_tgt}"
    )

    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    client = Client(url=url, username=username, password=password)

    try:
        main(client, num_jobs, num_modes, freq_tgt, split_tasks)
    except HPSError as e:
        log.error(str(e))


def sample_parameter(p, minval=None, maxval=None):
    if minval is None:
        minval = p.lower_limit
    if maxval is None:
        maxval = p.upper_limit
    return minval + random.random() * (maxval - minval)


def generate_parameter_values_for_job(i, params_by_name):
    values = {}
    values["canti_length"] = sample_parameter(params_by_name["canti_length"])
    values["canti_width"] = sample_parameter(params_by_name["canti_width"])
    values["canti_thickness"] = sample_parameter(params_by_name["canti_thickness"])
    values["arm_cutoff_width"] = sample_parameter(None, 0.0, values["canti_width"] / 2.5)
    values["arm_cutoff_length"] = sample_parameter(None, 10.0, values["canti_length"])
    if random.random() > 0.5:
        values["arm_slot"] = True
        values["arm_slot_width"] = sample_parameter(
            None,
            (values["canti_width"] - 2 * values["arm_cutoff_width"]) * 0.2,
            (values["canti_width"] - 2 * values["arm_cutoff_width"]) * 0.25,
        )
    values["port_geometry"] = random.randint(49153, 59999)
    values["port_mesh"] = random.randint(49153, 59999)
    values["port_mapdl"] = random.randint(49153, 59999)
    values["clean_venv"] = True
    return values


if __name__ == "__main__":
    # Verify that ansys-hps-client version is > 0.10.1 to ensure support for unmapped parameters
    if version.parse(ansys.hps.client.__version__) <= version.parse("0.10.1"):
        print(
            f"ERR: ansys-hps-client version {ansys.hps.client.__version__} \
                does not satisfy '>0.10.1'"
        )
        sys.exit(1)
    typer.run(entrypoint)
