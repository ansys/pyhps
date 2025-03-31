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

"""
Simplistic execution script for Python.

Command formed: python <script_file> <input_file (optional)>
"""

import json
import os

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


def subscript_enabled(path):
    lines = open(path).readlines()

    for line in lines:
        if line.startswith("CALL_SUBSCRIPT = True"):
            return True
        elif line.startswith("CALL_SUBSCRIPT = False"):
            return False
    return False


class PythonExecution(ApplicationExecution):
    def execute(self):
        log.info("Start Python execution script")

        # Identify files
        script_file = next((f for f in self.context.input_files if "_pyscript" in f["name"]), None)
        assert script_file, "Python evaluation script missing"
        task_definition = script_file["name"].split("_")[0][2:]

        parameters = self.context.parameter_values

        param_transfer = parameters["param_transfer"]
        image_flag = "--images" if parameters["images"] else ""

        # Write input params into file if needed
        if param_transfer == "json-file":
            with open("input_parameters.json", "w") as in_file:
                json.dump(parameters, in_file, indent=4)
            # Write into subscript input file if needed
            if subscript_enabled(script_file["path"]):
                log.debug("Writing subscript input file")
                data = {
                    "color": "white",
                    "period": 2,
                    "duration": 8,
                    "info": f"# changed for task ID: {self.context.task['task_id']}\
                      task {script_file['name']}",
                }
                sub_input_file = f"sub_td{task_definition}_input.json"
                with open(sub_input_file, "w") as in_file:
                    json.dump(data, in_file, indent=4)
                log.debug(f"Wrote to {sub_input_file}")

        elif param_transfer == "mapping":
            inp_file = next((f for f in self.context.input_files if "_input" in f["name"]), None)

        # Identify application
        app_name = "Python"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = f'"{exe}"'
        # Use properties from resource requirements
        # None currently

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Form command
        cmd = f"{exe} {script_file['path']}"
        if parameters["param_transfer"] == "mapping":
            cmd += f" {inp_file['path']}"
        else:
            cmd += " input_parameters.json"
        cmd += f" {task_definition} {image_flag}"

        # Execute
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract parameters if needed
        if param_transfer == "json-file":
            try:
                log.debug("Reading output of evaluation script...")
                with open("output_parameters.json") as out_file:
                    output_parameters = json.load(out_file)
                self.context.parameter_values.update(output_parameters)
            except Exception as ex:
                log.error(f"Failed to read output_parameters from file: {ex}")
            try:
                os.remove("output_parameters.json")
                os.remove("input_parameters.json")
            except Exception as ex:
                log.error(f"Failed to clean up: {ex}")

        log.info("End Python execution script")
