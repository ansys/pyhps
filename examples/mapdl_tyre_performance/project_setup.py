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

"""
Example to submit a nonlinear tire analysis job to HPS.

This is the Ansys Parametric Design Language (APDL) Tire Performance Simulation example included
in the technology demonstration guide (td-57).
"""

import argparse
import logging
import os
import random

from ansys.hps.client import Client, HPSError, __ansys_apps_version__
from ansys.hps.client.jms import (
    File,
    FloatParameterDefinition,
    JmsApi,
    Job,
    JobDefinition,
    ParameterMapping,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def create_project(
    client, name, version=__ansys_apps_version__, num_jobs=20, use_exec_script=False, active=True
) -> Project:

    log.debug("=== Project")
    jms_api = JmsApi(client)
    proj = Project(name=name, priority=1, active=True)
    proj = jms_api.create_project(proj)

    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)

    files = [
        File(
            name="inp",
            evaluation_path="tire_performance_simulation.mac",
            type="text/plain",
            src=os.path.join(cwd, "tire_performance_simulation.mac"),
        ),
        File(
            name="geom",
            evaluation_path="2d_tire_geometry.iges",
            type="text/plain",
            src=os.path.join(cwd, "2d_tire_geometry.iges"),
        ),
        File(name="results", evaluation_path="tire_performance_results.txt", type="text/plain"),
        File(name="img", evaluation_path="**.png", type="image/png", collect=True),
        File(name="out", evaluation_path="file.out", type="text/plain", collect=True, monitor=True),
        File(
            name="mntr", evaluation_path="file.mntr", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="cnd",
            evaluation_path="file.cnd",
            type="text/plain",
            collect=True,
            monitor=True,
            collect_interval=30,
        ),
        File(
            name="gst",
            evaluation_path="file.gst",
            type="text/plain",
            collect=True,
            monitor=True,
            collect_interval=30,
        ),
        File(
            name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")

    # Input params
    input_params = [
        FloatParameterDefinition(
            name="camber_angle",
            display_text="Camber Angle",
            lower_limit=-8.0,
            upper_limit=8.0,
            default=0.0,
        ),
        FloatParameterDefinition(
            name="inflation_pressure",
            display_text="Inflation Pressure",
            lower_limit=0.15e06,
            upper_limit=0.3e06,
            default=0.24e06,
        ),
        FloatParameterDefinition(
            name="rotational_velocity",
            display_text="Rotational Velocity",
            lower_limit=0.0,
            upper_limit=70.0,
            default=50.0,
        ),
        FloatParameterDefinition(
            name="translational_velocity",
            display_text="Translational Velocity",
            lower_limit=0.0,
            upper_limit=30.0,
            default=20.0,
        ),
    ]
    input_params = project_api.create_parameter_definitions(input_params)

    param_mappings = [
        ParameterMapping(
            key_string="camber_angle",
            tokenizer="=",
            parameter_definition_id=input_params[0].id,
            file_id=file_ids["inp"],
        ),
        ParameterMapping(
            key_string="inflation_pressure",
            tokenizer="=",
            parameter_definition_id=input_params[1].id,
            file_id=file_ids["inp"],
        ),
        ParameterMapping(
            key_string="rotational_velocity",
            tokenizer="=",
            parameter_definition_id=input_params[2].id,
            file_id=file_ids["inp"],
        ),
        ParameterMapping(
            key_string="translational_velocity",
            tokenizer="=",
            parameter_definition_id=input_params[3].id,
            file_id=file_ids["inp"],
        ),
    ]

    # Output Params

    # Collect some runtime stats from MAPDL out file
    output_params = [
        FloatParameterDefinition(name="mapdl_cp_time", display_text="MAPDL CP Time"),
        FloatParameterDefinition(name="mapdl_elapsed_time", display_text="MAPDL Elapsed Time"),
    ]
    output_params = project_api.create_parameter_definitions(output_params)

    param_mappings.extend(
        [
            ParameterMapping(
                key_string="CP Time      (sec)",
                tokenizer="=",
                parameter_definition_id=output_params[0].id,
                file_id=file_ids["out"],
            ),
            ParameterMapping(
                key_string="Elapsed Time (sec)",
                tokenizer="=",
                parameter_definition_id=output_params[1].id,
                file_id=file_ids["out"],
            ),
        ]
    )
    param_mappings = project_api.create_parameter_mappings(param_mappings)

    # TODO, add more

    task_defs = []
    # Process step
    task_def = TaskDefinition(
        name="MAPDL_run",
        software_requirements=[Software(name="Ansys Mechanical APDL", version=version)],
        execution_command="%executable% -b -i %file:inp% -o file.out -np %resource:num_cores%",
        resource_requirements=ResourceRequirements(
            num_cores=4,
            memory=4000 * 1024 * 1024,
            disk_space=500 * 1024 * 1024,
            distributed=True,
        ),
        max_execution_time=1800.0,
        execution_level=0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:2]],
        output_file_ids=[f.id for f in files[2:]],
    )

    if use_exec_script:
        exec_script_file = project_api.copy_default_execution_script(
            f"mapdl-v{version[2:4]}{version[6]}-exec_mapdl.py"
        )

        task_def.use_execution_script = True
        task_def.execution_script_id = exec_script_file.id

    task_defs.append(task_def)

    task_def = project_api.create_task_definitions(task_defs)[0]

    # Create job_definition in project
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    params = input_params + output_params
    job_def.task_definition_ids = [task_def.id]
    job_def.parameter_definition_ids = [pd.id for pd in params]
    job_def.parameter_mapping_ids = [pm.id for pm in param_mappings]
    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh the parameters
    params = project_api.get_parameter_definitions(id=job_def.parameter_definition_ids)

    log.debug("=== Jobs")
    jobs = []
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in params
            if p.mode == "input"
        }
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Mapdl Tyre Performance")
    parser.add_argument("-j", "--num-jobs", type=int, default=10)
    parser.add_argument("-es", "--use-exec-script", default=False, type=bool)
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== HPS connection")
    client = Client(url=args.url, username=args.username, password=args.password)

    try:
        log.info(f"HPS URL: {client.url}")
        proj = create_project(
            client=client,
            name=args.name,
            version=args.ansys_version,
            num_jobs=args.num_jobs,
            use_exec_script=args.use_exec_script,
        )
    except HPSError as e:
        log.error(str(e))
