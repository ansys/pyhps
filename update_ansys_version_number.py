# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

import os
import re
import sys


def replace_regex(filename, new_version, patterns, group=1):

    with open(filename, "r") as myfile:
        content = myfile.read()

    header = f"File: {os.path.relpath(filename)}\n   "

    for pattern in patterns:
        re_res = re.search(pattern, content)
        if re_res is not None:
            old_string = re_res.group(0)
            old_version = ".".join(re_res.groups())

            if new_version != old_version:
                new_string = old_string.replace(old_version, new_version)

                print(f"{header}'{old_string}' --> '{new_string}' ")
                content = content.replace(old_string, new_string)

            else:
                print(f"{header}'{old_string}' already up-to-date ")

        else:
            print(f"{header}Couldn't find a match for {pattern}")

    with open(filename, "w") as myfile:
        myfile.write(content)


def main():

    internal_version = sys.argv[1]
    external_version = sys.argv[2]
    internal_version_no_dot = internal_version.replace(".", "")

    cwd = os.getcwd()

    version_file_path = os.path.join(cwd, "ansys", "rep", "client", "__version__.py")
    replace_regex(version_file_path, internal_version, [r"(\d+.\d+).0"])

    replace_regex(version_file_path, internal_version_no_dot, [r'__version_no_dots__ = "(\d+)"'])

    replace_regex(version_file_path, external_version, [r'__ansys_apps_version__ = "(.*)"'])

    replace_regex(
        os.path.join(cwd, "doc", "source", "conf.py"), internal_version_no_dot, [r"corp/v(\d+)"]
    )


if __name__ == "__main__":
    main()
