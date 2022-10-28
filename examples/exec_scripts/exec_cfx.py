"""
Copyright (C) 2021 ANSYS, Inc. and its subsidiaries.  All Rights Reserved.
"""
import _thread
import json
import logging
import os
from os import path
import platform
import re
import shlex
import subprocess
import time
import traceback

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution
from ansys.rep.evaluator.task_manager.context import SubmitContext


class CfxExecution(ApplicationExecution):
    isLinux = platform.platform().startswith("Linux")

    def __init__(self, context):
        self.active_run_name = None
        self.putative_run_name = None
        self.withSoftInterrupt = True
        ApplicationExecution.__init__(self, context)

    def publish_to_default_log(self, msg):
        log.info(msg)

    def publish_to_debug_log(self, msg):
        log.debug(msg)

    def execute(self):
        log.info("Start CFX execution script")

        try:
            log.info("Evaluator Platform: " + platform.platform())

            num_cores = self.context.resource_requirements["num_cores"]
            log.info(f"Requested cores: {num_cores}")

            # create defaults for inputs not provided
            inputs = {
                "cfx_additionalArgs": self.context.execution_context.get("cfx_additionalArgs", "")
            }
            inputs["cfx_solverFile"] = self.context.execution_context.get("cfx_solverFile", None)
            inputs["cfx_definitionFile"] = self.context.execution_context.get(
                "cfx_definitionFile", None
            )
            inputs["cfx_iniFile"] = self.context.execution_context.get("cfx_iniFile", None)
            inputs["cfx_cclFile"] = self.context.execution_context.get("cfx_cclFile", None)
            inputs["cfx_contFile"] = self.context.execution_context.get("cfx_contFile", None)
            inputs["cfx_mcontFile"] = self.context.execution_context.get("cfx_mcontFile", None)
            inputs["cfx_mdefFile"] = self.context.execution_context.get("cfx_mdefFile", None)
            inputs["cfx_parFile"] = self.context.execution_context.get("cfx_parFile", None)
            inputs["cfx_indirectPath"] = self.context.execution_context.get(
                "cfx_indirectPath", None
            )
            inputs["cfx_version"] = self.context.execution_context.get("cfx_version", None)
            inputs["cfx_useAAS"] = self.context.execution_context.get("cfx_useAAS", False)
            inputs["cfx_startMethod"] = self.context.execution_context.get("cfx_startMethod", None)
            inputs["cfx_runName"] = self.context.execution_context.get("cfx_runName", None)

            cclFile = next((f for f in self.context.input_files if f["name"] == "ccl"), None)
            if cclFile != None:
                inputs["cfx_cclFile"] = cclFile["path"]
                log.info("ccl file path: " + cclFile["path"])

            defFile = next((f for f in self.context.input_files if f["name"] == "def"), None)
            if defFile != None:
                inputs["cfx_definitionFile"] = defFile["path"]
                log.info("def file path: " + defFile["path"])

            self.publish_to_default_log(
                "Task inputs after applying default values to missing inputs:"
            )
            for name in inputs.keys():
                if inputs[name] == None:
                    continue
                self.publish_to_default_log("\t-" + name + ":<" + str(inputs[name]) + ">")

            # Check existence of files which must exist if specified
            inputs_existchk = [
                "cclFile",
                "contFile",
                "definitionFile",
                "iniFile",
                "mcontFile",
                "mdefFile",
                "parFile",
                "solverFile",
            ]

            self.publish_to_default_log("Checking if provided files exist in the storage...")
            for i in inputs_existchk:
                k = "cfx_" + i
                if not inputs[k] == None:
                    if not os.path.isfile(inputs[k]):
                        raise Exception("Required file does not exist!\n" + inputs[k])

            if not inputs["cfx_indirectPath"] == None:
                # Special check for indirect startup and set active name for later use
                rundir = inputs["cfx_indirectPath"] + ".dir"
                if not os.path.isdir(rundir):
                    raise Exception("Required directory does not exist!\n" + rundir)
                startup_ccl = rundir + "/startup.ccl"
                if not os.path.isfile(startup_ccl):
                    raise Exception(startup_ccl)
                self.active_run_name = inputs["cfx_indirectPath"]
            else:
                # Set putative run name from input file
                for i in ["definitionFile", "mdefFile", "contFile", "iniFile", "mcontFile"]:
                    k = "cfx_" + i
                    if not inputs[k] == None:
                        probname = re.sub("(_\d{3})?\.[^\.]+$", "", inputs[k])
                        self.set_putative_run_name(probname)
                        break

                if self.putative_run_name == None and inputs["cfx_runName"] != None:
                    self.set_putative_run_name(inputs["cfx_runName"])

                # Set putative run name from -eg or -name value (-name always wins)
                if (
                    not inputs["cfx_additionalArgs"] == ""
                    and not inputs["cfx_additionalArgs"] == None
                ):
                    for opt in ["-eg", "-example", "-name"]:
                        m = re.search(opt + "\s+([^\s-]+)", inputs["cfx_additionalArgs"])
                        if m:
                            self.set_putative_run_name(m.group(1))

            # Identify application
            app_name = "Ansys CFX"
            app = next((a for a in self.context.software if a["name"] == app_name), None)
            assert app, f"{app_name} is required for execution"

            log.info("Using " + app["name"] + " " + app["version"])
            log.info("Current directory: " + os.getcwd())

            files = [f for f in os.listdir(".") if os.path.isfile(f)]
            for f in files:
                log.info("   " + f)

            # Determine CFX root directory, solver command and hosts
            self.publish_to_default_log("CFX Root directory = " + app["install_path"])

            exe = app["executable"]  # should already be platform specific
            self.publish_to_default_log("CFX Solver command: " + exe)

            # Create command line
            # Add parallel options
            cmd = [os.path.basename(exe)]
            cmd.append("-fullname")
            cmd.append(self.active_run_name)
            cmd.append("-batch")
            cmd.append("-serial")

            # Add options requiring an argument
            options_arg = {
                "-ccl": "cclFile",
                "-continue-from-file": "contFile",
                "-def": "definitionFile",
                "-indirect-startup-path": "indirectPath",
                "-initial-file": "iniFile",
                "-mcont": "mcontFile",
                "-mdef": "mdefFile",
                "-parfile-read": "parFile",
                "-solver": "solverFile",
            }
            for opt, i in sorted(options_arg.items()):
                k = "cfx_" + i
                if not inputs[k] == None:
                    cmd.append(opt)
                    cmd.append(inputs[k])

            # Add additional options
            if not inputs["cfx_additionalArgs"] == "" and not inputs["cfx_additionalArgs"] == None:
                cmd.extend(shlex.split(inputs["cfx_additionalArgs"]))

            # Start the solver
            self.publish_to_default_log("CFX solver command line = " + str(cmd))

            rc = None
            self.CFXOutputFile = None
            self.CFXMonFile = None
            cfx_env = os.environ.copy()

            with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=cfx_env, executable=exe
            ) as self.proc:
                if self.proc == None:
                    raise Exception("CFX Solver did not start")
                self.publish_to_default_log("CFX solver started\npid:" + format(self.proc.pid))
                t1 = _thread.start_new_thread(self.process_output, (self.proc,))
                t2 = _thread.start_new_thread(self.process_error, (self.proc,))

                while rc is None:
                    rc = self.proc.poll()
                    time.sleep(1)

            # Post solution actions
            for msg in ["Finished CFX solve"]:
                self.publish_to_default_log(msg)

            if rc != 0:
                self.publish_to_default_log(f"Error: Solver exited with errors ({rc}).")
                raise Exception("Solver exited with errors.")

            return

        except Exception as e:
            self.publish_to_debug_log(traceback.print_exc())
            self.publish_to_default_log(str(e))
            raise e

    # Set putative run name from problem name (to be called BEFORE the run is started)
    def set_putative_run_name(self, probname):
        if self.active_run_name != None:
            return
        imax = 0
        for dI in os.listdir(os.getcwd()):
            m = re.match("^" + probname + "_(\d+)(\.(ansys|dir|out|res|mres|trn|cfx))?$", dI)
            if m:
                i = int(m.group(1))
                if i > imax:
                    imax = i
        prob_ext = str(imax + 1)
        self.putative_run_name = probname + "_" + prob_ext.zfill(3)
        self.active_run_name = self.putative_run_name
        self.publish_to_default_log("Set putative run name = " + self.putative_run_name)

    # Find active run name from putative run name (to be called AFTER the run is started)
    def find_active_run_name(self):
        # Putative run name set: Wait for output or run directory or output file to exist
        if self.active_run_name == None:
            if self.putative_run_name == None:
                raise Exception("Unable to find active run name. Putative run name not set.")
            outdir = path.join(os.getcwd(), self.putative_run_name)
            rundir = outdir + ".dir"
            outfile = outdir + ".out"
            while self.active_run_name == None:
                if path.isdir(outdir) or path.isdir(rundir) or path.isfile(outfile):
                    self.active_run_name = self.putative_run_name
                else:
                    time.sleep(1)
        return self.active_run_name

    # Monitor the stdout of the main process. If present, create log and log data.
    def process_output(self, proc):
        for line in iter(proc.stdout.readline, b""):
            msg = line.decode("utf-8").rstrip()
            self.publish_to_default_log(msg)
        proc.stdout.close()

    # Monitor the stderr of the main process. If present, create log and log data.
    def process_error(self, proc):
        for line in iter(proc.stderr.readline, b""):
            msg = line.decode("utf-8").rstrip()
            self.publish_to_default_log(msg)
        proc.stderr.close()


# EXAMPLE: this function will only be called if this script is run at the command line.
if __name__ == "__main__":
    log = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Loading sample CFX context...")

        with open("cfx_context.json", "r") as f:
            context = json.load(f)
            print(context)

        submit_context = SubmitContext(**context)

        log.info("Executing...")
        ex = CfxExecution(submit_context).execute()
        log.info("Execution ended.")

    except Exception as e:
        log.error(str(e))
