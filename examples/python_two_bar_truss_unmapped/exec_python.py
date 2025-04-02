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

Command formed: python <script_file> <input_file>
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
        input_filename = "input_parameters.json"
        output_filename = "output_parameters.json"

        with open(input_filename, "w") as in_file:
            json.dump(self.context.parameter_values, in_file, indent=4)

        # Identify application
        app_name = "Python"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = f'"{exe}"'  # noqa

        # Use properties from resource requirements
        # None currently

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Form command
        cmd = f"{exe} {script_file['path']} {input_filename}"

        log.debug(f"Executing command: {cmd}")
        # Execute
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract parameters if needed
        try:
            log.debug(f"Loading output parameters from {output_filename}")
            with open(output_filename) as out_file:
                output_parameters = json.load(out_file)
            self.context.parameter_values.update(output_parameters)
            log.debug(f"Loaded output parameters: {output_parameters}")
        except Exception as ex:
            log.error(f"Failed to read output_parameters from file: {ex}")

        log.info("End Python execution script")
