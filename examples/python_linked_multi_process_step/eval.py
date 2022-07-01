# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): R.Walker
# ----------------------------------------------------------

"""
"""
import argparse
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main(input_file, task_definition):

    log = logging.getLogger()
    log.info("== Start Evaluation Process Step ==")

    # Read parameters
    log.info(f"Input File: {input_file}")
    log.info(f"Process Step: {task_definition}")
    input_file_path = os.path.abspath(input_file)
    log.info(f"Open input file: {input_file_path}")
    with open(input_file_path, "r") as f:
        params = json.load(f)

    log.info(f"Params read: {params}")
    start = params.get("start", params.get("product", 0.0))
    # Calculate the Output: Number of steps
    product = start * start

    output_parameters = {"product": product}

    # create json-results file
    out_filename = f"td{task_definition}_result.json"
    log.debug(f"Write JSON Results file: {out_filename}")
    with open(out_filename, "w") as out_file:
        json.dump(output_parameters, out_file, indent=4)

    log.info("Finished.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("task_definition", help="The task definition number the script is used in.")
    args = parser.parse_args()

    sys.exit(main(**vars(args)))
