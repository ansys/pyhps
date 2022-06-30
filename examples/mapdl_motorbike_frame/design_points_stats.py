import logging
import os
import random
from statistics import mean, median, stdev

from ansys.rep.client import REPError
from ansys.rep.client.jms import (Client, JobDefinition, Job, File,
                                  FitnessDefinition, Project, SuccessCriteria, Licensing)

log = logging.getLogger(__name__)

def print_value_stats(values, title):
    log.info(f"{title}")
    #log.info(f"Num      : {len(values)}")
    log.info(f"Mean     : {mean(values)} Stdev: {stdev(values)}")    
    log.info(f"(Min,Max): ({min(values)}, {max(values)})")

def main():

    log.info("=== DCS connection")
    #client = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")
    client = Client(rep_url="https://dcsv211dev.westeurope.cloudapp.azure.com/dcs", username="repadmin", password="An5y5_repadmin")
    log.info(f"DCS URL: {client.rep_url}")            
    
    log.info("=== Project")
    project=client.get_project(id="mapdl_motorbike_frame_perf_test")
    log.info(f"ID: {project.id}")
    log.info(f"Created on: {project.creation_time}")

    log.info("=== Query design points")
    jobs = project.get_jobs(eval_status="evaluated", fields=["id","values", "elapsed_time"])
    log.info(f"Statistics across {len(jobs)} design points")
    
    values= [dp.values["mapdl_elapsed_time_obtain_license"] for dp in jobs]    
    print_value_stats(values, "=== License checkoput (parameter: mapdl_elapsed_time_obtain_license)")    

    values= [dp.values["mapdl_elapsed_time"] for dp in jobs]    
    print_value_stats(values, "=== Elapsed time MAPDL (mapdl_elapsed_time)")    

    values= [dp.elapsed_time for dp in jobs]    
    print_value_stats(values, "=== Elapsed time DCS (elapsed_time)")    

    log.info("=== Query tasks")
    tasks=project.get_tasks(eval_status="evaluated", fields=["id", "prolog_time", "running_time", "finished_time"])
    log.info("Statistics across tasks")

    values= [(t.running_time-t.prolog_time).total_seconds() for t in tasks]    
    print_value_stats(values, "=== Prolog time (running_time - prolog_time")    

    values= [(t.finished_time-t.running_time).total_seconds() for t in tasks]    
    print_value_stats(values, "=== Running time (finished_time - running_time")    

if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(format='[%(asctime)s | %(levelname)s] %(message)s', level=logging.INFO)

    try:
        main()
    except REPError as e:
        log.error(str(e))


