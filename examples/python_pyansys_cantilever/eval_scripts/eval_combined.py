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
#     "ansys-meshing-prime[all]==0.7",
#     "ansys.mapdl.core",
#     "matplotlib"
# ]
# ///

import json
import os
import sys

import ansys.meshing.prime as prime
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.designer import DesignFileFormat
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch
from ansys.mapdl.core import launch_mapdl
from ansys.meshing.prime.graphics import PrimePlotter
from matplotlib.ticker import FuncFormatter


def geometry(params):
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

    # Check input
    if (
        arm_cutoff_length > length
        or arm_width <= 0.0
        or (arm_slot and arm_slot_width > arm_width)
        or (arm_slot and arm_slot_width > width)
    ):
        print("SanityError: Cantilever dimensions are not sane.")

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

        # Draw matplotlib figure
        points = [
            [0.0, -arm_width / 2.0],
            [0.0, arm_width / 2.0],
            [arm_cutoff_length, arm_width / 2.0],
            [arm_cutoff_length, width / 2.0],
            [length, width / 2.0],
            [length, -width / 2.0],
            [arm_cutoff_length, -width / 2.0],
            [arm_cutoff_length, -arm_width / 2.0],
            [0.0, -arm_width / 2.0],
        ]
        xs, ys = zip(*points, strict=False)
        fig, ax = plt.subplots()
        ax.fill(xs, ys, color="green", alpha=1, edgecolor="black", linewidth=0.3)
        if arm_slot:
            slot_points = [
                [2.5e-6, arm_slot_width / 2.0],
                [arm_cutoff_length - 2.5e-6, arm_slot_width / 2.0],
                [arm_cutoff_length - 2.5e-6, -arm_slot_width / 2.0],
                [2.5e-6, -arm_slot_width / 2.0],
            ]
            slot_xs, slot_ys = zip(*slot_points, strict=False)
            ax.fill(slot_xs, slot_ys, color="white", alpha=1, edgecolor="black", linewidth=0.3)
        wall = patches.Rectangle(
            xy=(-length, -max(width, length)),
            width=length,
            height=2 * max(width, length),
            linewidth=0.3,
            edgecolor="black",
            facecolor="#B16100",
            hatch="///",
            alpha=1.0,
        )
        ax.add_patch(wall)
        ax.set_aspect("equal", adjustable="box")
        ax_length = 0.05 * length + 1.1 * max(length, width)
        ax.set_xlim(-0.05 * length, 1.1 * max(length, width))
        ax.set_ylim(-ax_length / 2.0, ax_length / 2.0)
        ax.set_title("Cantilever")
        formatter = FuncFormatter(lambda x, _: f"{x * 1e6:.1f}")
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        ax.set_xlabel("x [um]")
        ax.set_ylabel("y [um]")
        plt.savefig("canti_plot.png", dpi=500)

        # export has different extensions on different OSs (.x_t, .xmt_txt)
        # design.export_to_parasolid_text(os.getcwd())
        design.download(
            os.path.join(os.getcwd(), design.name + ".x_t"), DesignFileFormat.PARASOLID_TEXT
        )
    except Exception as e:
        print(f"Exception in geometry: {e}")
    finally:
        modeler.exit()


def mesh(params, ansys_prime_root):
    # Read relevant dimensions from parameters
    um2mm = 1e-3
    swept_layers = params["mesh_swept_layers"]
    thickness = params["canti_thickness"] * um2mm
    length = min(params["canti_length"], params["arm_cutoff_length"]) * um2mm
    width = (params["canti_width"] - 2 * params["arm_cutoff_width"]) * um2mm
    if params["arm_slot"]:
        width -= params["arm_slot_width"] * um2mm
        width /= 2.0
    min_size = min(length, width) * 0.05
    max_size = min(length, width) * 0.3
    popup_plots = params["popup_plots"]
    port = params["port_mesh"]

    cad_file = "cantilever.x_t"
    if not os.path.isfile(cad_file):
        print(f"ERROR: Input file {cad_file} does not exist.")
        return 1

    with prime.launch_prime(prime_root=ansys_prime_root, port=port) as prime_client:
        model = prime_client.model
        mesh_util = prime.lucid.Mesh(model=model)

        # Import geometry
        mesh_util.read(file_name=cad_file, cad_reader_route=prime.CadReaderRoute.PROGRAMCONTROLLED)

        # Set mesh size
        sizing_params = prime.GlobalSizingParams(model=model, min=min_size, max=max_size)
        model.set_global_sizing_params(params=sizing_params)

        part = model.parts[0]
        sweeper = prime.VolumeSweeper(model)

        stacker_params = prime.MeshStackerParams(
            model=model,
            direction=[0, 0, 1],
            max_offset_size=thickness / swept_layers,
            delete_base=True,
        )

        # Create the base face
        createbase_results = sweeper.create_base_face(
            part_id=part.id,
            topo_volume_ids=part.get_topo_volumes(),
            params=stacker_params,
        )

        base_faces = createbase_results.base_face_ids

        part.add_labels_on_topo_entities(["base_faces"], base_faces)

        if popup_plots:
            scope = prime.ScopeDefinition(model=model, label_expression="base_faces")
            display = PrimePlotter()
            display.plot(model, scope=scope)
            display.show()

        base_scope = prime.lucid.SurfaceScope(
            entity_expression="base_faces",
            part_expression=part.name,
            scope_evaluation_type=prime.ScopeEvaluationType.LABELS,
        )

        # Create mesh on base face
        mesh_util.surface_mesh(
            min_size=min_size, max_size=max_size, scope=base_scope, generate_quads=True
        )

        if popup_plots:
            display = PrimePlotter()
            display.plot(model, scope=scope, update=True)
            display.show()

        # Sweep base mesh through body
        sweeper.stack_base_face(
            part_id=part.id,
            base_face_ids=base_faces,
            topo_volume_ids=part.get_topo_volumes(),
            params=stacker_params,
        )

        if popup_plots:
            display = PrimePlotter()
            display.plot(model, update=True)
            display.show()

        mesh_file = "cantilever.cdb"
        mesh_util.write(os.path.join(os.getcwd(), mesh_file))


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


def mapdl(params):
    # Read Parameters
    num_modes = params["num_modes"]
    young_modulus = params["young_modulus"]
    density = params["density"]
    poisson_ratio = params["poisson_ratio"]
    popup_plots = params["popup_plots"]
    port = params["port_mapdl"]
    num_cores = params["num_cores"]
    memory_mb = params["memory_b"] / 1024.0**2

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
            nproc=num_cores,
            ram=memory_mb,
            running_on_hpc=False,
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
    print(f"python exe: {sys.executable}")
    # Fetch parameters
    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path) as input_file:
        params = json.load(input_file)

    ansys_prime_root = os.environ.get("ANSYS_PRIME_ROOT", None)

    # Run program step by step
    print("===Designing Geometry")
    geometry(params)
    print("===Drawing Mesh")
    mesh(params, ansys_prime_root)
    print("===Computing Eigenfrequencies")
    mapdl(params)
