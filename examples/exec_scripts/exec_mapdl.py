"""
Basic execution script for MAPDL.

Command formed: ansys.exe -b -i <inp_file> -o <out_file> -np 4

"""

import json
import subprocess

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class MAPDLExecution(ApplicationExecution):
    def execute(self):

        # Dump whole context to file for debugging
        context_d = json.dumps(vars(self.context), indent=4, default=str)
        with open("context.txt", "w") as f:
            f.write(context_d)

        # Identify files
        inp_file = next((f for f in self.context.input_files if f["name"] == "inp"), None)
        assert inp_file, "Input file inp missing"
        out_file = next((f for f in self.context.output_files if f["name"] == "out"), None)
        assert out_file, "Output file out missing"

        # Identify application
        app_name = "ANSYS Mechanical APDL"
        app = next((a for a in self.context.applications if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = '"%s"' % exe

        # Use properties from resource requirements
        num_cores = self.context.resource_requirements["num_cores"]

        # Form command
        cmd = f"{exe} -b -i {inp_file['path']} -o {out_file['path']} -np {num_cores}"

        # Execute command
        log.info(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
