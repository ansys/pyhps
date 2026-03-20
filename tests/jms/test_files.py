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
        Project(name="rep_client_test_jms_FilesTest", active=False), replace=True
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
    for f1, f2 in zip(files, files_queried, strict=False):
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
        def handler(current_size):
            print(f"{current_size * 1.0 / files_queried[0].size * 100.0}% completed")

        fpath = project_api.download_file(files_queried[0], tpath, progress_handler=handler)
        with open(mac_path, "rb") as f, open(fpath, "rb") as sf:
            assert f.read() == sf.read()

    # Delete project again
    jms_api.delete_project(proj)


def test_download_file_in_subdir(client, inactive_temporary_project):
    project_api = ProjectApi(client, inactive_temporary_project.id)

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
        with open(fpath) as sf:
            assert "This is my file" == sf.read()


def test_download_file_with_correct_name(client, inactive_temporary_project):
    project_api = ProjectApi(client, inactive_temporary_project.id)

    files = [
        File(
            name="file",
            evaluation_path="test.txt",
            type="text/plain",
            src=io.BytesIO(b"This is my file"),
        )
    ]

    file = project_api.create_files(files)[0]

    with tempfile.TemporaryDirectory() as tpath:
        fpath = project_api.download_file(file, tpath, file_name="downloaded.txt")
        assert os.path.basename(fpath) == "downloaded.txt"
        with open(fpath) as sf:
            assert "This is my file" == sf.read()


def _write_file(file_path, size_in_mb):
    log.info(f"Generating file {file_path} with size {size_in_mb} MB")
    one_mb = 1024 * 1024  # 1MB
    with open(file_path, "wb") as f:
        for _ in range(size_in_mb):
            f.write(os.urandom(one_mb))


def test_file_download_progress(client, inactive_temporary_project):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test_file.bin")
        _write_file(file_path, 300)

        project_api = ProjectApi(client, inactive_temporary_project.id)
        files = [
            File(
                name="file",
                evaluation_path="test_file.bin",
                type="application/octet-stream",
                src=file_path,
            )
        ]

        file = project_api.create_files(files)[0]

        progress = []

        def _progress_handler(file_size):
            progress.append(file_size)
            log.info(f"Progress: {file_size / 1024.0 / 1024.0: .1f} MB downloaded")

        d_path = project_api.download_file(
            file, temp_dir, file_name="downloaded.bin", progress_handler=_progress_handler
        )
        assert os.path.exists(d_path)
        assert os.path.getsize(d_path) == os.path.getsize(file_path)

        assert len(progress) >= 2
        assert progress[0] == 0
        assert progress[-1] == file.size

        for i in range(1, len(progress)):
            assert progress[i] >= 0
            assert progress[i] <= file.size
            assert progress[i] >= progress[i - 1]


def test_files_access_mode(client):
    jms_api = JmsApi(client)
    proj = jms_api.create_project(
        Project(name="rep_client_test_jms_FilesTest_access_mode", active=False), replace=True
    )
    project_api = ProjectApi(client, proj.id)

    cwd = os.path.dirname(__file__)
    example_dir = os.path.join(cwd, "..", "..", "examples", "mapdl_motorbike_frame")
    log.debug(f"example_dir: {example_dir}")

    # Create some files
    files = []
    mac_path = os.path.join(example_dir, "motorbike_frame.mac")
    files.append(
        File(
            name="mac",
            evaluation_path="motorbike_frame.mac",
            type="text/plain",
            src=mac_path,
            access_mode="direct_access",
        )
    )

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
        if file.access_mode is not missing:
            if file.name == "mac":
                assert file.access_mode == "direct_access"
            if file.name == "file-object":
                assert file.access_mode == "transfer"

    # Delete project again
    jms_api.delete_project(proj)
