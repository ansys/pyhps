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
#     "numpy",
#     "matplotlib"
# ]
# ///

import json
import sys

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    # Generate plot
    ts = np.linspace(0.0, 10.0, 100)
    ys = np.sin(ts)

    fig, ax = plt.subplots()
    ax.plot(ts, ys)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Displacement [cm]")
    plt.savefig("plot.png", dpi=200)

    # Communicate location of venv for cleanup
    with open("output_parameters.json", "w") as out_file:
        json.dump({"exe": sys.executable}, out_file, indent=4)
