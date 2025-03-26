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
        script_file = next((f for f in self.context.input_files if f["name"] == "script"), None)
        assert script_file, "Python script file script missing"
        inp_file = next((f for f in self.context.input_files if f["name"] == "inp"), None)

        param_transfer = self.context.parameter_values["param_transfer"]
        parameters = self.context.parameter_values
        # Write input params into file if needed
        if param_transfer == "json-file":
            param_name_to_label = {
                "height": "H",
                "diameter": "d",
                "thickness": "t",
                "separation_distance": "B",
                "young_modulus": "E",
                "density": "rho",
                "load": "P",
            }
            input_parameters = {
                param_name_to_label[name]: value
                for name, value in parameters.items()
                if name in param_name_to_label.keys()
            }
            with open("input_parameters.json", "w") as in_file:
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
        cmd = f"{exe} {script_file['path']}"
        if parameters["param_transfer"] == "mapping":
            cmd += f" {inp_file['path']}"
        else:
            cmd += f" input_parameters.json"

        # Execute
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract parameters if needed
        if param_transfer == "json-file":
            try:
                with open("output_parameters.json", "r") as out_file:
                    output_parameters = json.load(out_file)
                self.context.parameter_values.update(output_parameters)
                os.remove("output_parameters.json")
            except Exception as ex:
                log.error("Failed to read output_parameters from file: {ex}")

        log.info("End Python execution script")
