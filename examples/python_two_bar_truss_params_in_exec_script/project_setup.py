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

"""Python two-bar truss example with direct parameter exchange."""

import argparse
import logging
import os
import random

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import (
    File,
    FitnessDefinition,
    FloatParameterDefinition,
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


def main(client, num_jobs, python_version=None) -> Project:
    """This example demonstrates how parameters can directly be exchanged with the application from within the execution script."""  # noqa
    log.debug("=== Project")
    proj = Project(name="Two-bar Truss Problem", priority=1, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = [
        File(
            name="script",
            evaluation_path="evaluate.py",
            type="text/plain",
            src=os.path.join(cwd, "evaluate.py"),
        ),
    ]
    files.append(
        File(
            name="exec_python",
            evaluation_path="exec_python.py",
            type="application/x-python-code",
            src=os.path.join(cwd, "exec_python.py"),
        )
    )
    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}
    input_file_ids = [file_ids["script"]]

    log.debug("=== Job Definition with simulation workflow and parameters")
    job_def = JobDefinition(
        name="JobDefinition.1",
        active=True,
    )

    # Input params
    params = [
        FloatParameterDefinition(
            name="height", lower_limit=10, upper_limit=100.0, default=30, units="in", mode="input"
        ),
        FloatParameterDefinition(
            name="diameter", lower_limit=0.2, upper_limit=5, default=3, units="in", mode="input"
        ),
        FloatParameterDefinition(
            name="thickness",
            lower_limit=0.03,
            upper_limit=0.6,
            default=0.15,
            units="in",
            mode="input",
        ),
        FloatParameterDefinition(
            name="separation_distance",
            lower_limit=40,
            upper_limit=150,
            default=60,
            units="in",
            mode="input",
        ),
        FloatParameterDefinition(
            name="young_modulus",
            lower_limit=1e6,
            upper_limit=1e8,
            default=3e7,
            units="lbs in^-2",
            mode="input",
        ),
        FloatParameterDefinition(
            name="density",
            lower_limit=0.1,
            upper_limit=0.6,
            default=0.3,
            units="lbs in^-2",
            mode="input",
        ),
        FloatParameterDefinition(
            name="load", lower_limit=1e1, upper_limit=1e5, default=66e3, units="lbs", mode="input"
        ),
    ]
    # Output params
    params.extend(
        [
            FloatParameterDefinition(name="weight", units="lbs", mode="output"),
            FloatParameterDefinition(name="stress", units="ksi", mode="output"),
            FloatParameterDefinition(name="buckling_stress", units="ksi", mode="output"),
            FloatParameterDefinition(name="deflection", units="in", mode="output"),
        ]
    )
    params = project_api.create_parameter_definitions(params)
    job_def.parameter_definition_ids = [o.id for o in params]

    task_def = TaskDefinition(
        name="python_evaluation",
        software_requirements=[Software(name="Python", version=python_version)],
        resource_requirements=ResourceRequirements(
            num_cores=0.5,
        ),
        use_execution_script=True,
        execution_script_id=file_ids["exec_python"],
        execution_level=0,
        max_execution_time=30.0,
        input_file_ids=input_file_ids,
        success_criteria=SuccessCriteria(
            return_code=0,
            require_all_output_parameters=True,
        ),
    )

    task_def = project_api.create_task_definitions([task_def])[0]
    job_def.task_definition_ids = [task_def.id]

    # Fitness definition
    fd = FitnessDefinition(error_fitness=10.0)
    fd.add_fitness_term(
        name="weight",
        type="design_objective",
        weighting_factor=1.0,
        expression="map_design_objective( values['weight'], 35, 20)",
    )
    fd.add_fitness_term(
        name="max_stress",
        type="limit_constraint",
        weighting_factor=1.0,
        expression="map_limit_constraint( values['stress'], 85, 10 )",
    )
    fd.add_fitness_term(
        name="max_deflection",
        type="limit_constraint",
        weighting_factor=1.0,
        expression="map_limit_constraint( values['deflection'], 0.25, 0.05 )",
    )
    job_def.fitness_definition = fd

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh parameters
    params = project_api.get_parameter_definitions(job_def.parameter_definition_ids)

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
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-n", "--num-jobs", type=int, default=50)
    parser.add_argument("-v", "--python-version", default="3.10")

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    client = Client(url=args.url, username=args.username, password=args.password)

    try:
        main(
            client,
            num_jobs=args.num_jobs,
            python_version=args.python_version,
        )
    except HPSError as e:
        log.error(str(e))
