"""
Example to setup a nonlinear tyre analysis job in REP.

Author(s): F.Negri
"""

import argparse
import logging
import os
import random

from ansys.rep.client import REPError
from ansys.rep.client import __external_version__ as ansys_version
from ansys.rep.client.jms import (
    Client,
    File,
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


def main(client, name, num_jobs):
    """
    Create project with Ansys MAPDL tire simulation.

    ANSYS APDL Tire-Performance Simulation example as included
    in the technology demonstration guide (td-57).
    """
    log.debug("=== Project")
    proj = Project(name=name, display_name="MAPDL Tyre Performance", priority=1, active=True)
    proj = client.create_project(proj, replace=True)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    files.append(
        File(
            name="mac",
            evaluation_path="dcs_tire_performance_simulation.mac",
            type="text/plain",
            src=os.path.join(cwd, "dcs_tire_performance_simulation.mac"),
        )
    )
    files.append(
        File(
            name="geom",
            evaluation_path="2d_tire_geometry.iges",
            type="text/plain",
            src=os.path.join(cwd, "2d_tire_geometry.iges"),
        )
    )
    files.append(
        File(name="results", evaluation_path="tire_performance_results.txt", type="text/plain")
    )
    files.append(File(name="img", evaluation_path="**.png", type="image/png", collect=True))
    files.append(
        File(name="out", evaluation_path="file.out", type="text/plain", collect=True, monitor=True)
    )
    files.append(
        File(
            name="mntr", evaluation_path="file.mntr", type="text/plain", collect=True, monitor=True
        )
    )
    files.append(
        File(name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True)
    )

    files = proj.create_files(files)
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
    input_params = proj.create_parameter_definitions(input_params)

    param_mappings = [
        ParameterMapping(
            key_string="camber_angle",
            tokenizer="=",
            parameter_definition_id=input_params[0].id,
            file_id=file_ids["mac"],
        ),
        ParameterMapping(
            key_string="inflation_pressure",
            tokenizer="=",
            parameter_definition_id=input_params[1].id,
            file_id=file_ids["mac"],
        ),
        ParameterMapping(
            key_string="rotational_velocity",
            tokenizer="=",
            parameter_definition_id=input_params[2].id,
            file_id=file_ids["mac"],
        ),
        ParameterMapping(
            key_string="translational_velocity",
            tokenizer="=",
            parameter_definition_id=input_params[3].id,
            file_id=file_ids["mac"],
        ),
    ]

    # Output Params

    # Collect some runtime stats from MAPDL out file
    output_params = [
        FloatParameterDefinition(name="mapdl_cp_time", display_text="MAPDL CP Time"),
        FloatParameterDefinition(name="mapdl_elapsed_time", display_text="MAPDL Elapsed Time"),
    ]
    output_params = proj.create_parameter_definitions(output_params)

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
    param_mappings = proj.create_parameter_mappings(param_mappings)

    # TODO, add more

    # Process step
    task_def = TaskDefinition(
        name="MAPDL_run",
        software_requirements=[Software(name="ANSYS Mechanical APDL", version=ansys_version)],
        execution_command="%executable% -b -i %file:mac% -o file.out -np %resource:num_cores%",
        resource_requirements=ResourceRequirements(
            cpu_core_usage=4,
            memory=4000,
            disk_space=500,
        ),
        max_execution_time=1800.0,
        execution_level=0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:2]],
        output_file_ids=[f.id for f in files[2:]],
    )
    task_def = proj.create_task_definitions([task_def])[0]

    # Create job_definition in project
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    params = input_params + output_params
    job_def.task_definition_ids = [task_def.id]
    job_def.parameter_definition_ids = [pd.id for pd in params]
    job_def.parameter_mapping_ids = [pm.id for pm in param_mappings]
    job_def = proj.create_job_definitions([job_def])[0]

    # Refresh the parameters
    params = proj.get_parameter_definitions(id=job_def.parameter_definition_ids)

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
    parser.add_argument("-n", "--name", type=str, default="mapdl_tyre_performance")
    parser.add_argument("-j", "--num-jobs", type=int, default=1000)
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== DCS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        main(client, name=args.name, num_jobs=args.num_jobs)
    except REPError as e:
        log.error(str(e))
