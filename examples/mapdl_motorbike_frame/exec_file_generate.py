# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Basic execution script for generating random files from python."""

import datetime
import os
import re

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


def parse_size(size_str):
    match = re.match(r"(\d+)([KMG]?B)?", size_str.upper())
    if not match:
        raise ValueError("Invalid size format")

    size = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        None: 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
    }

    return size * multipliers[unit]


def generate_files(num_files, file_size, prefix="file"):
    for i in range(num_files):
        # Make the filename always the same length regardless of the number of files
        filename = f"{prefix}_{i + 1:04}.bin"
        with open(filename, "wb") as f:
            f.write(os.urandom(file_size))
        log.info(f"Created {filename} ({file_size} bytes)")


class PythonExecution(ApplicationExecution):
    def execute(self):
        log.info(f"{datetime.datetime.now()}: Creating large files")

        for size in ["1GB"]:  # , "5GB", "10GB", "20GB"]:
            m = parse_size(size)
            generate_files(1, m, prefix=f"{size}_file")

        n = 200
        m = parse_size("10KB")

        log.info(f"{datetime.datetime.now()}: Creating {n} files of size {m} bytes each")

        generate_files(n, m, prefix="super_extra_silly_long_name_of_a_small_file")

        log.info(f"{datetime.datetime.now()}: End Python execution script")
