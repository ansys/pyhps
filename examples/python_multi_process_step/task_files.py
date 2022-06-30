# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): R.Walker
# ----------------------------------------------------------
'''
Update some task files
(1) Create a new input file with changed data
(2) change parameter `CALL_SUBSCRIPT` to true in `eval.py` that the script is run as subscript with new input file
(3) make sure that newly generated files are added as output of the process step
'''
import os
import logging
import json
from tempfile import NamedTemporaryFile

from ansys.rep.client.jms import File

log = logging.getLogger(__name__)

ADDITIONAL_TASK_FILE = ''

def update_input_file(task):

    log.info('Update input file for task {}'.format(task.task_definition_snapshot.name))

    data = {
      "color": "white",
      "period": 2,
      "duration": 8,
      "info": '# changed for task ID: {} Process Step {}'.format(task.id, task.task_definition_snapshot.name)
    }
    file = NamedTemporaryFile(delete=False, prefix='input_mod', suffix='.json', mode='w')
    json.dump(data, file)
    return file.name


def update_eval_script(task):
    
    path = 'eval.py'
    lines = open(path).readlines()

    log.info('Update input file {} for task {}'.format(path, task.task_definition_snapshot.name))

    lines = ['#'*20+'\n', 
             '# Changed Task File\n'.format(task.id, task.task_definition_snapshot.name),
             '#'*20 + '\n'] \
            + lines

    for i,line in enumerate(lines):
        if line.startswith('CALL_SUBSCRIPT = '):
            lines[i] = 'CALL_SUBSCRIPT = True\n'

    file = NamedTemporaryFile(
        delete=False,
        mode='w',
        **dict(zip(['prefix', 'suffix'], os.path.splitext(os.path.basename(path)))))
    file.writelines(lines)
    file.close()
    return file.name


def update_task_files(proj, num_jobs, write_images):

    log.debug("=== Update Task files ===")
    cwd = os.path.dirname(__file__)

    config = proj.get_job_definitions()[0]
    jobs = config.get_jobs(limit=num_jobs)

    for dp in jobs:
        log.debug(' Update job {}'.format(dp.name))
        dp.name = dp.name + ' Modified'
        tasks = dp.get_tasks()
        for i,task in enumerate(tasks, 1):
            files = []
            # input_file
            ##input_name = "ps_{}_input".format(i)
            ##files.append( File( name=input_name,
            ##                evaluation_path="ps_{}_input.json".format(i),
            ##                type="application/json",
            ##                src=os.path.join(cwd, "input.json".format(i)) ) )
            # new input_file will be used by subprocess
            new_input_file = update_input_file(task)
            new_input_name = "sub_td_{}_input".format(i)
            files.append( File( name=new_input_name,
                            evaluation_path="sub_td_{}_input.json".format(i),
                            type="application/json",
                            src=new_input_file) )
            # overwrite the eval script: same name --> will be overwritten 
            new_eval_script = update_eval_script(task)
            new_eval_name = "td_{}_pyscript".format(i)
            files.append( File( name=new_eval_name,
                            evaluation_path="eval.py",
                            type="text/plain",
                            src=new_eval_script ) )
            # output text
            #out_name = "ps_{}_results".format(i)
            #files.append( File( name=out_name,
            #                evaluation_path="ps_{}_results.txt".format(i),
            #                collect=True, monitor=True,
            #                type="text/plain" ) )
            # new output text
            new_out_name = "sub_td_{}_results".format(i)
            files.append( File( name=new_out_name,
                            evaluation_path="sub_td_{}_results.txt".format(i),
                            collect=True, monitor=True,
                            type="text/plain" ) )
            # new image
            if write_images:
                new_image_name = "sub_td_{}_results_jpg".format(i)
                files.append( File( name=new_image_name,
                                    evaluation_path="sub_td_{}_results.jpg".format(i),
                                    type="image/jpeg", collect=True ) )

            files = proj.create_files(files)
            file_ids = {f.name: f.id for f in files}
            
            output_file_ids = [file_ids[new_out_name]]
            if write_images:
                output_file_ids.append(file_ids[new_image_name])

            task.output_file_ids = output_file_ids
            task.input_file_ids = [file_ids[new_input_name], file_ids[new_eval_name]]

        proj.update_tasks(tasks)

    proj.update_jobs(jobs)
    log.info('Updated {} design points'.format(len(jobs)))
