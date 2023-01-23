"""
Example to query resources from a project.

- Query values from evaluated jobs, computing some simple statistics on parameter values.
- Download files from the project

"""
import argparse
import logging

from ansys.rep.client import Client, REPError
from ansys.rep.client.jms import JmsApi, ProjectApi

log = logging.getLogger(__name__)


def modify_task_definitions(client, project_name):
    """Example to modify task definition of a project"""

    jms_api = JmsApi(client)
    log.info("=== Project")
    project = jms_api.get_project_by_name(name=project_name)
    log.info(f"ID: {project.id}")
    log.info(f"Created on: {project.creation_time}")

    log.info("=== Modify task definitions of project")
    project_api = ProjectApi(client, project.id)

    log.info("Add a custom requirement")
    task_defs = project_api.get_task_definitions(fields=["id", "resource_requirements"])
    for td in task_defs:
        log.info(f"Original task definition: {td}")
        #log.info(f"custom={td.resource_requirements.custom}")

        # In case there are no custom requirements yet
        if not td.resource_requirements.custom:
            td.resource_requirements.custom = {}

        # Just as an example we add a custom target_task_definition field,
        # temporarily used in scaling experiments.
        td.resource_requirements.custom = {"target_task_definition": td.id}

    project_api.update_task_definitions(task_defs)

    # Verify the custom task definitions are set
    task_defs = project_api.get_task_definitions(fields=["id", "resource_requirements"])
    for td in task_defs:
        log.info(f"Modified task definition: {td}")
        assert "target_task_definition" in td.resource_requirements.custom.keys()
        assert td.resource_requirements.custom["target_task_definition"] == td.id

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Mapdl Motorbike Frame")
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

        modify_task_definitions(client=client, project_name=args.name)

    except REPError as e:
        log.error(str(e))
