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
Evaluation script for multi task definition testing
run *python eval.py --help* for command line arguments
The script has JSON-File as input and writes *text* and *json* as result files.
Input file has 3 parameters
```
{
      "color": "red",
      "period": 2,
      "duration":4
}
```
color: color of the image to be written
period [s]: period to wait before sending next log message
duration [s]: the duration of the eval script in seconds
The output of the script is the number of steps (log-calls) calculated with:
```
steps = duration // period
```

If the script is called with *--in-subscript* all the result file names are prepended with *sub_*

The support of json-file replacement is limited and therefore a string parameter value must be empty
```
"color": ,
```

"""
import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


#
# This flag will manually be set to True for design point task files
#
CALL_SUBSCRIPT = False


def main(input_file, task_definition, images, in_subscript):

    log = logging.getLogger()
    log.info("== Start Evaluation Task Definition ==")

    # Flag to mark files coming from subscript
    subs = "sub_" if in_subscript else ""

    # Read parameters
    log.info(f"Input File: {input_file}")
    log.info(f"Task Definition: {task_definition}")
    input_file_path = os.path.abspath(input_file)
    log.info(f"Open input file: {input_file_path}")
    with open(input_file_path, "r") as f:
        params = json.load(f)

    log.info(f"Params read: {params}")
    period = params["period"]
    duration = params["duration"]
    color = params["color"]

    # Calculate the Output: Number of steps
    steps = int(duration // period)

    output_parameters = {"steps": steps}

    # create json-results file
    out_filename = f"{subs}td{task_definition}_results.json"
    log.debug(f"Write JSON results file: {out_filename}")
    with open(out_filename, "w") as out_file:
        json.dump(output_parameters, out_file, indent=4)

    # create test-results file
    stamp = datetime.datetime.now()
    out_filename = f"{subs}td{task_definition}_results.txt"
    log.debug(f"Write text results file: {out_filename}")
    with open(out_filename, "w") as out:
        out.write(f"Script JobDefinition:\n")
        out.write(f"  Task Definition: {task_definition}\n")
        out.write(f"  Input File: {input_file}\n")
        out.write(f"  Images: {images}\n")
        out.write(f"Input:\n")
        out.write(f"  Duration: {duration}\n")
        out.write(f"  Period: {period}\n")
        out.write(f"  Color: {color}\n")
        out.write(f"Output:\n")
        out.write(f"  Steps: {steps}\n")
        out.flush()

    for i in range(1, steps + 1):
        with open(out_filename, "a+") as out:
            sec = (datetime.datetime.now() - stamp).seconds
            i_step = "{}/{}".format(i, steps)
            msg = "Task Definition: {}, Step: {:>8}, Time: {:>6}s".format(
                task_definition, i_step, sec
            )
            log.info(msg)
            out.write(msg + "\n")
            out.flush()
        time.sleep(period)

    with open(out_filename, "a+") as out:
        out.write("Finished.\n")
        out.flush()

    if images:

        # place import here if script should run without image generation
        from PIL import Image, ImageDraw, ImageFont

        # create an image !!!
        img = Image.new("RGB", (600, 400), color=color)
        d = ImageDraw.Draw(img)
        line_height = 36
        font = ImageFont.truetype("arial.ttf", 24)

        def text(i, txt):
            d.text((line_height, line_height * i), txt, fill=(0, 0, 1), font=font)

        # write the task definition
        text(1, f"{subs}task_definition: {task_definition}")
        i = 2
        for k, v in {**params, **output_parameters}.items():
            text(i, "{}: {}".format(k, v))
            i += 1
        text(i, "Have a lot of fun...")

        out_filename = f"{subs}td{task_definition}_results.jpg"
        log.debug(f"Write Image Results File: {out_filename}")
        img.save(out_filename)

    if CALL_SUBSCRIPT and not in_subscript:
        cmd = [
            "python",
            "eval.py",
            f"sub_td{task_definition}_input.json",
            f"{task_definition}",
            "--in-subscript",
        ]
        log.info("Run Subscript with: {cmd}")
        subprocess.run(cmd)

    log.info("Finished.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("input_file")
    parser.add_argument("task_definition", help="The task definition number the script is used.")
    parser.add_argument(
        "--images",
        action="store_true",
        default=False,
        help="""Enable if you want images to be generated.
                Needs PIL installed ( `pip install pillow` ) """,
    )
    parser.add_argument(
        "--in-subscript",
        action="store_true",
        default=False,
        help="Flag to inform script that it's a subprocess of itself.",
    )

    args = parser.parse_args()

    sys.exit(main(**vars(args)))

    # file_ids = {f.name: f.id for f in files}

    # log.debug("=== JobDefinition with simulation workflow and parameters")
    # job_def = JobDefinition(name="job_definition.1", active=True)

    # log.debug("=== Parameters")
    # params = [
    #     FloatParameterDefinition(name='start', lower_limit=1.0, upper_limit=start),
    # ]
    # params.extend([
    #     FloatParameterDefinition(name=f"product{i}") for i in range(num_task_definitions)
    # ])
    # params = proj.create_parameter_definitions(params)
    # job_def.parameter_definition_ids = [o.id for o in params]

    # param_mappings = [
    #     ParameterMapping(key_string='"start"', tokenizer=":",
    #     parameter_definition_id=params[0].id, file_id=file_ids['input'])
    # ]
    # param_mappings.extend([
    #     ParameterMapping(key_string='"product"', tokenizer=":",
    #     parameter_definition_id=params[i+1].id, file_id=file_ids[f'td{i}_result'])
    #     for i in range(num_task_definitions)
    # ])
    # param_mappings = proj.create_parameter_mappings(param_mappings)
    # job_def.parameter_mapping_ids = [o.id for o in param_mappings]

    # log.debug("=== Process Steps")
    # task_defs = []
    # for i in range(num_task_definitions):

    #     input_file_ids = [file_ids[f'td{i}_pyscript']]
    #     if i == 0:
    #         input_file_ids.append(file_ids['input'])
    #         cmd = f'%executable% %file:td{i}_pyscript% %file:input% {i}'
    #     else:
    #         input_file_ids.append(file_ids[f"td{i-1}_result"])
    #        cmd = f'%executable% %file:td{i}_pyscript% %file:p
