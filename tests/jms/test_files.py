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

import io
import logging
import os
import tempfile

from marshmallow.utils import missing

from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import File, Project

log = logging.getLogger(__name__)


def test_files(client):

    jms_api = JmsApi(client)
    proj = jms_api.create_project(
        Project(name=f"rep_client_test_jms_FilesTest", active=False), replace=True
    )
    project_api = ProjectApi(client, proj.id)

    cwd = os.path.dirname(__file__)
    example_dir = os.path.join(cwd, "..", "..", "examples", "mapdl_motorbike_frame")
    log.debug(f"example_dir: {example_dir}")

    # Create some files
    files = []
    mac_path = os.path.join(example_dir, "motorbike_frame.mac")
    files.append(
        File(name="mac", evaluation_path="motorbike_frame.mac", type="text/plain", src=mac_path)
    )
    res_path = os.path.join(example_dir, "motorbike_frame_results.txt")
    files.append(
        File(
            name="results",
            evaluation_path="motorbike_frame_results.txt",
            type="text/plain",
            src=res_path,
        )
    )
    files.append(File(name="img", evaluation_path="file000.jpg", type="image/jpeg", hash=None))
    files.append(File(name="out", evaluation_path="file.out", type="text/plain", hash=None))

    with open(mac_path, "rb") as f:
        file_object_string = f.read()
    files.append(
        File(
            name="file-object",
            evaluation_path="my-file.txt",
            type="text/plain",
            src=io.BytesIO(file_object_string),
        )
    )

    files_created = project_api.create_files(files)
    for file in files_created:
        assert file.created_by is not missing
        assert file.creation_time is not missing
        assert file.modified_by is not missing
        assert file.modification_time is not missing
        assert file.created_by == file.modified_by

    # Get files
    files_queried = project_api.get_files(content=True)

    # Compare file objects, comparing all attrs that are not missing on created file object
    attrs = [attr for attr in files[0].declared_fields() if getattr(files[0], attr) != missing]
    for f1, f2 in zip(files, files_queried):
        for attr in attrs:
            assert getattr(f1, attr) == getattr(f2, attr)

    # Compare file contents
    with open(mac_path, "rb") as f:
        assert f.read() == files_queried[0].content
    with open(res_path, "rb") as f:
        assert f.read() == files_queried[1].content
    assert file_object_string == files_queried[4].content

    # verify that file size was correctly set
    assert os.path.getsize(mac_path) == files_queried[0].size
    assert os.path.getsize(res_path) == files_queried[1].size
    assert os.path.getsize(mac_path) == files_queried[4].size

    with tempfile.TemporaryDirectory() as tpath:

        # test chunked file download
        fpath = project_api.download_file(files_queried[0], tpath)
        with open(mac_path, "rb") as f, open(fpath, "rb") as sf:
            assert f.read() == sf.read()

        fpath = project_api.download_file(files_queried[1], tpath)
        with open(res_path, "rb") as f, open(fpath, "rb") as sf:
            assert f.read() == sf.read()

        # test download without streaming
        fpath = project_api.download_file(files_queried[0], tpath, stream=False)
        with open(mac_path, "rb") as f, open(fpath, "rb") as sf:
            assert f.read() == sf.read()

        # test progress handler
        handler = lambda current_size: print(
            f"{current_size*1.0/files_queried[0].size * 100.0}% completed"
        )
        fpath = project_api.download_file(files_queried[0], tpath, progress_handler=handler)
        with open(mac_path, "rb") as f, open(fpath, "rb") as sf:
            assert f.read() == sf.read()

    # Delete project again
    jms_api.delete_project(proj)


def test_download_file_in_subdir(client):

    jms_api = JmsApi(client)
    proj = jms_api.create_project(Project(name=f"rep_test_download_file_in_subdir", active=False))
    project_api = ProjectApi(client, proj.id)

    files = [
        File(
            name="file",
            evaluation_path="subdir/file.txt",
            type="text/plain",
            src=io.BytesIO(b"This is my file"),
        )
    ]

    file = project_api.create_files(files)[0]

    with tempfile.TemporaryDirectory() as tpath:
        fpath = project_api.download_file(file, tpath)
        with open(fpath, "r") as sf:
            assert "This is my file" == sf.read()

    # Delete project again
    jms_api.delete_project(proj)
