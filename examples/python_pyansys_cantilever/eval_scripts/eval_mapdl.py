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
# requires-python = "==3.12"
# dependencies = [
#     "ansys.mapdl.core",
#     "vtk==9.4.2",
# ]
# ///
import json
import os
import sys

from ansys.mapdl.core import launch_mapdl


def extract_frequencies(output_string, num_freqs):
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
    # Read Parameters
    num_modes = params["num_modes"]
    young_modulus = params["young_modulus"]
    density = params["density"]
    poisson_ratio = params["poisson_ratio"]
    popup_plots = params["popup_plots"]
    port = params["port_mapdl"]

    input_filename = "cantilever.cdb"
    if not os.path.isfile(input_filename):
        print(f"ERROR: Input file {input_filename} does not exist.")
        return 1

    try:
        # Launch MAPDL as a service
        mapdl = launch_mapdl(
            start_instance=True,
            mode="grpc",
            loglevel="DEBUG",
            run_location=f"{os.getcwd()}",
            port=port,
        )
        print(mapdl)
        mapdl.mute = True
        mapdl.clear()

        # Load input file
        mapdl.input("cantilever.cdb")
        mapdl.prep7()

        # Define material properties
        mapdl.mp("EX", 1, young_modulus)
        mapdl.mp("EY", 1, young_modulus)
        mapdl.mp("EZ", 1, young_modulus)
        mapdl.mp("PRXY", 1, poisson_ratio)
        mapdl.mp("PRYZ", 1, poisson_ratio)
        mapdl.mp("PRXZ", 1, poisson_ratio)
        mapdl.mp("DENS", 1, density)

        # Apply prestress
        mapdl.allsel()
        mapdl.inistate("DEFINE", val5=100.0e6, val6=100.0e6, val7=0.0)

        # Apply cantilever boundary conditions
        mapdl.allsel()
        mapdl.emodif("ALL", "MAT", i1=1)
        mapdl.nsel("S", "LOC", "X", 0)
        print(f"Fixing {len(mapdl.get_array('NODE', item1='NLIST'))} nodes")
        mapdl.d("ALL", "ALL")

        # Set keyopt properties
        mapdl.allsel()
        mapdl.etlist()
        element_type_id = int(mapdl.get("ETYPE", "ELEM", "1", "ATTR", "TYPE"))
        mapdl.keyopt(f"{element_type_id}", "2", "3", verbose=True)

        # Solve modal
        mapdl.slashsolu()
        mapdl.antype("MODAL")
        mapdl.modopt("LANB", num_modes)
        mapdl.mxpand(num_modes)
        output = mapdl.solve(verbose=False)

        # Extract calculated Eigenfrequencies
        mapdl.post1()
        output = mapdl.set("LIST", mute=False)
        mode_freqs = extract_frequencies(output, 20)
        if popup_plots:
            mode_num = 1
            mapdl.set(1, mode_num)
            mapdl.plnsol("u", "sum")

        mode_freqs["exe"] = sys.executable
        with open("output_parameters.json", "w") as out_file:
            json.dump(mode_freqs, out_file, indent=4)

    except Exception as e:
        print(f"Exception in mapdl: {e}")
    finally:
        mapdl.exit()


if __name__ == "__main__":
    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path) as input_file:
        params = json.load(input_file)

    main(params)
