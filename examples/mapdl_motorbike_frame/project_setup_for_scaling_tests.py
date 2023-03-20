"""
Alternative script to setup a simple MAPDL project with parameters in pyrep
used for scalability tests for number of projects, job definitions and jobs

Author(s): O.Koenig
"""

import argparse
import logging
import os
import random

from ansys.rep.client import Client, REPError, __external_version__
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


def create_project(
    client, name, version=__external_version__, num_job_defs=1, num_jobs=20, use_exec_script=False
) -> Project:
    """
    Create a REP project consisting of an ANSYS APDL beam model of a motorbike-frame.

    After creating the project job_definition, 10 design points with randomly
    chosen parameter values are created and set to pending.

    For further details about the model and its parametrization, see e.g.
    "Using Evolutionary Methods with a Heterogeneous Genotype Representation
    for Design Optimization of a Tubular Steel Trellis Motorbike-Frame", 2003
    by U. M. Fasel, O. Koenig, M. Wintermantel and P. Ermanni.
    """
    jms_api = JmsApi(client)
    log.debug("=== Project")
    proj = Project(
        name=f"{name} JD{num_job_defs} J{num_jobs}",
        priority=1,
        active=True,
    )
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    files.append(
        File(
            name="inp",
            evaluation_path="motorbike_frame.mac",
            type="text/plain",
            src=os.path.join(cwd, "motorbike_frame.mac"),
        )
    )
    files.append(
        File(
            name="results",
            evaluation_path="motorbike_frame_results.txt",
            type="text/plain",
            src=os.path.join(cwd, "motorbike_frame_results.txt"),
        )
    )
    files.append(
        File(name="out", evaluation_path="file.out", type="text/plain", collect=True, monitor=True)
    )
    files.append(File(name="img", evaluation_path="**.jpg", type="image/jpeg", collect=True))
    files.append(
        File(name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True)
    )

    # Alternative, not recommended way, will collect ALL files matching file.*
    # files.append( File( name="all_files", evaluation_path="file.*", type="text/plain") )

    if use_exec_script:
        # Define and upload an exemplary exec script to run MAPDL
        files.append(
            File(
                name="exec_mapdl",
                evaluation_path="exec_mapdl.py",
                type="application/x-python-code",
                src=os.path.join(cwd, "exec_mapdl.py"),
            )
        )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.info("=== Parameter definitions")
    # Todo: Failed to create parameter definitions and mappings at once for all job definitions,
    all_float_input_params = []
    all_str_input_params = []
    all_output_params = []
    all_param_mappings = []
    for i in range(num_job_defs):
        # Input parameter definitions

        # Dimensions of three custom tubes - float params
        param_props = []
        params = []
        param_mappings = []
        for i in range(1, 4):
            p = FloatParameterDefinition(
                name=f"tube{i}_radius", lower_limit=4.0, upper_limit=20.0, default=12.0
            )
            param_props.append({"name": p.name, "key_string": f"radius({i})"})
            params.append(p)
            p = FloatParameterDefinition(
                name=f"tube{i}_thickness", lower_limit=0.5, upper_limit=2.5, default=1.0
            )
            param_props.append({"name": p.name, "key_string": f"thickness({i})"})
            params.append(p)

        params = project_api.create_parameter_definitions(params)
        all_float_input_params.append(params)

        # Input parameter mappings
        for pd, pr in zip(params, param_props):
            assert pd.name == pr["name"]
            param_mappings.append(
                ParameterMapping(
                    key_string=pr["key_string"],
                    tokenizer="=",
                    parameter_definition_id=pd.id,
                    file_id=file_ids["inp"],
                )
            )

        # Custom types used for all the different tubes of the frame - string parameter
        param_props = []
        params = []
        for i in range(1, 22):
            p = StringParameterDefinition(name=f"tube{i}", default="1", value_list=["1", "2", "3"])
            param_props.append({"name": p.name, "key_string": f"tubes({i})"})
            params.append(p)

        params = project_api.create_parameter_definitions(params)
        all_str_input_params.append(params)

        # Input parameter mappings
        for pd, pr in zip(params, param_props):
            assert pd.name == pr["name"]
            param_mappings.append(
                ParameterMapping(
                    key_string=pr["key_string"],
                    tokenizer="=",
                    parameter_definition_id=pd.id,
                    file_id=file_ids["inp"],
                )
            )

        # Output Params
        params = []

        # Collect some runtime stats from MAPDL out file
        param_props = [
            {
                "name": "mapdl_elapsed_time_obtain_license",
                "key_string": "Elapsed time spent obtaining a license",
                "tokenizer": ":",
                "fname": "out",
            },
            {
                "name": "mapdl_cp_time",
                "key_string": "CP Time      (sec)",
                "tokenizer": "=",
                "fname": "out",
            },
            {
                "name": "mapdl_elapsed_time",
                "key_string": "Elapsed Time (sec)",
                "tokenizer": "=",
                "fname": "out",
            },
        ]
        for pr in param_props:
            params.append(FloatParameterDefinition(name=pr["name"]))

        # Design variables
        for pname in ["weight", "torsion_stiffness", "max_stress"]:
            params.append(FloatParameterDefinition(name=pname))
            param_props.append(
                {"name": pname, "key_string": pname, "tokenizer": "=", "fname": "results"}
            )

        params = project_api.create_parameter_definitions(params)
        all_output_params.append(params)

        # Output parameter mappings
        for pd, pr in zip(params, param_props):
            assert pd.name == pr["name"]
            param_mappings.append(
                ParameterMapping(
                    key_string=pr["key_string"],
                    tokenizer=pr["tokenizer"],
                    parameter_definition_id=pd.id,
                    file_id=file_ids[pr["fname"]],
                )
            )

        all_param_mappings.append(project_api.create_parameter_mappings(param_mappings))

    # # Fitness definition
    fd = FitnessDefinition(error_fitness=10.0)
    fd.add_fitness_term(
        name="weight",
        type="design_objective",
        weighting_factor=1.0,
        expression="map_design_objective( values['weight'], 7.5, 5.5)",
    )
    fd.add_fitness_term(
        name="torsional_stiffness",
        type="target_constraint",
        weighting_factor=1.0,
        expression="map_target_constraint( values['torsion_stiffness'], 1313.0, 5.0, 30.0 )",
    )
    fd.add_fitness_term(
        name="max_stress",
        type="limit_constraint",
        weighting_factor=1.0,
        expression="map_limit_constraint( values['max_stress'], 451.0, 50.0 )",
    )

    task_defs = []
    for i in range(num_job_defs):
        # Task definition
        task_def = TaskDefinition(
            name=f"MAPDL_run",
            software_requirements=[
                Software(name="Ansys Mechanical APDL", version=version),
            ],
            execution_command="%executable% -b -i %file:inp% -o file.out -np %resource:num_cores%",
            resource_requirements=ResourceRequirements(
                cpu_core_usage=1.0,
                memory=250,
                disk_space=5,
            ),
            execution_level=0,
            max_execution_time=50.0,
            num_trials=1,
            input_file_ids=[f.id for f in files[:1]],
            output_file_ids=[f.id for f in files[1:]],
            success_criteria=SuccessCriteria(
                return_code=0,
                expressions=["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
                required_output_file_ids=[file_ids["results"]],
                require_all_output_files=False,
                require_all_output_parameters=True,
            ),
            licensing=Licensing(
                enable_shared_licensing=False
            ),  # Shared licensing disabled by default
        )

        if use_exec_script:
            task_def.use_execution_script = True
            task_def.execution_script_id = file_ids["exec_mapdl"]

        task_defs.append(task_def)

    # Create all task definitions at once
    task_defs = project_api.create_task_definitions(task_defs)

    job_defs = []
    for i in range(num_job_defs):
        job_def = JobDefinition(name=f"JobDefinition {i}", active=True)
        job_def.fitness_definition = fd
        job_def.parameter_definition_ids = [
            pd.id
            for pd in all_float_input_params[i] + all_str_input_params[i] + all_output_params[i]
        ]
        job_def.parameter_mapping_ids = [pm.id for pm in all_param_mappings[i]]
        job_def.task_definition_ids = [task_defs[i].id]
        job_defs.append(job_def)

    # Create all job definitions in project at once
    job_defs = project_api.create_job_definitions(job_defs)

    jobs = []
    for i in range(num_job_defs):
        for j in range(num_jobs):
            values = {
                p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
                for p in all_float_input_params[0]
            }
            values.update({p.name: random.choice(p.value_list) for p in all_str_input_params[0]})
            jobs.append(
                Job(
                    name=f"Job.{j}",
                    values=values,
                    eval_status="pending",
                    job_definition_id=job_defs[i].id,
                )
            )

    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Mapdl Motorbike Frame")
    parser.add_argument("-pr", "--num-projects", type=int, default=5)
    parser.add_argument("-jd", "--num-job-defs", type=int, default=5)
    parser.add_argument("-j", "--num-jobs", type=int, default=5)
    parser.add_argument("-es", "--use-exec-script", default=False, action="store_true")
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-v", "--ansys-version", default=__external_version__)
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to REP JMS")
        client = Client(rep_url=args.url, username=args.username, password=args.password)
        log.info(f"REP URL: {client.rep_url}")
        for i in range(args.num_projects):
            name = f"{args.name} P{i}"
            proj = create_project(
                client=client,
                name=name,
                version=args.ansys_version,
                num_job_defs=args.num_job_defs,
                num_jobs=args.num_jobs,
                use_exec_script=args.use_exec_script,
            )

    except REPError as e:
        log.error(str(e))
