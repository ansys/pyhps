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

import logging
import os
import sys
import time

log = logging.getLogger(__name__)


def main():
    start_time = time.time()

    file_name = "output.bin"
    size = 1

    log.info(f"Generating file {file_name} with size {size} GB")
    one_gb = 1024 * 1024 * 1024  # 1GB
    with open(file_name, "wb") as fout:
        for i in range(size):
            fout.write(os.urandom(one_gb))
    log.info(f"File {file_name} has been generated after {(time.time() - start_time):.2f} seconds")
    return 0


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    sys.exit(main())
