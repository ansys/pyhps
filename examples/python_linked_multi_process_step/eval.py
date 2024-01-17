# Copyright (C) 2021 by
# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

"""
"""
import argparse
import json
import logging
import os
import sys

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
