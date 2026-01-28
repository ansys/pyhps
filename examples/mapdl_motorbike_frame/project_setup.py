# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Example script to set up a simple MAPDL project with parameters in PyHPS.

Author(s): O.Koenig
"""

import argparse
import logging
import os
import random

import jwt

from ansys.hps.client import Client, HPSError, __ansys_apps_version__
from ansys.hps.client.jms import (
    File,
    FitnessDefinition,
    FloatParameterDefinition,
    HpcResources,
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
from ansys.rep.common.auth.self_signed_token_provider import SelfSignedTokenProvider

log = logging.getLogger(__name__)


def create_project(
    client,
    name,
    version=__ansys_apps_version__,
    num_jobs=20,
    use_exec_script=False,
    active=True,
    one_to_one=False,
) -> Project:
    """Create an HPS project consisting of an ANSYS APDL beam model of a motorbike frame.

    After creating the project job definition, 10 design points with randomly
    chosen parameter values are created and set to pending.

    For more information on the model and its parametrization, see
    "Using Evolutionary Methods with a Heterogeneous Genotype Representation
    for Design Optimization of a Tubular Steel Trellis Motorbike-Frame", 2003
    by U. M. Fasel, O. Koenig, M. Wintermantel and P. Ermanni.
    """
    jms_api = JmsApi(client)
    log.debug("=== Project")
    proj = Project(name=name, priority=1, active=active)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    # File definitions
    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    files.append(
        File(
            name="inp",
            # evaluation_path="headlamp_short_fiber.dat",
            evaluation_path="motorbike_frame.mac",
            type="text/plain",
            # src=os.path.join(cwd, "headlamp_short_fiber.dat"),
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

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_defs = []
    if one_to_one:
        for i in range(num_jobs):
            job_defs.append(JobDefinition(name=f"JobDefinition.{i + 1}", active=True))
    else:
        job_defs.append(JobDefinition(name="JobDefinition.1", active=True))

    # Parameter definitions
    params = []
    # Input params: Dimensions of three custom tubes
    for i in range(1, 4):
        params.extend(
            [
                FloatParameterDefinition(
                    name=f"tube{i}_radius",
                    lower_limit=4.0,
                    upper_limit=20.0,
                    default=12.0,
                    mode="input",
                ),
                FloatParameterDefinition(
                    name=f"tube{i}_thickness",
                    lower_limit=0.5,
                    upper_limit=2.5,
                    default=1.0,
                    mode="input",
                ),
            ]
        )
    # Input params: Custom types used for all the different tubes of the frame
    for i in range(1, 22):
        params.append(
            StringParameterDefinition(
                name=f"tube{i}", default="1", value_list=["1", "2", "3"], mode="input"
            )
        )
    # Output params
    for pname in ["weight", "torsion_stiffness", "max_stress"]:
        params.append(FloatParameterDefinition(name=pname, mode="output"))
    # Runtime stats from MAPDL out file
    params.append(FloatParameterDefinition(name="mapdl_elapsed_time_obtain_license", mode="output"))
    params.append(FloatParameterDefinition(name="mapdl_cp_time", mode="output"))
    params.append(FloatParameterDefinition(name="mapdl_elapsed_time", mode="output"))
    # Create parameter definitions in project
    params = project_api.create_parameter_definitions(params)

    # Parameter mappings
    param_mappings = []
    pi = 0
    for i in range(1, 4):
        param_mappings.append(
            ParameterMapping(
                key_string=f"radius({i})",
                tokenizer="=",
                parameter_definition_id=params[pi].id,
                file_id=file_ids["inp"],
            )
        )
        pi += 1
        param_mappings.append(
            ParameterMapping(
                key_string=f"thickness({i})",
                tokenizer="=",
                parameter_definition_id=params[pi].id,
                file_id=file_ids["inp"],
            )
        )
        pi += 1
    for i in range(1, 22):
        param_mappings.append(
            ParameterMapping(
                key_string=f"tubes({i})",
                tokenizer="=",
                parameter_definition_id=params[pi].id,
                file_id=file_ids["inp"],
            )
        )
        pi += 1
    for name in ["weight", "torsion_stiffness", "max_stress"]:
        param_mappings.append(
            ParameterMapping(
                key_string=name,
                tokenizer="=",
                parameter_definition_id=params[pi].id,
                file_id=file_ids["results"],
            )
        )
        pi += 1
    param_mappings.append(
        ParameterMapping(
            key_string="Elapsed time spent obtaining a license",
            tokenizer=":",
            parameter_definition_id=params[pi].id,
            file_id=file_ids["out"],
        )
    )
    pi += 1
    param_mappings.append(
        ParameterMapping(
            key_string="CP Time      (sec)",
            tokenizer="=",
            parameter_definition_id=params[pi].id,
            file_id=file_ids["out"],
        )
    )
    pi += 1
    param_mappings.append(
        ParameterMapping(
            key_string="Elapsed Time (sec)",
            tokenizer="=",
            parameter_definition_id=params[pi].id,
            file_id=file_ids["out"],
        )
    )
    # For demonstration purpose we also define some parameter replacements
    # that refer to task definition properties
    param_mappings.append(
        ParameterMapping(
            key_string="name",
            tokenizer="=",
            string_quote="'",
            task_definition_property="name",
            file_id=file_ids["inp"],
        )
    )
    param_mappings.append(
        ParameterMapping(
            key_string="application_name",
            tokenizer="=",
            string_quote="'",
            task_definition_property="software_requirements[0].name",
            file_id=file_ids["inp"],
        )
    )
    param_mappings.append(
        ParameterMapping(
            key_string="num_cores",
            tokenizer="=",
            task_definition_property="num_cores",
            file_id=file_ids["inp"],
        )
    )
    param_mappings.append(
        ParameterMapping(
            key_string="cpu_core_usage",
            tokenizer="=",
            task_definition_property="resource_requirements.num_cores",
            file_id=file_ids["inp"],
        )
    )
    param_mappings = project_api.create_parameter_mappings(param_mappings)
    # Task definition
    task_def = TaskDefinition(
        name="MAPDL_run",
        software_requirements=[
            Software(name="Ansys Mechanical APDL", version=version),
        ],
        execution_command="%executable% -b -i %file:inp% -o file.out -np %resource:num_cores%",
        resource_requirements=ResourceRequirements(
            num_cores=4.0,
            # memory=250 * 1024 * 1024,  # 250 MB
            # disk_space=5 * 1024 * 1024,  # 5 MB
            hpc_resources=HpcResources(queue="amd-96c-384g-hpc"),
        ),
        execution_level=0,
        # max_execution_time=600.0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:1]],
        output_file_ids=[f.id for f in files[1:]],
        success_criteria=SuccessCriteria(
            return_code=0,
            # expressions=["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
            # required_output_file_ids=[file_ids["results"]],
            # require_all_output_files=False,
            # require_all_output_parameters=True,
        ),
        licensing=Licensing(enable_shared_licensing=False),  # Shared licensing disabled by default
    )

    if use_exec_script:
        task_def.use_execution_script = True
        task_def.execution_script_id = file_ids["exec_mapdl"]

    task_defs = [task_def]
    if one_to_one:
        task_defs = task_defs * num_jobs

    task_defs = project_api.create_task_definitions(task_defs)

    # Fitness definition
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
    if one_to_one:
        for idx, jd in enumerate(job_defs):
            # jd.fitness_definition = fd
            # jd.parameter_definition_ids = [pd.id for pd in params]
            # jd.parameter_mapping_ids = [pm.id for pm in param_mappings]
            jd.task_definition_ids = [task_defs[idx].id]
    else:
        # job_defs[0].fitness_definition = fd
        # job_defs[0].parameter_definition_ids = [pd.id for pd in params]
        # job_defs[0].parameter_mapping_ids = [pm.id for pm in param_mappings]
        job_defs[0].task_definition_ids = [td.id for td in task_defs]

    # Create job_definition in project
    job_defs = project_api.create_job_definitions(job_defs)

    log.debug(f"=== Create {num_jobs} jobs")
    jobs = []
    params = project_api.get_parameter_definitions()
    input_float_params = [p for p in params if p.mode == "input" and p.type == "float"]
    input_str_params = [p for p in params if p.mode == "input" and p.type == "string"]
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in input_float_params
        }
        values.update({p.name: random.choice(p.value_list) for p in input_str_params})
        job_def_idx = 0
        if one_to_one:
            job_def_idx = i

        jobs.append(
            Job(
                name=f"Job.{i}",
                values=values,
                eval_status="pending",
                job_definition_id=job_defs[job_def_idx].id,
            )
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Mapdl Motorbike Frame")
    parser.add_argument("-j", "--num-jobs", type=int, default=50)
    parser.add_argument("-es", "--use-exec-script", default=False, action="store_true")
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)
    parser.add_argument("-t", "--token", default=None)
    parser.add_argument("-a", "--account", default="onprem_account")
    parser.add_argument("-s", "--signing_key", default="")
    parser.add_argument(
        "-o", "--one-to-one", action="store_true", help="Use one-to-one task definition mapping"
    )
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    if args.token:
        if args.signing_key:
            payload = jwt.decode(
                args.token, algorithms=["RS256"], options={"verify_signature": False}
            )
            user_id = payload["sub"]
            log.debug(f"Found user_id from token: {payload['sub']}")
            provider = SelfSignedTokenProvider({"hps-default": args.signing_key})
            extra = {"preferred_username": user_id}
            # extra = {"account_admin": True, "oid": user_id}
            token = provider.generate_signed_token(user_id, user_id, args.account, 6000, extra)
            log.debug(f"Token: {token}")
        else:
            token = args.token

        client = Client(url=args.url, access_token=token)
        client.session.headers.update({"accountid": args.account})
    else:
        client = Client(url=args.url, username=args.username, password=args.password)

    try:
        log.info(f"HPS URL: {client.url}")
        proj = create_project(
            client=client,
            name=args.name,
            version=args.ansys_version,
            num_jobs=args.num_jobs,
            use_exec_script=args.use_exec_script,
            one_to_one=args.one_to_one,
        )

    except HPSError as e:
        log.error(str(e))
