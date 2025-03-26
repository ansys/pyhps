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

import logging

from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import Algorithm, Job, JobDefinition, JobSelection, Project
from marshmallow.utils import missing

log = logging.getLogger(__name__)


def test_algorithms(client):
    log.debug("=== Client ===")
    client = client
    jms_api = JmsApi(client)
    proj_name = "rep_client_test_jms_AlgorithmsTest"

    proj = Project(name=proj_name, active=True)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    job_def = JobDefinition(name="New Config", active=True)
    job_def = project_api.create_job_definitions([job_def])[0]

    # Create some Jobs
    jobs = [
        Job(name=f"dp_{i}", eval_status="inactive", job_definition_id=job_def.id) for i in range(10)
    ]
    jobs = project_api.create_jobs(jobs)

    # Create selections with some jobs
    sels = [JobSelection(name="selection_0", jobs=[dp.id for dp in jobs[0:5]])]
    sels.append(JobSelection(name="selection_1", jobs=[dp.id for dp in jobs[5:]]))
    for sel in sels:
        assert len(sel.jobs) == 5
        assert sel.algorithm_id == missing

    project_api.create_job_selections(sels)
    sels = project_api.get_job_selections(fields="all")
    for sel in sels:
        assert len(sel.jobs) == 5
        assert sel.algorithm_id is None
        assert sel.created_by is not missing
        assert sel.creation_time is not missing
        assert sel.modified_by is not missing
        assert sel.modification_time is not missing
        assert sel.created_by == sel.modified_by

    # Create an algorithm
    algo = Algorithm(name="new_algo")
    assert algo.data == missing
    assert algo.description == missing
    assert algo.jobs == missing

    algo = project_api.create_algorithms([algo])[0]
    assert len(algo.jobs) == 0
    assert algo.data is None
    assert algo.description is None
    assert algo.created_by is not missing
    assert algo.creation_time is not missing
    assert algo.modified_by is not missing
    assert algo.modification_time is not missing
    assert algo.created_by == algo.modified_by

    # Link jobs to algorithm
    algo.jobs = [j.id for j in jobs]
    algo = project_api.update_algorithms([algo])[0]
    assert len(algo.jobs) == 10

    # Link selections to algorithm
    for sel in sels:
        sel.algorithm_id = algo.id
    sels = project_api.update_job_selections(sels)

    # Query algorithm selections
    sels = project_api.get_job_selections(algorithm_id=algo.id)
    for sel in sels:
        assert len(sel.jobs) == 5

    # Query algorithm design points
    jobs = project_api.get_jobs(algorithm_id=algo.id)
    assert len(jobs) == 10

    # Update algorithm
    algo.description = "testing algorithm"
    algo.data = "data"
    algo_id = algo.id
    project_api.update_algorithms([algo])
    algo = project_api.get_algorithms(id=algo_id)[0]
    assert algo.description == "testing algorithm"
    assert algo.data == "data"

    # Delete some design points
    job_ids = [jobs[0].id, jobs[1].id, jobs[6].id, jobs[7].id]
    project_api.delete_jobs([Job(id=f"{j_id}") for j_id in job_ids])
    assert len(project_api.get_jobs()) == 6

    # Delete project
    jms_api.delete_project(proj)
