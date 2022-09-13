"""
Copyright (C) 2021 ANSYS, Inc. and its subsidiaries.  All Rights Reserved.
"""

# modules required to support CFX implemented functionality
from os import path
import json
import re
import os
import platform
#import psutil
import shlex
import subprocess
import time
import _thread
import traceback
import uuid
import logging

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

    def publish_to_default_log(self,msg):
        log.info(msg)

    def publish_to_debug_log(self,msg):
        log.debug(msg)

    def execute(self):
        log.info("Start CFX execution script")

        #with open("c:/ansysdev/pyrep/examples/exec_scripts/cfx_context.json", "w") as f:
        #    json.dump(vars(self.context), f)

        try:

            log.info("Queue Platform: " + platform.platform())

            coresCount = self.context.resource_requirements["num_cores"]
            log.info(f'coresCount: {coresCount}')

            #create defaults for inputs not provided
            inputs = { "cfx_additionalArgs" : self.context.execution_context.get("cfx_additionalArgs","") }
            inputs["cfx_solverFile"] = self.context.execution_context.get("cfx_solverFile", None)
            inputs["cfx_definitionFile"] = self.context.execution_context.get("cfx_definitionFile", None)
            inputs["cfx_iniFile"] = self.context.execution_context.get("cfx_iniFile", None)
            inputs["cfx_cclFile"] = self.context.execution_context.get("cfx_cclFile", None)
            inputs["cfx_contFile"] = self.context.execution_context.get("cfx_contFile", None)
            inputs["cfx_mcontFile"] = self.context.execution_context.get("cfx_mcontFile", None)
            inputs["cfx_mdefFile"] = self.context.execution_context.get("cfx_mdefFile", None)
            inputs["cfx_parFile"] = self.context.execution_context.get("cfx_parFile", None)
            inputs["cfx_indirectPath"] = self.context.execution_context.get("cfx_indirectPath", None)
            inputs["cfx_version"]  = self.context.execution_context.get("cfx_version", None)
            inputs["cfx_useAAS"] = self.context.execution_context.get("cfx_useAAS", False)
            inputs["cfx_startMethod"] = self.context.execution_context.get("cfx_startMethod", None)
            inputs["cfx_runName"] = self.context.execution_context.get("cfx_runName", None)

            self.publish_to_default_log("Task inputs after applying default values to missing inputs:")
            for name in inputs.keys():
                if inputs[name]==None:continue
                self.publish_to_default_log("\t-"+name+":<"+str(inputs[name])+">")

            # Check existence of files which must exist if specified
            inputs_existchk = ["cclFile","contFile","definitionFile",
                               "iniFile","mcontFile","mdefFile","parFile",
                               "solverFile"]

            self.publish_to_default_log("Checking if provided files exist in the storage...")
            for i in inputs_existchk:
                k = "cfx_"+i
                if not inputs[k]==None:
                    if not os.path.isfile(inputs[k]):
                        raise Exception("Required file does not exist!\n"+ inputs[k])

            if not inputs["cfx_indirectPath"]==None:
                # Special check for indirect startup and set active name for later use
                rundir = inputs["cfx_indirectPath"]+'.dir'
                if not os.path.isdir(rundir):
                    raise Exception("Required directory does not exist!\n"+rundir)
                startup_ccl = rundir+'/startup.ccl'
                if not os.path.isfile(startup_ccl):
                    raise Exception(startup_ccl)
                self.active_run_name = inputs["cfx_indirectPath"]
            else:
                # Set putative run name from input file
                for i in ['definitionFile','mdefFile','contFile','iniFile','mcontFile']:
                    k = "cfx_"+i
                    if not inputs[k]==None:
                        probname = re.sub('(_\d{3})?\.[^\.]+$','',inputs[k])
                        self.set_putative_run_name(probname)
                        break
                
                if self.putative_run_name == None and inputs["cfx_runName"] != None:
                    self.set_putative_run_name(inputs["cfx_runName"])

                # Set putative run name from -eg or -name value (-name always wins)
                if not inputs["cfx_additionalArgs"]=="" and not inputs["cfx_additionalArgs"]==None:
                    for opt in ['-eg','-example','-name']:
                        m = re.search(opt+'\s+([^\s-]+)',inputs["cfx_additionalArgs"])
                        if (m):
                            self.set_putative_run_name(m.group(1))

            # Identify application
            app_name = "ANSYS CFX"
            app = next((a for a in self.context.software if a["name"] == app_name), None)
            assert app, f"{app_name} is required for execution"

            log.info("Using "+app["name"]+" "+app["version"])
            log.info("Current directory: " + os.getcwd())

            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                log.info("   " + f)

            # Determine CFX root directory, solver command and hosts
            #self.rootDir = desired_cfx.rootFolder
            self.publish_to_default_log("CFX Root directory = " + app["install_path"])

            #exe = self.cfx_command("cfx5solve")
            exe = app["executable"]  # should already be platform specific
            self.publish_to_default_log("CFX Solver command: " + exe)

            machines = [] # TODO: self.environmentInfo.machines
            #self.publish_to_default_log(str(len(machines))+" available machine(s):")
            #for machine in machines:
            #    self.publish_to_default_log("\t-"+str(machine.hostname)+" ("+str(machine.coresCount)+" cores)")

            # Create command line
            # Add parallel options
            cmd = [exe]
            cmd.extend(["-fullname", self.active_run_name])
            cmd.append("-batch")
            if coresCount>1:
                hostlist = []
                for machine in machines:
                    hostlist.append(str(machine.hostname)+"*"+str(machine.coresCount))

                cmd.extend(["-par-dist", ','.join(hostlist)])
            else:
                cmd.append("-serial")

            # Add options requiring an argument
            options_arg = {"-ccl":"cclFile",
                           "-continue-from-file":"contFile",
                           "-def":"definitionFile",
                           "-indirect-startup-path":"indirectPath",
                           "-initial-file":"iniFile",
                           "-mcont":"mcontFile",
                           "-mdef":"mdefFile",
                           "-parfile-read":"parFile",
                           "-solver":"solverFile"}
            for opt, i in sorted(options_arg.items()):
                k = "cfx_"+i
                if not inputs[k]==None:
                    cmd.extend([opt,inputs[k]])

            # Add aaS options
            aasKeyFile = str(uuid.uuid4())+".txt"
            instantaasKeyFile = "instant_"+aasKeyFile
            aas_enabled = False
            if inputs["cfx_useAAS"]:
                aas_enabled = True
                cmd.extend(["-aas", "-aas-keyfile", aasKeyFile])

            # Add additional options
            if not inputs["cfx_additionalArgs"]=="":
                cmd.extend(shlex.split(inputs["cfx_additionalArgs"]))

            # Start the solver
            self.publish_to_default_log("CFX solver command line = "+str(cmd))

            aas_task_name="aas"
            self.aas_workflow_path=None
            self.aas_key=None
            self.aas_key_broadcasted=False

            rc = None
            self.CFXOutputFile = None
            self.CFXMonFile = None
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as self.proc:
                self.publish_to_default_log("CFX solver started\npid:"+format(self.proc.pid))
                t1=_thread.start_new_thread(self.process_output, (self.proc,))
                t2=_thread.start_new_thread(self.process_error, (self.proc,))
                t3=_thread.start_new_thread(self.monitor_outfile, (self.proc,))
                t4=_thread.start_new_thread(self.monitor_monfile, (self.proc,))

                while rc is None:
                    rc = self.proc.poll()

                    if (aas_enabled):
                        # Get aaS workflow path. Wait up to 1 minute.
                        if self.aas_workflow_path==None:
                            for i in range(60):
                                aas_task_paths=self.get_task_paths_by_name(aas_task_name)
                                if len(aas_task_paths)==1:
                                    self.aas_workflow_path=aas_task_paths[0]
                                    self.publish_to_default_log("aas_workflow_path: "+format(self.aas_workflow_path))
                                    break
                                time.sleep(1)

                        # aaS key not yet set: Read from key file if present. Allow 2 seconds for the file to be written.
                        if self.aas_key==None:
                            if os.path.isfile(instantaasKeyFile):
                                time.sleep(2)
                                self.publish_to_default_log("New AAS key generated in <"+instantaasKeyFile+">")
                                with open(instantaasKeyFile,'r') as f:
                                    self.aas_key=f.read()

                        # aas key is set: Broadcast key to jobs API
                        if not self.aas_key==None:
                            if not self.aas_workflow_path==None:
                                if self.aas_key_broadcasted==False:
                                    command="NewAASKey"
                                    inputs={}
                                    inputs["name"]="Main CFX"
                                    inputs["description"]="This is the CFX session"
                                    inputs["Solver"]="CFX"
                                    inputs["IOR"]=self.aas_key
                                    if self.job_access==True:
                                        command_model = ansys.hpcservices.job_management_jobs_v1.CommandModel(workflow_path=self.aas_workflow_path, command=command, inputs=inputs)
                                        self.publish_to_default_log("command_model:"+format(command_model))
                                        api_response = self.jobs_api.run_job_command_async(self.context.jobReference, command_model=command_model)
                                        self.publish_to_default_log("api_response:"+format(api_response))
                                        self.aas_key_broadcasted=True
                    time.sleep(1)

            # Post solution actions
            for msg in ["Finished CFX solve"]:
                self.publish_to_default_log(msg)

            if rc!=0:
                self.publish_to_default_log(f'Error: Solver exited with errors ({rc}).')
                raise Exception("Solver exited with errors.")

            return

        except Exception as e:
            self.publish_to_debug_log(traceback.print_exc())
            self.publish_to_default_log(str(e))
            raise e

    # HPC required method, user defined implementation
    # this method is called whenever an Out-of Cloud user makes a request to this Python task
    # if CFXSolverLauncherActionDefinition.withSoftInterrupt is true, implementation forSoftInterrupt command is required
    def oncommand(self, command):
        self.publish_to_default_log("Received command:\n\n"+format(command)+"\n\n")
        if command.commandName=='SoftInterrupt':
            self.execute_soft_interrupt()
        if command.commandName=='DynControl':
            self.execute_dyn_control(command.inputs.__dict__)
        return

    # Interrupt (gracefully stop) a solver run
    def execute_soft_interrupt(self):
        if not self.rootDir:
            self.publish_to_default_log("Error: Cannot stop run unless started.")
            return

        active_run_name = self.find_active_run_name()
        if active_run_name == None:
            self.publish_to_default_log("Cannot stop run. No active run found.")
            return

        rundir = path.join(os.getcwd(),active_run_name+'.dir')
        if not path.isdir(rundir):
            self.publish_to_default_log("Cannot stop run. Run directory not found: "+str(rundir))
            return

        exe = self.cfx_command("cfx5stop")
        cmd = [exe]
        cmd.extend(["-directory",rundir])
        self.publish_to_default_log("command line = "+str(cmd))
        result = subprocess.run(cmd)
        rc = result.returncode

        if rc==0:
            self.publish_to_default_log("normal completion of cfx5stop")
        else:
            self.publish_to_default_log(f'Error: cfx5stop exited with errors ({rc}).')
            raise Exception("cfx5stop exited with errors.")

        return

    # Dynamically control a solver run
    def execute_dyn_control(self,inputs):
        if not self.rootDir:
            self.publish_to_default_log("Error: Dynamic run control not possible. Run is not started.")
            return

        if not inputs:
            self.publish_to_default_log("Error: Dynamic run control not possible without inputs.")
            return

        active_run_name = self.find_active_run_name()
        if active_run_name == None:
            self.publish_to_default_log("Dynamic run control not possible. No active run found.")
            return

        rundir = path.join(os.getcwd(),active_run_name+'.dir')
        if not path.isdir(rundir):
            self.publish_to_default_log("Dynamic run control not possible. Run directory not found: "+str(rundir))
            return

        exe = self.cfx_command("cfx5control")
        cmd = [exe]
        cmd.append(rundir)

        # Add options requiring an argument
        options_arg = {"-inject-commands":"injectCommands",
                       "-merge-commands":"mergeCommands"}
        for opt, i in sorted(options_arg.items()):
            k = "cfx_"+i
            if k in inputs:
                cmd.extend([opt,inputs[k]])

        # Add options not requiring an argument
        options_noarg = {"-abort":"abort",
                         "-backup":"backup",
                         "-complete-child-runs":"completeChildRuns",
                         "-no-backup":"noBackup",
                         "-stop":"stop"}
        for opt, i in sorted(options_noarg.items()):
            k = "cfx_"+i
            if k in inputs:
                cmd.append(opt)

        self.publish_to_default_log("command line = "+str(cmd))
        result = subprocess.run(cmd)
        rc = result.returncode

        if rc==0:
            self.publish_to_default_log("normal completion of cfx5control")
        else:
            self.publish_to_default_log(f'Error: cfx5control exited with errors ({rc}).')
            raise Exception("cfx5control exited with errors.")

        return

    # Set putative run name from problem name (to be called BEFORE the run is started)
    def set_putative_run_name(self,probname):
        if self.active_run_name != None:
            return
        imax = 0
        for dI in os.listdir(os.getcwd()):
            m = re.match('^'+probname+'_(\d+)(\.(ansys|dir|out|res|mres|trn|cfx))?$',dI)
            if (m):
                i = int(m.group(1))
                if i > imax:
                    imax = i
        prob_ext = str(imax + 1)
        self.putative_run_name = probname + '_' + prob_ext.zfill(3)
        self.active_run_name = self.putative_run_name
        self.publish_to_default_log('Set putative run name = '+self.putative_run_name)

    # Find active run name from putative run name (to be called AFTER the run is started)
    def find_active_run_name(self):
        # Putative run name set: Wait for output or run directory or output file to exist
        if self.active_run_name == None:
            if  self.putative_run_name == None:
                raise Exception("Unable to find active run name. Putative run name not set.")
            outdir = path.join(os.getcwd(),self.putative_run_name)
            rundir = outdir + '.dir'
            outfile = outdir + '.out'
            while (self.active_run_name == None):
                if path.isdir(outdir) or path.isdir(rundir) or path.isfile(outfile):
                    self.active_run_name = self.putative_run_name
                else:
                    time.sleep(1)
        return self.active_run_name

    # Monitor the stdout of the main process. If present, create log and log data.
    def process_output(self, proc):
        for line in iter(proc.stdout.readline, b''):
            msg=line.decode("utf-8").rstrip()
            self.publish_to_default_log(msg)
        proc.stdout.close()

    # Monitor the stderr of the main process. If present, create log and log data.
    def process_error(self, proc):
        for line in iter(proc.stderr.readline, b''):
            msg=line.decode("utf-8").rstrip()
            self.publish_to_default_log(msg)
        proc.stderr.close()

    # Monitor the solver output file
    def monitor_outfile (self, proc):
        active_run_name = self.find_active_run_name()
        try:
            while (self.CFXOutputFile == None):
                time.sleep(1)
                if not active_run_name == None:
                    f = path.join(os.getcwd(),active_run_name+'.out')
                    if os.path.isfile(f):
                        self.CFXOutputFile = f
            self.publish_to_default_log("CFX solver output file detected: <"+format(self.CFXOutputFile)+">")

            current_line=0
            while True:
                time.sleep(1)
                with open(self.CFXOutputFile) as f:
                    for _ in range(current_line):
                        next(f)
                    for line in f:
                        self.publish_to_default_log(line.rstrip())
                        current_line=current_line+1
        except Exception as e:
            errormessage=traceback.format_exc()
            self.publish_to_default_log(errormessage)
            self.publish_to_default_log("<"+format(e)+">")

    # Monitor the solver monitor file
    def monitor_monfile (self, proc):
        active_run_name = self.find_active_run_name()
        try:
            while (self.CFXMonFile == None):
                time.sleep(1)
                if not active_run_name == None:
                    f = path.join(os.getcwd(),active_run_name+'.dir','mon')
                    if os.path.isfile(f):
                        self.CFXMonFile = f
            self.publish_to_default_log("CFX solver monitor file detected: <"+format(self.CFXMonFile)+">")

            # TODO: do something with mon file?
        except Exception as e:
            errormessage=traceback.format_exc()
            self.publish_to_default_log(errormessage)
            self.publish_to_default_log("<"+format(e)+">")

    # Return the full path of a CFX command, appropriate for the OS used
    def cfx_command(self,command):
        if self.isLinux:
            return self.rootDir+"/bin/"+command
        else:
            return self.rootDir+"\\bin\\"+command+".exe"

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
        