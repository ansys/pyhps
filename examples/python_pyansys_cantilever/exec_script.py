# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
import shutil

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class PythonExecution(ApplicationExecution):
    def execute(self):
        log.info("Start uv execution script")

        # Identify files
        script_file = next(
            (f for f in self.context.input_files if f["name"].startswith("eval_")), None
        )
        assert script_file, "Python script file missing"
        input_filename = "input_parameters.json"
        output_filename = "output_parameters.json"

        # Use assigned resources
        self.context.parameter_values["num_cores"] = self.context.resource_requirements["num_cores"]
        self.context.parameter_values["memory_b"] = self.context.resource_requirements["memory"]

        # Pass parameters
        with open(input_filename, "w") as in_file:
            json.dump(self.context.parameter_values, in_file, indent=4)

        # Identify applications
        app_uv = next((a for a in self.context.software if a["name"] == "uv"), None)
        # app_xvfb = next((a for a in self.context.software if a["name"] == "Xvfb-run"), None)
        assert app_uv, "Cannot find app uv"

        # Add " around exe if needed for Windows
        exes = {"uv": app_uv["executable"]}
        for k, v in exes.items():
            if " " in v and not v.startswith('"'):
                exes[k] = f'"{v}"'  # noqa

        # Invoke xvfb if available
        # if app_xvfb != None:
        #    exes['uv'] = "pkill Xvfb; " + app_xvfb['executable'] + " " + exes['uv']

        # Use properties from resource requirements
        # None currently

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        ## Run evaluation script
        cmd = f"{exes['uv']} run {script_file['path']} {input_filename}"
        self.run_and_capture_output(cmd, shell=True, env=env)

        # Extract parameters if needed
        try:
            log.debug(f"Loading output parameters from {output_filename}")
            with open(output_filename) as out_file:
                output_parameters = json.load(out_file)
            self.context.parameter_values.update(output_parameters)
            log.debug(f"Loaded output parameters: {output_parameters}")
        except Exception as ex:
            log.info("No output parameters found.")
            log.debug(f"Failed to read output parameters from file: {ex}")

        # Clean up venv cache
        if "exe" in output_parameters.keys() and self.context.parameter_values.get("clean_venv"):
            try:
                venv_cache = os.path.abspath(os.path.join(output_parameters["exe"], "..", ".."))
                venv_cache_parent = os.path.join(venv_cache, "..")
                if os.path.exists(venv_cache):
                    log.debug(f"Current venv cache: {os.listdir(venv_cache_parent)}")
                    log.debug(f"Cleaning venv cache at {venv_cache}...")
                    shutil.rmtree(venv_cache)
                else:
                    log.debug(f"Venv cache path {venv_cache} does not exist.")
            except Exception as ex:
                log.debug(f"Couldn't clean venv cache at {venv_cache}: {ex}")

        log.info("End Python execution script")
