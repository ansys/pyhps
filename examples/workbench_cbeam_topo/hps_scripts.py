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

"""Example script to set up a simple Ansys Workbench project with parameters in PyHPS.

Author(s): O.Koenig
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
    SuccessCriteria,
    TaskDefinition,
)
from ansys.hps.client.jms.api import project_api

log = logging.getLogger(__name__)


def define_project(project_api, version=__ansys_apps_version__, num_jobs=20) -> Project:
    """Define an HPS project for a simple Ansys Workbench project

    After creating the project job definition, a number of design points with randomly
    chosen parameter values are created and set to pending.
    """

    # File definitions
    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    # Input files
    files.append(
        File(
            name="wbpz",
            evaluation_path="cbeam_topo.wbpz",
            type="application/zip",
            src=os.path.join(cwd, "cbeam_topo.wbpz"),
        )
    )
    files.append(
        File(
            name="script_Workbench_Project",
            evaluation_path="cbeam_topo_Workbench_Project.wbjn",
            type="application/x-python-code",
            src=os.path.join(cwd, "cbeam_topo_Workbench_Project.wbjn"),
        )
    )
    files.append(
        File(
            name="input_parameters",
            evaluation_path="cbeam_topo_input_param.wbjn",
            type="application/x-python-code",
            src=os.path.join(cwd, "cbeam_topo_input_param.wbjn"),
        )
    )

    # Output files
    files.append(
        File(
            name="log_Workbench_Project",
            evaluation_path="cbeam_topo_Workbench_Project_log.txt",
            type="text/plain",
            collect=True,
            monitor=True,
        )
    )
    files.append(
        File(
            name="output_parameters",
            evaluation_path="cbeam_topo_output_param.txt",
            type="text/plain",
            collect=True,
        )
    )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="WBDP", active=True)

    # Parameter definitions
    input_params = [
        FloatParameterDefinition(
            name="P4",
            display_text="Body Sizing Element Size",
            default=15.0,
            mode="input",
            unit="mm",
        ),
        FloatParameterDefinition(
            name="P9", display_text="l", default=60.0, mode="input", unit="mm"
        ),
        FloatParameterDefinition(
            name="P10", display_text="t1", default=40.0, mode="input", unit="mm"
        ),
        FloatParameterDefinition(
            name="P11", display_text="t2", default=40.0, mode="input", unit="mm"
        ),
        FloatParameterDefinition(
            name="P12", display_text="Response Constraint Percentage", default=50.0, mode="input"
        ),
    ]
    input_params = project_api.create_parameter_definitions(input_params)
    param_mappings = []
    for p in input_params:
        param_mappings.append(
            ParameterMapping(
                key_string=f"input_parameters['{p.name}']",
                tokenizer="=",
                parameter_definition_id=p.id,
                file_id=file_ids["input_parameters"],
            )
        )

    output_params = [
        FloatParameterDefinition(name="P5", display_text="Mesh Elements", mode="output"),
        FloatParameterDefinition(name="P6", display_text="Mesh Nodes", mode="output"),
        FloatParameterDefinition(
            name="P15", display_text="Topology Density Percent Mass of Original", mode="output"
        ),
        FloatParameterDefinition(
            name="P14", display_text="Topology Density Final Mass", unit="kg", mode="output"
        ),
        FloatParameterDefinition(
            name="P13", display_text="Topology Density Original Mass", unit="kg", mode="output"
        ),
    ]
    output_params = project_api.create_parameter_definitions(output_params)
    for p in output_params:
        param_mappings.append(
            ParameterMapping(
                key_string=p.name,
                tokenizer="=",
                parameter_definition_id=p.id,
                file_id=file_ids["output_parameters"],
            )
        )

    param_mappings = project_api.create_parameter_mappings(param_mappings)
    params = add_parameter_limits(project_api=project_api)

    # Task definition
    task_def = TaskDefinition(
        name="Workbench Project",
        software_requirements=[
            Software(name="Ansys Workbench", version=version),
        ],
        execution_command=(
            "%executable% -B -R %file:script_Workbench_Project% -Z Rep.EvaluatorRun "
            "--enable-beta --output %file:log_Workbench_Project%"
        ),
        resource_requirements=ResourceRequirements(num_cores=4.0),
        execution_level=0,
        max_execution_time=500.0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:3]],
        output_file_ids=[f.id for f in files[3:]],
        success_criteria=SuccessCriteria(
            return_code=0,
            require_all_output_files=True,
            require_all_output_parameters=True,
        ),
    )

    task_defs = [task_def]
    task_defs = project_api.create_task_definitions(task_defs)

    job_def.parameter_definition_ids = [pd.id for pd in params]
    job_def.parameter_mapping_ids = [pm.id for pm in param_mappings]
    job_def.task_definition_ids = [td.id for td in task_defs]

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    # Add jobs
    add_jobs(project_api, num_jobs)


def add_parameter_limits(project_api):
    """
    To create jobs with random parameter values parameter limits are needed for input parameters
    Hardcoded for now
    """
    param_d = {p.name: p for p in project_api.get_parameter_definitions()}
    param_d["P4"].lower_limit = 10.0
    param_d["P4"].upper_limit = 25.0
    param_d["P9"].lower_limit = 50.0
    param_d["P9"].upper_limit = 100.0
    param_d["P10"].lower_limit = 20.0
    param_d["P10"].upper_limit = 60.0
    param_d["P11"].lower_limit = 20.0
    param_d["P11"].upper_limit = 60.0
    param_d["P12"].lower_limit = 10.0
    param_d["P12"].upper_limit = 60.0

    return project_api.update_parameter_definitions(list(param_d.values()))


def add_jobs(project_api, num_jobs):
    log.debug(f"=== Create {num_jobs} jobs")
    params = project_api.get_parameter_definitions()
    job_def = project_api.get_job_definitions()[0]

    input_params = [p for p in params if p.mode == "input"]
    jobs = []
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in input_params
        }
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Workbench Cbeam Topology Optimization")
    parser.add_argument(
        "-a", "--action", type=str, default="create_project", choices=["create_project", "add_jobs"]
    )
    parser.add_argument("-j", "--num-jobs", type=int, default=50)
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")
        jms_api = JmsApi(client)

        if args.action == "create_project":
            log.info(f"=== Create new project {args.name}")
            proj = Project(name=args.name, priority=1, active=True)
            proj = jms_api.create_project(proj, replace=True)
            project_api = ProjectApi(client, proj.id)
            define_project(
                project_api=project_api, version=args.ansys_version, num_jobs=args.num_jobs
            )
        elif args.action == "add_jobs":
            log.info(f"=== Add jobs to existing project {args.name}")
            proj = jms_api.get_project_by_name(args.name)
            project_api = ProjectApi(client, proj.id)
            add_parameter_limits(project_api=project_api)
            add_jobs(project_api=project_api, num_jobs=args.num_jobs)

        else:
            raise HPSError(f"Invalid action '{args.action}'")

    except HPSError as e:
        log.error(str(e))
