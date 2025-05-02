# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "ansys.mapdl.core",
# ]
# ///
import json
import os
import sys

from ansys.mapdl.core import launch_mapdl


def extract_frequencies(output_string, num_freqs):
    print("----EXTRACT_FREQUENCIES")
    print("OUTPUT_STRING:")
    print("----")
    print(f"{output_string}")
    print("----")
    mode_freqs = {}
    lines = output_string.split("\n")
    for line in lines:
        split = line.split()
        if len(split) < 2 or len(split[0]) == 0:
            continue
        print(split)
        if split[0][0].isdigit():
            index = int(split[0])
            mode_freqs[f"freq_mode_{index}"] = float(split[1])
            if index == num_freqs:
                break
    return mode_freqs


def main(params):
    print("Loading and setting up model")
    num_modes = params["num_modes"]
    young_modulus = params["young_modulus"]
    density = params["density"]
    poisson_ratio = params["poisson_ratio"]
    popup_plots = params["popup_plots"]
    port = params["port"]

    input_filename = "cantilever.cdb"
    if not os.path.isfile(input_filename):
        print(f"ERROR: Input file {input_filename} does not exist.")
        return 1

    # mapdl = launch_mapdl(loglevel="DEBUG")
    mapdl = launch_mapdl(
        start_instance=True, mode="grpc", loglevel="INFO", run_location=f"{os.getcwd()}", port=port
    )
    print(f"IP: {mapdl.ip}:{mapdl.port}")
    print(f"State: {mapdl.channel_state}")
    print(f"Status: {mapdl.check_status}")
    print(f"Connection: {mapdl.connection}")
    print(f"is_local: {mapdl.is_local}")
    print(mapdl)
    mapdl.mute = True
    mapdl.clear()

    mapdl.input("cantilever.cdb")
    mapdl.prep7()

    mapdl.mp("EX", 1, young_modulus)
    mapdl.mp("EY", 1, young_modulus)
    mapdl.mp("EZ", 1, young_modulus)
    mapdl.mp("PRXY", 1, poisson_ratio)
    mapdl.mp("PRYZ", 1, poisson_ratio)
    mapdl.mp("PRXZ", 1, poisson_ratio)
    mapdl.mp("DENS", 1, density)

    mapdl.allsel()
    mapdl.inistate("DEFINE", val5=100.0e6, val6=100.0e6, val7=0.0)

    mapdl.allsel()
    mapdl.emodif("ALL", "MAT", i1=1)
    mapdl.nsel("S", "LOC", "X", 0)
    print(f"Fixing {len(mapdl.get_array('NODE', item1='NLIST'))} nodes")
    mapdl.d("ALL", "ALL")

    mapdl.allsel()
    mapdl.etlist()
    element_type_id = int(mapdl.get("ETYPE", "ELEM", "1", "ATTR", "TYPE"))
    mapdl.keyopt(f"{element_type_id}", "2", "3", verbose=True)

    print("Solving model")
    mapdl.slashsolu()
    mapdl.antype("MODAL")
    mapdl.modopt("LANB", num_modes)
    mapdl.mxpand(num_modes)
    output = mapdl.solve(verbose=True)
    # output=mapdl.solve(verbose=False)
    # print(f"{mapdl.list_files()}")
    # mapdl.download("file0.err", ".")
    # mapdl.download("file1.err", ".")
    # mapdl.download("file1.out", ".")

    mapdl.post1()
    print("getting frequencies")
    output = mapdl.set("LIST", mute=False)
    mode_freqs = extract_frequencies(output, 20)
    print(f"Frequencies: {mode_freqs}")
    if popup_plots:
        mode_num = 1
        mapdl.set(1, mode_num)
        mapdl.plnsol("u", "sum")

    with open("output_parameters.json", "w") as out_file:
        json.dump(mode_freqs, out_file, indent=4)

    mapdl.exit()


if __name__ == "__main__":
    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path) as input_file:
        params = json.load(input_file)

    main(params)
