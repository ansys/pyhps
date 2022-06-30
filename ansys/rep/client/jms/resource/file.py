# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import json
import logging
import os
from pathlib import Path

from ansys.rep.client.exceptions import REPError
from ..schema.file import FileSchema
from .base import (Object, create_objects, get_objects,
                   update_objects)

log = logging.getLogger(__name__)

class File(Object):
    """File resource.
    
    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): A project resource. Defaults to None.
        src (str, optional): Path to the local file. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the File schema below.

    Example:

        >>> # input file
        >>> f1 = File(name="mac", evaluation_path="demo_project.mac",
                        type="text/plain", src=os.path.join(os.getcwd(), "motorbike_frame.mac")
        >>> # output file
        >>> f2 = File(name="img", evaluation_path="file000.jpg", type="image/jpeg") )

    The File schema has the following fields:

    .. jsonschema:: schemas/File.json

    """

    class Meta:
        schema = FileSchema
        rest_name = "files"

    def __init__(self, project=None, src=None, **kwargs):
        self.project=project
        self.src = src
        self.content = None
        super(File, self).__init__(**kwargs)

    def download(self, target_path, stream=True, progress_handler=None):
        """ 
        Download file content and save it to disk. If stream=True,
        data is retrieved in chunks, avoiding storing the entire content
        in memory.
        """
        return download_file(self, target_path, progress_handler, stream)


FileSchema.Meta.object_class = File

def _download_files(files):
    """ 
    Temporary implementation of file download directly using fs REST gateway.
    To be replaced with direct ansft calls, when it is available as python pkg
    """

    for f in files:
        if getattr(f, "hash", None) is not None:
            r = f.project.client.session.get(f"{f.project.fs_bucket_url}/{f.storage_id}")
            f.content = r.content
            f.content_type = r.headers['Content-Type']

def get_files(project, as_objects=True, content=False, **query_params):

    files = get_objects(project, File, as_objects=as_objects, **query_params)
    for file in files:
        file.project = project
    if content:
        _download_files(files)
    return files


def _upload_files(project, files):
    """ 
    Temporary implementation of file upload directly using fs REST gateway.
    To be replaced with direct ansft calls, when it is available as python pkg
    """
    fs_headers= {'content-type': "application/octet-stream"}

    for f in files:
        if getattr(f, "src", None) is not None:
            with open(f.src, "rb") as file_content:
                r = project.client.session.post(f"{project.fs_bucket_url}/{f.storage_id}", data=file_content, headers=fs_headers)
                f.hash = r.json()["checksum"]
                f.size = os.path.getsize(f.src)

def create_files(project, files, as_objects=True):
    # (1) Create file resources in DPS
    created_files = create_objects(project, files, as_objects=as_objects)
    
    # (2) Check if there are src properties, files to upload
    num_uploads=0
    for f,cf in zip(files, created_files):
        if getattr(f, "src", None) is not None:
            cf.src=f.src
            num_uploads+=1

    if num_uploads>0:

        # (3) Upload file contents
        _upload_files(project, created_files)
        
        # (4) Update corresponding file resources in DPS with hashes of uploaded files
        created_files = update_objects(project, created_files, as_objects=as_objects)

    return created_files

def update_files(project, files, as_objects=True):
    # Upload files first if there are any src parameters
    _upload_files(project, files)
    # Update file resources in DPS
    return update_objects(project, files, as_objects=as_objects)

def download_file(file, target_path, progress_handler=None, stream=True):
    
    if getattr(file, "hash", None) is None:
        raise REPError(f"No hash found. Failed to download file {file.name}")

    Path(target_path).mkdir(parents=True, exist_ok=True)
    download_link = f"{file.project.fs_bucket_url}/{file.storage_id}"
    download_path = os.path.join(target_path, file.evaluation_path)
    
    with file.project.client.session.get(download_link, stream=stream) as r,\
        open(download_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=None):
            f.write(chunk)
            if progress_handler is not None:
                progress_handler(len(chunk))
    
    return download_path