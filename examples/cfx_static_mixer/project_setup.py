"""
Example script to setup a simple CFX project [TODO: with parameters] in pyrep.

Author(s): O.Koenig
"""

import argparse
import logging
import os
import random

from ansys.rep.client import Client, REPError
from ansys.rep.client import __external_version__ as ansys_version
from ansys.rep.client.jms import (
    File,
    FitnessDefinition,
    FloatParameterDefinition,
    JmsApi,
    Job,
    JobDefinition,
    Licensing,
    ParameterMapping,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    StringParameterDefinition,
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)

def create_project(client, name, num_jobs=20, use_exec_script=False):
    """
    Create a REP project consisting of an ANSYS CFX model.
    """
    jms_api = JmsApi(client)
    log.debug("=== Project")
    proj = Project(name=name, priority=1, active=False)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    files.append(
        File(name="ccl", evaluation_path="runInput.ccl", type="text/plain", src=os.path.join(cwd, "runInput.ccl") )
    )
    files.append(
        File(name="inp", evaluation_path="StaticMixer_001.cfx", type="application/octet-stream", src=os.path.join(cwd, "StaticMixer_001.cfx") )
    )
    files.append(
        File(name="def", evaluation_path="StaticMixer_001.def", type="application/octet-stream", src=os.path.join(cwd, "StaticMixer_001.def") )
    )

    if use_exec_script:
        # Define and upload an exemplary exec script to run CFX solver
        files.append(
            File(name="exec_cfx", evaluation_path="exec_cfx.py", type="application/x-python-code", src=os.path.join(cwd, "..", "exec_scripts", "exec_cfx.py") )
        )

    files.append(
        File(name="out", evaluation_path="StaticMixer_*.out", type="text/plain", collect=True, monitor=True)
    )
    files.append(
        File(name="res", evaluation_path="StaticMixer_*.res", type="text/plain", collect=True, monitor=False)
    )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    float_input_params = []

    stat_params = []
    # EXAMPLE: Collect some runtime stats from Fluent transcript file
    #stat_params.append(FloatParameterDefinition(name="mapdl_elapsed_time_obtain_license"))
    #stat_params = project_api.create_parameter_definitions(stat_params)

    param_mappings = []
    #param_mappings.append(
    #    ParameterMapping(
    #        key_string="Elapsed time spent obtaining a license",
    #        tokenizer=":",
    #        parameter_definition_id=stat_params[0].id,
    #        file_id=file_ids["out"],
    #    )
    #)

    str_input_params = []

    # Task definition
    num_input_files = 4 if use_exec_script else 3
    task_def = TaskDefinition(
        name="CFX_run",
        software_requirements=[
            Software(name="ANSYS CFX", version="2022 R2") #ansys_version),
        ],
        execution_command="%executable% -b -i %file:inp% -o file.out -np %resource:num_cores%",
        resource_requirements=ResourceRequirements(
            cpu_core_usage=1.0,
            memory=250,
            disk_space=5,
        ),
        execution_level=0,
        execution_context = {
            "cfx_cclFile" : "runInput.ccl",
            "cfx_runName" : "StaticMixer"
        },
        max_execution_time=50.0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:num_input_files]],
        output_file_ids=[f.id for f in files[num_input_files:]],
        success_criteria=SuccessCriteria(
            return_code=0,
            #expressions=["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
            required_output_file_ids=[file_ids["out"]],
            require_all_output_files=False,
        ),
        licensing=Licensing(enable_shared_licensing=False),  # Shared licensing disabled by default
    )

    if use_exec_script:
        task_def.use_execution_script = True
        task_def.execution_command = None
        task_def.execution_script_id = file_ids["exec_cfx"]

    task_defs = [task_def]

    # EXAMPLE: Fitness definition
    #fd = FitnessDefinition(error_fitness=10.0)
    #fd.add_fitness_term(
    #    name="weight",
    #    type="design_objective",
    #    weighting_factor=1.0,
    #    expression="map_design_objective( values['weight'], 7.5, 5.5)",
    #)
    #job_def.fitness_definition = fd

    task_defs = project_api.create_task_definitions(task_defs)
    param_mappings = project_api.create_parameter_mappings(param_mappings)

    output_params = []

    job_def.parameter_definition_ids = [
        pd.id for pd in float_input_params + str_input_params + output_params + stat_params
    ]
    job_def.parameter_mapping_ids = [pm.id for pm in param_mappings]
    job_def.task_definition_ids = [td.id for td in task_defs]

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    job_def = project_api.get_job_definitions()[0]

    log.debug(f"=== Create {num_jobs} jobs")
    jobs = []
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in float_input_params
        }
        values.update({p.name: random.choice(p.value_list) for p in str_input_params})
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="cfx_static_mixer")
    parser.add_argument("-j", "--num-jobs", type=int, default=1)
    parser.add_argument("-es", "--use-exec-script", default=True, action="store_true")
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to REP JMS")
        client = Client(rep_url=args.url, username=args.username, password=args.password)
        log.info(f"REP URL: {client.rep_url}")
        proj = create_project(
            client=client,
            name=args.name,
            num_jobs=args.num_jobs,
            use_exec_script=args.use_exec_script,
        )

    except REPError as e:
        log.error(str(e))
