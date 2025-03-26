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

"""Simplistic execution script for Python.

Command formed: python <script_file> <input_file (optional)>
"""

import json
import os

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class PythonExecution(ApplicationExecution):
    def execute(self):
        log.info("Start Python execution script")

        # Identify files
        script_file = next((f for f in self.context.input_files if "_pyscript" in f["name"]), None)
        assert script_file, "Python script file script missing"
        try:
            exec_level = int(script_file["name"].split("_")[0][2:])
        except Exception as ex:
            log.error(f"Failed to extract execution level from filename {script_file.name}: {ex}")
            exec_level = 0

        # Write input param into file
        parameters = self.context.parameter_values
        if exec_level == 0:
            input_parameters = {"start": parameters.get("start", 0.0)}
        else:
            input_parameters = {
                f"product{exec_level - 1}": parameters.get(f"product{exec_level - 1}", 0.0)
            }

        in_filename = "input_parameters.json"
        with open(in_filename, "w") as in_file:
            json.dump(input_parameters, in_file, indent=4)

        # Identify application
        app_name = "Python"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = '"%s"' % exe  # noqa

        # Use properties from resource requirements
        # None currently

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Form command
        cmd = f"{exe} {script_file['path']} {in_filename} {exec_level}"

        # Execute
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract result
        try:
            with open(f"td{exec_level}_result.json") as out_file:
                output_parameters = json.load(out_file)
            self.context.parameter_values.clear()
            self.context.parameter_values[f"product{exec_level}"] = output_parameters["product"]
            os.remove(f"td{exec_level}_result.json")
        except Exception as ex:
            log.error(f"Failed to read output_parameters from file: {ex}")

        log.info("End Python execution script")
