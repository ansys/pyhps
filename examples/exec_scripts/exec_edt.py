"""
Electronics Desktop execution script
"""
import os
import shlex
import subprocess

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution
import json

class EDTExecution(ApplicationExecution):
    def execute(self):

        log.info("Starting EDT execution script")

        # Identify files
        inp_file = next((f for f in self.context.input_files if f["name"] == "aedtz"), None)
        assert inp_file, "Input file inp missing"
        res_file = next((f for f in self.context.output_files if f["name"] == "results"), None)
        assert inp_file, "Result file missing"

        # Identify application
        app_name = "Ansys Electronics Desktop"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        exe = app["executable"]

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Handle context
        log.debug(f"EX: {self.context.execution_context}")
        batchopts = [f"'{k}'='{1 if v==True else v}'" for k, v in self.context.execution_context.items() if v]
        log.debug(f"Batch opts: {batchopts}")

        # Form command
        cmd = [exe, '-ng', '-batchsolve', '-archiveoptions', 'repackageresults',  '-batchoptions', ' '.join(batchopts), inp_file['path']]

        # Execute command
        log.info(f"Running: {cmd}")
        subprocess.run(cmd, capture_output=True, env=env)
        log.info(f"Command is done")

        # Rename the overwritten aedtz file to whatever was specified in the project definition (the default is results.aedtz)
        os.rename(inp_file['path'], res_file['path'])
