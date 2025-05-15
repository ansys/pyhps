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
#     "ansys-meshing-prime[all]==0.7",
# ]
# ///

import json
import os
import sys

import ansys.meshing.prime as prime
from ansys.meshing.prime.graphics import PrimePlotter


def main(params, ansys_prime_root):
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


if __name__ == "__main__":
    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path) as input_file:
        params = json.load(input_file)
    ansys_prime_root = os.environ.get("ANSYS_PRIME_ROOT", None)
    main(params, ansys_prime_root)
