# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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
Basic execution script for MAPDL.

Command formed: ansys.exe -b -i <inp_file> -o <out_file> -np 4

"""
import os
import subprocess

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class MAPDLExecution(ApplicationExecution):
    class Meta(ApplicationExecution.Meta):
        available_commands = ["interrupt", "command_with_parameters"]

    def execute(self):

        log.info("Start of MAPDL execution script.")

        # Identify files
        inp_file = next((f for f in self.context.input_files if f["name"] == "inp"), None)
        assert inp_file, "Input file inp missing"
        out_file = next((f for f in self.context.output_files if f["name"] == "out"), None)
        assert out_file, "Output file out missing"

        # Identify application
        app_name = "Ansys Mechanical APDL"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = '"%s"' % exe

        # Use properties from resource requirements
        num_cores = self.context.resource_requirements["num_cores"]

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Form command
        cmd = f"{exe} -b -i {inp_file['path']} -o {out_file['path']} -np {num_cores}"

        # Execute command
        log.info(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, check=True, env=env)

        log.info("End of MAPDL execution script.")

    def interrupt(self):
        log.info("Interrupting MAPDL.")
        with open("file.abt", "w") as file:
            file.write("nonlinear")
        log.info("Created file.abt.")

    def command_with_parameters(self, count: int, message: str):
        if not count or count < 0:
            raise ("count must be greater than zero")

        message = os.path.expandvars(message)
        for c in count:
            log.info(message)
