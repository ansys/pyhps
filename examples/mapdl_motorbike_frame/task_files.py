import logging
import os

from ansys.rep.client import REPError
from ansys.rep.client.jms import (
    Client,
    File,
    FitnessDefinition,
    Job,
    JobDefinition,
    Licensing,
    Project,
    SuccessCriteria,
)

log = logging.getLogger(__name__)


def main():

    log.debug("=== Task files example script ===")
    cwd = os.path.dirname(__file__)

    client = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")
    proj = client.get_project("mapdl_motorbike_frame")

    # Create a modified MAPDL input file that reads an extra task file and writes out an extra result file
    mac_file = proj.get_files(id=1, content=True)[0]
    content = mac_file.content.decode("utf-8")
    lines = content.splitlines()
    for i, l in enumerate(lines):
        if "/PREP7" in l:
            lines.insert(i + 1, "/INPUT,task_input_file,mac")
            break
    for i, l in enumerate(lines):
        if "*CFCLOSE" in l:
            lines.insert(i + 2, "*CFCLOSE")
            lines.insert(i + 2, "('task_var = ',F20.8)")
            lines.insert(i + 2, "*VWRITE,task_var")
            lines.insert(i + 2, "*CFOPEN,task_output_file,txt")
            break
    mac_fpath = os.path.join(cwd, "motorbike_frame_mod.mac")
    with open(mac_fpath, "w") as f:
        f.write("\n".join(lines))

    # Add specific task files to tasks
    tasks = proj.get_tasks(limit=5)
    for t in tasks:
        log.debug(f"Modify task {t.id}")
        files = []

        # Overwrite modified mac file per task
        files.append(
            File(
                name="mac", evaluation_path="motorbike_frame.mac", type="text/plain", src=mac_fpath
            )
        )

        # Add an extra task input file
        mac2_fpath = os.path.join(cwd, f"task_input_file_{t.id}.mac")
        with open(mac2_fpath, "w") as f:
            f.write(f"task_var={t.id}")
        files.append(
            File(
                name="mac2",
                evaluation_path="task_input_file.mac",
                type="text/plain",
                src=mac2_fpath,
            )
        )

        # Add an extra task output file
        files.append(
            File(
                name="task_result",
                evaluation_path="task_output_file.txt",
                type="text/plain",
                collect=True,
            )
        )

        files = proj.create_files(files)
        file_ids = {f.name: f.id for f in files}
        log.debug(f"Add files: {file_ids}")

        t.input_file_ids = [file_ids["mac"], file_ids["mac2"]]
        t.output_file_ids.append(file_ids["task_result"])
        # Not yet supported: t.eval_status = 'pending'

    tasks = proj.update_tasks(tasks)

    # Set affected design points back to pending
    # (directly setting tasks back to pending is not yet supported)
    dp_ids = [t.job_id for t in tasks]
    dps = proj.get_jobs(id=dp_ids)
    for dp in dps:
        dp.eval_status = "pending"
    proj.update_jobs(dps)

    log.debug("=== Modified tasks and design points:")
    for t, dp in zip(tasks, dps):
        log.debug(
            f"Task: id={t.id} eval_status={t.eval_status} input_file_ids={t.input_file_ids} ouptut_file_ids={t.output_file_ids} Design point: id={dp.id} eval_status={dp.eval_status}"
        )
        # log.debug(f'{t}')
        # log.debug(f'{dp}')


if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(
        # format='[%(asctime)s | %(levelname)s] %(message)s',
        format="%(message)s",
        level=logging.DEBUG,
    )

    try:
        main()
    except REPError as e:
        log.error(str(e))
