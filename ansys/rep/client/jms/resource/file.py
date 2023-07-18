from marshmallow.utils import missing

from ..schema.file import FileSchema
from ansys.rep.client.common import Object


class File(Object):
    """File resource.

    Parameters
    ----------
    src : str, optional
        Client-only field to specify the path of an input file.
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str
        Name of the file resource.
    type : str, optional
        Type of the file. This can be any string but using a correct media type for the given resource is advisable.
    storage_id : str, optional
        File's identifier in the (orthogonal) file storage system
    size : int, optional
    hash : str, optional
    creation_time : datetime, optional
        The date and time the file resource was created.
    modification_time : datetime, optional
        The date and time the file resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    format : str, optional
    expiry_time : datetime, optional
        File expiration time.
    evaluation_path : str, optional
        Relative path under which the file instance for a job evaluation will be stored.
    monitor : bool, optional
        Whether to live monitor the file's content.
    collect : bool, optional
        Whether file should be collected per job
    collect_interval : int, optional
        Collect frequency for a file with collect=True. Min value limited by the evaluator's settings. 0/None - let the evaluator decide, other value - interval in seconds
    reference_id : str, optional
        Reference file from which this one was created

    """

    class Meta:
        schema = FileSchema
        rest_name = "files"

    def __init__(self, src=None,
        id=missing,
        name=missing,
        type=missing,
        storage_id=missing,
        size=missing,
        hash=missing,
        creation_time=missing,
        modification_time=missing,
        created_by=missing,
        modified_by=missing,
        expiry_time=missing,
        format=missing,
        evaluation_path=missing,
        monitor=missing,
        collect=missing,
        collect_interval=missing,
        reference_id=missing,
        **kwargs,
    ):
        self.src = src
        self.content = None

        self.id = id
        self.name = name
        self.type = type
        self.storage_id = storage_id
        self.size = size
        self.hash = hash
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.expiry_time = expiry_time
        self.format = format
        self.evaluation_path = evaluation_path
        self.monitor = monitor
        self.collect = collect
        self.collect_interval = collect_interval
        self.reference_id = reference_id

        self.obj_type = self.__class__.__name__

FileSchema.Meta.object_class = File
