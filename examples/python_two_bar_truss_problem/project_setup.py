# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import argparse
import logging
import os
import random
import sys

from ansys.rep.client import REPError
from ansys.rep.client.jms import (
    Client,
    File,
    FitnessDefinition,
    FloatParameterDefinition,
    Job,
    JobDefinition,
    ParameterMapping,
    Project,
    ResourceRequirements,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def main(client, num_jobs):
    """Example of Python project implementing the Two-Bar Truss example
    from  R.L. Fox, Optimization Methods in Engineering Design, Addison Wesley, 1971
    See e.g. https://static1.squarespace.com/static/53eacd17e4b0588f78eb723c/t/586ea636d482e91c7a76bd61/1483646550748/Optimization+Methods+in+Engineering+Design.pdf
    """

    log.debug("=== Project")
    proj = Project(
        name="two_bar_truss_problem", display_name="Two-bar Truss Problem", priority=1, active=True
    )
    proj = client.create_project(proj, replace=True)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)

    files = []
    files.append(
        File(
            name="input_params",
            evaluation_path="input_parameters.json",
            type="text/plain",
            src=os.path.join(cwd, "input_parameters.json"),
        )
    )
    files.append(
        File(
            name="pyscript",
            evaluation_path="evaluate.py",
            type="text/plain",
            src=os.path.join(cwd, "evaluate.py"),
        )
    )
    files.append(
        File(
            name="results",
            evaluation_path="output_parameters.json",
            type="text/plain",
            collect=True,
        )
    )

    files = proj.create_files(files)

    input_file = files[0]
    result_file = files[2]

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(
        name="job_definition.1",
        active=True,
    )

    # Input params
    input_params = [
        FloatParameterDefinition(
            name="height", lower_limit=10, upper_limit=100.0, default=30, units="in"
        ),
        FloatParameterDefinition(
            name="diameter", lower_limit=0.2, upper_limit=5, default=3, units="in"
        ),
        FloatParameterDefinition(
            name="thickness", lower_limit=0.03, upper_limit=0.6, default=0.15, units="in"
        ),
        FloatParameterDefinition(
            name="separation_distance", lower_limit=40, upper_limit=150, default=60, units="in"
        ),
        FloatParameterDefinition(
            name="young_modulus", lower_limit=1e6, upper_limit=1e8, default=3e7, units="lbs in^-2"
        ),
        FloatParameterDefinition(
            name="density", lower_limit=0.1, upper_limit=0.6, default=0.3, units="lbs in^-2"
        ),
        FloatParameterDefinition(
            name="load", lower_limit=1e1, upper_limit=1e5, default=66e3, units="lbs"
        ),
    ]
    input_params = proj.create_parameter_definitions(input_params)

    mappings = [
        ParameterMapping(
            key_string='"H"',
            tokenizer=":",
            parameter_definition_id=input_params[0].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"d"',
            tokenizer=":",
            parameter_definition_id=input_params[1].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"t"',
            tokenizer=":",
            parameter_definition_id=input_params[2].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"B"',
            tokenizer=":",
            parameter_definition_id=input_params[3].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"E"',
            tokenizer=":",
            parameter_definition_id=input_params[4].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"rho"',
            tokenizer=":",
            parameter_definition_id=input_params[5].id,
            file_id=input_file.id,
        ),
        ParameterMapping(
            key_string='"P"',
            tokenizer=":",
            parameter_definition_id=input_params[6].id,
            file_id=input_file.id,
        ),
    ]

    output_params = [
        FloatParameterDefinition(name="weight", units="lbs"),
        FloatParameterDefinition(name="stress", units="ksi"),
        FloatParameterDefinition(name="buckling_stress", units="ksi"),
        FloatParameterDefinition(name="deflection", units="in"),
    ]
    output_params = proj.create_parameter_definitions(output_params)

    mappings.extend(
        [
            ParameterMapping(
                key_string='"weight"',
                tokenizer=":",
                parameter_definition_id=output_params[0].id,
                file_id=result_file.id,
            ),
            ParameterMapping(
                key_string='"stress"',
                tokenizer=":",
                parameter_definition_id=output_params[1].id,
                file_id=result_file.id,
            ),
            ParameterMapping(
                key_string='"buckling_stress"',
                tokenizer=":",
                parameter_definition_id=output_params[2].id,
                file_id=result_file.id,
            ),
            ParameterMapping(
                key_string='"deflection"',
                tokenizer=":",
                parameter_definition_id=output_params[3].id,
                file_id=result_file.id,
            ),
        ]
    )

    mappings = proj.create_parameter_mappings(mappings)

    job_def.parameter_definition_ids = [o.id for o in input_params + output_params]
    job_def.parameter_mapping_ids = [o.id for o in mappings]

    # Process step
    task_def = TaskDefinition(
        name="python_evaluation",
        software_requirements=[Software(name="Python", version="3.10")],
        execution_command="%executable% %file:pyscript% %file:input_params%",
        resource_requirements=ResourceRequirements(
            cpu_core_usage=0.5,
            memory=100,
            disk_space=5,
        ),
        execution_level=0,
        max_execution_time=30.0,
        input_file_ids=[f.id for f in files[:2]],
        output_file_ids=[f.id for f in files[2:]],
    )
    task_def = proj.create_task_definitions([task_def])[0]
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
    job_def = proj.create_job_definitions([job_def])[0]

    params = proj.get_parameter_definitions(job_def.parameter_definition_ids)

    log.debug("=== Jobs")
    jobs = []
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in params
            if p.mode == "input"
        }
        jobs.append(Job(name=f"Job.{i}", values=values, eval_status="pending"))
    jobs = job_def.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-n", "--num-jobs", type=int, default=1000)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== DCS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        main(client, num_jobs=args.num_jobs)
    except REPError as e:
        log.error(str(e))
