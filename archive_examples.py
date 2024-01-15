# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import os
from zipfile import ZipFile


def archive_examples():
    """Create a zip archive for each listed example included in the examples folder."""

    examples = {
        "mapdl_motorbike_frame": [
            "project_setup.py",
            "project_query.py",
            "exec_mapdl.py",
            "motorbike_frame_results.txt",
            "motorbike_frame.mac",
        ],
        "mapdl_tyre_performance": [
            "project_setup.py",
            "tire_performance_simulation.mac",
            "2d_tire_geometry.iges",
        ],
        "mapdl_linked_analyses": [
            "project_setup.py",
            "prestress.dat",
            "modal.dat",
            "harmonic.dat",
        ],
        "lsdyna_cylinder_plate": [
            "lsdyna_job.py",
            "cylinder_plate.k",
            "postprocess.cfile",
        ],
        "python_two_bar_truss_problem": [
            "project_setup.py",
            "exec_python.py",
            "evaluate.py",
            "input_parameters.json",
        ],
        "fluent_2d_heat_exchanger": [
            "project_setup.py",
            "heat_exchanger.jou",
            "heat_exchanger.cas.h5",
        ],
        "fluent_nozzle": [
            "project_setup.py",
            "exec_fluent.py",
            "solve.jou",
            "nozzle.cas",
        ],
        "cfx_static_mixer": [
            "project_setup.py",
            "exec_cfx.py",
            "runInput.ccl",
            "StaticMixer_001.cfx",
            "StaticMixer_001.def",
        ],
    }

    os.makedirs("build", exist_ok=True)
    for name, files in examples.items():
        with ZipFile(os.path.join("build", f"{name}.zip"), "w") as zip_archive:
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), file)

    with ZipFile(os.path.join("build", f"pyhps_examples.zip"), "w") as zip_archive:
        for name, files in examples.items():
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), os.path.join(name, file))


if __name__ == "__main__":
    archive_examples()
