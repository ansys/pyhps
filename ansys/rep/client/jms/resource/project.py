
from marshmallow.utils import missing
from .base import Object
from ..schema.project import ProjectSchema

class Project(Object):
    """Project resource.

    Parameters:
        id (str): Unique ID to access the project, specified on creation of the project.
        name (str): Name of the project.
        active (bool): Defines whether the project is active for evaluation.
        priority (int): Priority to pick the project for evaluation.
        creation_time (datetime, optional): The date and time the project was created.
        modification_time (datetime, optional): The date and time the project was last modified.
        file_storages (list): List of file storages defined for the project.
        statistics (dict): Optional dictionary containing various project statistics.

    """

    class Meta:
        schema = ProjectSchema
        rest_name = "projects"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.active = missing
        self.priority = missing
        self.creation_time = missing
        self.modification_time = missing
        self.file_storages = missing
        self.statistics = missing

        super().__init__(**kwargs)

ProjectSchema.Meta.object_class = Project
