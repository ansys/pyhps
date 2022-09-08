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
    format : str, optional
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

    def __init__(self, src=None, **kwargs):
        self.src = src
        self.content = None

        self.id = missing
        self.name = missing
        self.type = missing
        self.storage_id = missing
        self.size = missing
        self.hash = missing
        self.creation_time = missing
        self.modification_time = missing
        self.format = missing
        self.evaluation_path = missing
        self.monitor = missing
        self.collect = missing
        self.collect_interval = missing
        self.reference_id = missing

        super().__init__(**kwargs)

FileSchema.Meta.object_class = File
