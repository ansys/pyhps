"""
Simplistic execution script for Python.

Command formed: python <script_file> <input_file>
"""
import os
import subprocess

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class PythonExecution(ApplicationExecution):
    def execute(self):

        log.info("Start Python execution script")

        # Identify files
        script_file = next((f for f in self.context.input_files if f["name"] == "script"), None)
        assert script_file, "Python script file script missing"
        inp_file = next((f for f in self.context.input_files if f["name"] == "inp"), None)
        assert inp_file, "Input file inp missing"

        # Identify application
        app_name = "Python"
        app = next((a for a in self.context.software if a["name"] == app_name), None)
        assert app, f"Cannot find app {app_name}"

        # Add " around exe if needed for Windows
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = '"%s"' % exe

        # Use properties from resource requirements
        # None currently

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # Form command
        cmd = f"{exe} {script_file['path']} {inp_file['path']}"

        # Execute
        log.info(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, check=True, env=env)

        log.info("End Python execution script")
