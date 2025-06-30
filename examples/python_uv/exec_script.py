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

"""Simplistic execution script for Python with uv.

Command formed: uv run <script_file> <input_file>
"""

import json
import os

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class PythonExecution(ApplicationExecution):
    def execute(self):
        log.info("Start uv execution script")

        # Identify files
        script_file = next((f for f in self.context.input_files if f["name"] == "eval"), None)
        assert script_file, "Python script file missing"
        output_filename = "output_parameters.json"

        # Identify applications
        app_uv = next((a for a in self.context.software if a["name"] == "uv"), None)
        assert app_uv, "Cannot find app uv"

        # Add " around exe if needed for Windows
        exes = {"uv": app_uv["executable"]}
        for k, v in exes.items():
            if " " in v and not v.startswith('"'):
                exes[k] = f'"{v}"'  # noqa

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        ## Run evaluation script
        cmd = f"{exes['uv']} run {script_file['path']}"
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract parameters if needed
        output_parameters = {}
        try:
            log.debug(f"Loading output parameters from {output_filename}")
            with open(output_filename) as out_file:
                output_parameters = json.load(out_file)
            self.context.parameter_values.update(output_parameters)
            log.debug(f"Loaded output parameters: {output_parameters}")
        except Exception as ex:
            log.info("No output parameters found.")
            log.debug(f"Failed to read output_parameters from file: {ex}")

        log.info("End Python execution script")
