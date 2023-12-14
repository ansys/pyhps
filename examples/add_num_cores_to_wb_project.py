# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
#
# Exemplary utility script that connects to a WB project and then
# adds a number_of_cores parameter location to to propagate the
# number to the input script.
#

import logging

from ansys.hps.client import REPError
from ansys.hps.client.jms import Client

log = logging.getLogger(__name__)


def main():

    client = Client(
        rep_url="https://dcsv202testing.westeurope.cloudapp.azure.com/dcs",
        username="repadmin",
        password="An5y5_repadmin",
    )
    log.debug(f"Client connected to {client.rep_url}")
    proj = client.get_project("steel_support_img_steps")
    job_def = proj.get_job_definitions(id=1)[0]
    files = proj.get_files()

    wbjn_names = ["wbjn_Workbench_Geometry", "wbjn_Workbench_Solution", "wbjn_Workbench_Project"]
    wbjn_files = []
    for f in files:
        if f.name in wbjn_names:
            wbjn_files.append(f)

    for wbjn in wbjn_files:
        log.debug(f"Addin parameter location rule for number_of_cores value to {wbjn.name}")
        job_def.add_parameter_mapping(
            key_string="number_of_cores",
            tokenizer="=",
            task_definition_property="num_cores",
            file_id=wbjn.id,
        )
    proj.update_job_definitions([job_def])


if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    try:
        main()
    except REPError as e:
        log.error(str(e))
