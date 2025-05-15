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
# requires-python = "==3.10"
# dependencies = [
#     "ansys-geometry-core[all]",
# ]
# ///

import json
import os
import sys

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.designer import DesignFileFormat
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch


def main(params):
    # Read parameters, convert to meters
    um2m = 1e-6
    width = params["canti_width"] * um2m
    length = params["canti_length"] * um2m
    thickness = params["canti_thickness"] * um2m
    arm_cutoff_width = params["arm_cutoff_width"] * um2m
    arm_cutoff_length = params["arm_cutoff_length"] * um2m
    arm_slot = params["arm_slot"]
    arm_slot_width = params["arm_slot_width"] * um2m
    popup_plots = params["popup_plots"]
    port = params["port_geometry"]
    arm_width = width - 2 * arm_cutoff_width

    # Draw Cantilever in 2D Sketch
    canti_sketch = Sketch()
    canti_sketch.segment(
        start=Point2D([0.0, -arm_width / 2.0]), end=Point2D([0.0, arm_width / 2.0])
    )
    canti_sketch.segment_to_point(end=Point2D([arm_cutoff_length, arm_width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([arm_cutoff_length, width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([length, width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([length, -width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([arm_cutoff_length, -width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([arm_cutoff_length, -arm_width / 2.0]))
    canti_sketch.segment_to_point(end=Point2D([0.0, -arm_width / 2.0]))

    # Add arm slot if it exists
    if arm_slot:
        canti_sketch.box(
            Point2D([arm_cutoff_length / 2.0 + 2.5e-6, 0.0]),
            arm_cutoff_length - 5e-6,
            arm_slot_width,
        )

    # Create a modeler, extrude sketches, union bodies
    try:
        modeler = launch_modeler(port=port)
        print(modeler)

        design = modeler.create_design("cantilever")
        design.extrude_sketch("cantilever", canti_sketch, thickness)

        # Plot if requested
        if popup_plots:
            design.plot()

        # export has different extensions on different OSs (.x_t, .xmt_txt)
        # design.export_to_parasolid_text(os.getcwd())
        design.download(
            os.path.join(os.getcwd(), design.name + ".x_t"), DesignFileFormat.PARASOLID_TEXT
        )
    except Exception as e:
        print(f"Exception in geometry: {e}")
    finally:
        modeler.exit()


if __name__ == "__main__":
    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path) as input_file:
        params = json.load(input_file)

    main(params)
