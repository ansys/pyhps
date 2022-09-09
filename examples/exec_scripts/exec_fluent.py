"""
Copyright (C) 2021 ANSYS, Inc. and its subsidiaries.  All Rights Reserved.
"""

# modules required to support Fluent implemented functionality
import subprocess
import time
import _thread
import os
import traceback
import json
import psutil
import platform
import logging

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution
from ansys.rep.evaluator.task_manager.context import SubmitContext

class FluentExecution(ApplicationExecution):
    isLinux = platform.platform().startswith("Linux")
    
    def __init__(self, context):
        self.CleanupScript = None
        self.FluentTranscript = None
        self.error_detected = False
        self.fluent_children=[]
        #self.aas_workflow_path=None
        #self.aas_key=None
        #self.aas_key_broadcasted=False  

        ApplicationExecution.__init__(self, context)

    def execute(self):
        try:
            log.info("Start FLUENT execution script")

            #with open("c:/ansysdev/pyrep/examples/exec_scripts/fluent_context.json", "w") as f:
            #    json.dump(vars(self.context), f)

            pythoncode_version="0.1"
            log.info("python code version "+pythoncode_version)                
            
            log.info("Queue Platform: " + platform.platform())
            
            coresCount = self.context.resource_requirements["num_cores"]
            log.info(f'coresCount: {coresCount}')

            #self.environmentInfo.defaultMpi
            defaultMpi = "intel"

            #create defaults for inputs not provided
            inputs = { "fluent_dimension" : self.context.execution_context.get("fluent_dimension","2d") }
            inputs["fluent_precision"] = self.context.execution_context.get("fluent_precision", "dp")
            inputs["fluent_meshing"] = self.context.execution_context.get("fluent_meshing", False)
            inputs["fluent_numGPGPUsPerMachine"] = self.context.execution_context.get("fluent_numGPGPUsPerMachine", 0)
            inputs["fluent_defaultFluentVersion"]  = self.context.execution_context.get("fluent_defaultFluentVersion", None)
            inputs["fluent_MPIType"] = self.context.execution_context.get("fluent_MPIType", defaultMpi)
            inputs["fluent_otherEnvironment"]  = self.context.execution_context.get("fluent_otherEnvironment", "{}")
            inputs["fluent_UDFBat"] = self.context.execution_context.get("fluent_UDFBat", None)
            inputs["fluent_jouFile"] = self.context.execution_context.get("fluent_jouFile", None)
            inputs["fluent_useGUI"] = self.context.execution_context.get("fluent_useGUI", False)
            inputs["fluent_additionalArgs"]  = self.context.execution_context.get("fluent_additionalArgs", "")

            log.info("Task inputs ")
            for name in inputs.keys():
                if inputs[name]==None:continue
                log.info("\t-"+name+":<"+str(inputs[name])+">") 
            
            log.info("Checking if required inputs are provided...")
            
            valid_launcher_dimensions=['2d','3d']
            if not inputs["fluent_dimension"] in valid_launcher_dimensions:
                raise Exception("Required Input is invalid! fluent_dimension("+inputs["fluent_dimension"]+")\nValid values are "+format(valid_launcher_dimensions))
            
            valid_launcher_precisions=['sp','dp']
            if not inputs["fluent_precision"] in valid_launcher_precisions:
                raise Exception("Required Input is invalid! fluent_precision("+inputs["fluent_precision"]+")\nValid values are "+format(valid_launcher_precisions))

            # Identify application
            app_name = "ANSYS Fluent"
            app = next((a for a in self.context.software if a["name"] == app_name), None)
            assert app, f"{app_name} is required for execution"
            
            log.info("Using "+app["name"]+" "+app["version"])
            log.info("Current directory: " + os.getcwd())

            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                log.info("   " + f)

            if not os.path.isfile(inputs["fluent_jouFile"]):
                raise Exception("File "+inputs["fluent_jouFile"]+" does not exist!")            

            # Add " around exe if needed for Windows
            #exe= f"{desired_fluent.rootFolder}/bin/fluent" if isLinux else f'{desired_fluent.rootFolder}\\ntbin\\win64\\fluent.exe'
            exe = app["executable"]  # should already be platform specific
            log.info("Fluent executable: " + exe)
            #if " " in exe and not exe.startswith('"'):
            #    exe = '"%s"' % exe
            
            if inputs["fluent_UDFBat"]==None:
                if self.isLinux:
                    pass #no need in Linux, None is OK
                else:
                    inputs["fluent_UDFBat"]=os.path.join(os.path.dirname(exe), "udf.bat")
                    log.info("Setting fluent_UDFBat to "+inputs["fluent_UDFBat"])
            
            #machines = self.environmentInfo.machines           
            #log.info(str(len(machines))+" available machine(s):")        
            #for machine in machines:log.info("\t-"+str(machine.hostname)+" ("+str(machine.coresCount)+" cores)")
            #cnf = ""
            #if len(machines)>1:
            #    cnf = ""
            #    hosts = machines[0].hostname
            #    for m in machines[1:]:
            #        hosts = hosts+','+m.hostname
            #    cnf = f" -cnf={hosts}"

            otherEnvironment=json.loads(inputs['fluent_otherEnvironment'])
            noGuiOptions=None
            if not inputs["fluent_useGUI"]:
                if self.isLinux:
                    noGuiOptions = " -gu -driver null"
                else:
                    noGuiOptions = " -hidden -driver null"
            
            log.debug(f'exe: {exe}')
            args=inputs['fluent_dimension']
            args+= (inputs["fluent_precision"] if inputs["fluent_precision"]=="dp" else "")
            args+= (" -meshing" if inputs["fluent_meshing"] else "")
            args+= (" -t"+format(coresCount))
            if inputs["fluent_MPIType"]!=None and inputs["fluent_MPIType"]!= "":
                args+= (" -mpi="+format(inputs["fluent_MPIType"]))
            if inputs['fluent_numGPGPUsPerMachine'] > 0:
                args+= (" -gpgp="+format(inputs['fluent_numGPGPUsPerMachine']))
            args+= (" -i "+ inputs['fluent_jouFile'])
            #args+= cnf
            if not noGuiOptions==None:args+=noGuiOptions
            args+=(" "+inputs["fluent_additionalArgs"]+" ")
                
            cmd = ["fluent.exe"]
            cmd.extend(args.split(' '))
            
            rc = None
            firstchild=None

            fluent_env = os.environ.copy()
            
            for oenv in otherEnvironment:
                if "FLUENT_GUI"==oenv['Name']:continue
                #if "FLUENT_AAS"==oenv['Name']:continue
                fluent_env[oenv['Name']]=oenv['Value']
            log.info("Fluent environment:")
            for k in fluent_env:
                try:
                    log.info("\t- "+k+"\n\t\t "+fluent_env[k])
                except:                   
                    log.info("\t- error while printing "+k)
                    
            log.info(' '.join(cmd))
            
            #aas_task_name="aas"
            max_wait_time = 120
            tried_time = 0
            self.error_detected = False
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=fluent_env, executable=exe) as self.proc:
                log.info("Fluent started\npid:"+format(self.proc.pid))
                log.info("TODO: start new thread to monitor process children")
                t3=_thread.start_new_thread(self.monitor_children, (self.proc,))
                log.info("Fluent started a new thread to monitor its children")
                t4=_thread.start_new_thread(self.monitor_transcript, (self.proc,))
                log.info("Fluent started a new thread to monitor its transcript")

                t1=_thread.start_new_thread(self.process_output, (self.proc,))
                log.info("Fluent started a new thread for stdout log")
                t2=_thread.start_new_thread(self.process_error, (self.proc,))
                log.info("Fluent started a new thread for stderr log")
                while True:
                    if self.error_detected:
                        log.info("Error: Solver exited with error")
                        log.info("TODO: implement child process kill")
                        for child in self.fluent_children:
                            pToKill = psutil.Process(child)
                            pToKill.kill()
                        raise Exception("Solver exited with errors.")
                    if rc is None:
                        rc = self.proc.poll()
                    elif firstchild is None:
                        time.sleep(3)
                        tried_time = tried_time + 3
                        if len(self.fluent_children)==0:
                            if (tried_time < max_wait_time):
                                log.info("\t- no fluent children process found, continue") 
                                continue
                            else:
                                log.info("\t- can not start fluent in " + format(max_wait_time) + "seconds, quit the process") 
                                break
                        firstchild=self.fluent_children[0]
                        log.info("rc:"+format(rc)+" ,firstchild:"+format(firstchild))
                    elif not psutil.pid_exists(firstchild):
                        log.info("\t- fluent exits normally")
                        break
                    
            #log.info("waiting 180 seconds for log completions...")
            #time.sleep(180)
            #log.info("leaving Python task...")

            log.info("Finished Fluent solve")
            if rc!=0:
                log.info(f'Error: Solver exited with errors ({rc}).')
                raise Exception("Solver exited with errors.")
        
        except Exception as e:
            log.info("====== error in execute =========")
            log.debug(traceback.print_exc())
            log.info(str(e))
            log.info("====== error in execute =========")
            raise e
        
    # HPC required method, user defined implementation
    # this method is called whenever an Out-of Cloud user makes a request to this Python task
    # if FluentLauncherActionDefinition.withSoftInterrupt is true, implementation forSoftInterrupt command is required
    def oncommand(self, command):
        log.info("Received!\n\n"+format(command)+"\n\n")
        try:
            log.info(self, command.commandId,"Received")
            if command.commandName=='SoftInterrupt':
                log.info("\n\nSoftInterrupt Received!\n\n")
                if self.CleanupScript==None:
                    log.info("\n\nSoftInterrupt There is no kill script!\n\n")
                    log.info("\n\n Discovering the kill script ... \n\n")
                    for fn in os.listdir('.'):
                        if not fn.startswith('cleanup-fluent'):continue
                        log.info("\t- "+fn)
                        log.info("\n\n Candidate kill script found \n\n")
                        with open(fn) as candidate_kill_script:
                            content=candidate_kill_script.read()
                            for pidc in self.fluent_children:
                                footprint=" "+format(pidc)
                                log.info("\n\n Checking for footprint:<"+footprint+"> \n\n")
                                if footprint in content:
                                    log.info("\n\n kill script found:"+fn+" \n\n")
                                    self.CleanupScript=fn
                                    if self.isLinux:os.system(f"./sh {self.CleanupScript}")
                                    else:os.system(self.CleanupScript)
                                    log.info(self, command.commandId,"Completed","Killing using "+format(self.CleanupScript)) 
                                    break                                    
                else:
                    if self.isLinux:os.system(f"./sh {self.CleanupScript}")
                    else:os.system(self.CleanupScript)
                    log.info(self, command.commandId,"Completed","Killing using "+format(self.CleanupScript))                                    
            elif command.commandName=='TestFail': 
                #this should be used to in test to certify that errors are reported accuratley to the caller
                #this command is implemented intentionally to fail (true negative test)
                failure_on_intent=3/0
            elif command.commandName=='TestSucceedWithOutput':
                #this should be used to in test to certify that outputs are reported accurately to the caller
                #this command is implemented intentionally to succeed (true positive test)
                log.info(self, command.commandId,"Completed","command <"+command.commandName+"> has suceeded!")
            else:
                # this should be used to test that "No implemented" or "Not yet implemented" commands
                #    return an accurate response. 
                # Silent reponse (no reponse ) is a defective response
                log.info(self, command.commandId,"Completed","No callback for command <"+command.commandName+">")
        except Exception as e:
            errormessage=traceback.format_exc()
            log.info(errormessage)
            log.info(self, command.commandId,"Failed",errormessage)
    
    #user defined methods follow ...
    
    #monitor the children of the main process
    def monitor_children(self,proc):
        starting_process=psutil.Process(proc.pid)
        try:
            while True:
                for child in starting_process.children():
                    if not child.pid in self.fluent_children:self.fluent_children.append(child.pid)
                time.sleep(0.001)
        except Exception as e:
            if not 'psutil.NoSuchProcess' in format(e):
                errormessage=traceback.format_exc()
                log.info(errormessage)
                log.info("<"+format(e)+">")
    
    #monitor creation and content of transcript files and record content to corresponding logs
    def monitor_transcript(self,proc):
        try:
            while True:
                log.info("Looking for fluent automatically generated transcript file...")
                if not self.FluentTranscript==None:break
                time.sleep(1)
                for fn in os.listdir('.'):
                    if not fn.endswith(".trn"):continue
                    if fn.endswith(format(self.proc.pid)+".trn"):
                        self.FluentTranscript=fn
                    for childpid in self.fluent_children:
                        if fn.endswith(format(childpid)+".trn"):
                            log.info("Warning: a fluent child process generated transcript <" + format(fn) + "> is found!")
                            self.FluentTranscript=fn
                if not self.FluentTranscript==None:break
            log.info("Fluent transcript detected: <"+format(self.FluentTranscript)+">")
            
            current_line=0
            while True:
                time.sleep(1)
                with open(self.FluentTranscript) as f:
                    for _ in range(current_line):
                        next(f)
                    for line in f:
                        #log.info(format(self.FluentTranscript)+" -------> "+line.rstrip())
                        log.info(line.rstrip())
                        current_line=current_line+1
                        msg=line.rstrip()
                        if msg.startswith('ANSYS LICENSE STDOUT ERROR'):
                            self.error_detected=True
                            log.info("License error detected in fluent")
                        if msg.startswith('Unexpected license problem'):
                            self.error_detected=True
                            log.info("Unexpected license error detected in fluent")
                        if msg.startswith('Warning: An error or interrupt occurred while reading the journal file'):
                            self.error_detected=True
                            log.info("An error detected in fluent, killing fluent...")
                        if msg.startswith('Error:'):
                            self.error_detected=True
                            log.info("An error detected in fluent, killing fluent...")                              
                        if msg.startswith('Cleanup script file is'):
                            self.CleanupScript=msg.replace('Cleanup script file is ','') 
                            log.debug("Execute kills script is : "+ self.CleanupScript)
                        if msg.startswith('Opening input/output transcript to file "'):
                            self.FluentTranscript=msg.replace('Opening input/output transcript to file "','').replace('".','') 
                            log.debug("Fluent transcript is : "+ self.FluentTranscript)
        except Exception as e:
            errormessage=traceback.format_exc()
            log.info(errormessage)
            log.info("<"+format(e)+">")

    #monitor the stdout of the main process and log information to corresponding logs
    def process_output(self, proc):
        for line in iter(proc.stdout.readline, b''):
            msg=line.decode("utf-8").rstrip()
            log.info(msg)
            if msg.startswith('ANSYS LICENSE MANAGER ERROR'):self.error_detected=True
            if msg.startswith('Cleanup script file is'):
                self.CleanupScript=msg.replace('Cleanup script file is ','') 
                log.debug("Execute kills script is : "+ self.CleanupScript)
            if msg.startswith('Opening input/output transcript to file "'):
                self.FluentTranscript=msg.replace('Opening input/output transcript to file "','').replace('".','') 
                log.debug("Fluent transcript is : "+ self.FluentTranscript)
            #log.info(msg)
            if self.error_detected:log.debug(msg)
        proc.stdout.close()
    
    #monitor the stderr of the main process and log information to corresponding logs
    def process_error(self, proc):
        for line in iter(proc.stderr.readline, b''):
            msg=line.decode("utf-8").rstrip()
            log.error(msg)
            #self.publishMainTranscriptMessage(f'ERROR: {msg}')
            if msg.startswith('Fatal error in MPI_Init: Internal MPI error!'):
                if self.CleanupScript==None:
                    self.proc.kill()
                else:
                    p = subprocess.Popen(self.CleanupScript,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = p.communicate()
        proc.stderr.close()

if __name__ == "__main__":
    log = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Loading sample Fluent context...")

        with open("fluent_context.json", "r") as f:
            context = json.load(f)
            print(context)
   
        submit_context = SubmitContext(**context)

        log.info("Executing...")
        ex = FluentExecution(submit_context).execute()
        log.info("Execution ended.")

    except Exception as e:
        log.error(str(e))
        
