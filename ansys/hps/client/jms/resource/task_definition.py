# autogenerated code
from marshmallow.utils import missing
from ansys.hps.client.common import Object
from ..schema.task_definition import HpcResourcesSchema
from ..schema.task_definition import ResourceRequirementsSchema
from ..schema.task_definition import SoftwareSchema
from ..schema.task_definition import SuccessCriteriaSchema
from ..schema.task_definition import LicensingSchema
from ..schema.task_definition import TaskDefinitionSchema

class HpcResources(Object):
    """HpcResources resource.

    Parameters
    ----------
    num_cores_per_node : int, optional
        Number of cores per node.
    num_gpus_per_node : int, optional
        Number of GPUs per node.
    exclusive : bool, optional
        When set, a job can't share resources with other running jobs.
    queue : str, optional
        Name of job scheduler queue.

    """

    class Meta:
        schema = HpcResourcesSchema
        rest_name = "None"

    def __init__(self,
        num_cores_per_node=missing,
        num_gpus_per_node=missing,
        exclusive=missing,
        queue=missing,
        **kwargs
    ):
        self.num_cores_per_node = num_cores_per_node
        self.num_gpus_per_node = num_gpus_per_node
        self.exclusive = exclusive
        self.queue = queue

        self.obj_type = self.__class__.__name__

HpcResourcesSchema.Meta.object_class = HpcResources

class ResourceRequirements(Object):
    """ResourceRequirements resource.

    Parameters
    ----------
    platform : str, optional
        Basic platform information: 'windows' or 'linux'.
    memory : int, optional
        Amount of RAM in bytes.
    num_cores : float, optional
        Number of cores.
    disk_space : int, optional
        Amount of disk space in bytes.
    distributed : bool, optional
        Enable distributed parallel processing.
    custom : dict[str, int | float | str | bool], optional
        Custom resource requirements.
    hpc_resources : HpcResources, optional
        HPC requirements

    """

    class Meta:
        schema = ResourceRequirementsSchema
        rest_name = "None"

    def __init__(self,
        platform=missing,
        memory=missing,
        num_cores=missing,
        disk_space=missing,
        distributed=missing,
        custom=missing,
        hpc_resources=missing,
        **kwargs
    ):
        self.platform = platform
        self.memory = memory
        self.num_cores = num_cores
        self.disk_space = disk_space
        self.distributed = distributed
        self.custom = custom
        self.hpc_resources = hpc_resources

        self.obj_type = self.__class__.__name__

ResourceRequirementsSchema.Meta.object_class = ResourceRequirements

class Software(Object):
    """Software resource.

    Parameters
    ----------
    name : str
        Application's name.
    version : str, optional
        Application's version.

    """

    class Meta:
        schema = SoftwareSchema
        rest_name = "None"

    def __init__(self,
        name=missing,
        version=missing,
        **kwargs
    ):
        self.name = name
        self.version = version

        self.obj_type = self.__class__.__name__

SoftwareSchema.Meta.object_class = Software

class SuccessCriteria(Object):
    """SuccessCriteria resource.

    Parameters
    ----------
    return_code : int, optional
        The process exit code that must be returned by the executed command.
    expressions : list, optional
        A list of expressions to be evaluated.
    required_output_file_ids : list[str], optional
        List of IDs of required output files.
    require_all_output_files : bool, optional
        Flag to require all output files.
    required_output_parameter_ids : list[str], optional
        List of names of required output parameters.
    require_all_output_parameters : bool, optional
        Flag to require all output parameters.

    """

    class Meta:
        schema = SuccessCriteriaSchema
        rest_name = "None"

    def __init__(self,
        return_code=missing,
        expressions=missing,
        required_output_file_ids=missing,
        require_all_output_files=missing,
        required_output_parameter_ids=missing,
        require_all_output_parameters=missing,
        **kwargs
    ):
        self.return_code = return_code
        self.expressions = expressions
        self.required_output_file_ids = required_output_file_ids
        self.require_all_output_files = require_all_output_files
        self.required_output_parameter_ids = required_output_parameter_ids
        self.require_all_output_parameters = require_all_output_parameters

        self.obj_type = self.__class__.__name__

SuccessCriteriaSchema.Meta.object_class = SuccessCriteria

class Licensing(Object):
    """Licensing resource.

    Parameters
    ----------
    enable_shared_licensing : bool, optional
        Whether to enable shared licensing contexts for Ansys simulations

    """

    class Meta:
        schema = LicensingSchema
        rest_name = "None"

    def __init__(self,
        enable_shared_licensing=missing,
        **kwargs
    ):
        self.enable_shared_licensing = enable_shared_licensing

        self.obj_type = self.__class__.__name__

LicensingSchema.Meta.object_class = Licensing

class TaskDefinition(Object):
    """TaskDefinition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    creation_time : datetime, optional
        The date and time the resource was created.
    modification_time : datetime, optional
        The date and time the resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    name : str, optional
        Name.
    execution_command : str, optional
        Command to execute (command or execution script is required).
    use_execution_script : bool, optional
        Whether to run task with the execution command or the execution script.
    execution_script_id : str, optional
        Script to execute (command or execution script is required).
    execution_level : int
        Define execution level for this task.
    execution_context : dict[str, int | float | str | bool], optional
        Additional arguments to pass to the executing command
    environment : dict[str, str], optional
        Environment variables to set for the executed process
    max_execution_time : float, optional
        Maximum time in seconds for executing the task.
    num_trials : int, optional
        Maximum number of attempts to execute the task.
    store_output : bool, optional
        Specify whether to store the standard output of the task.
    input_file_ids : list[str]
        List of IDs of input files.
    output_file_ids : list[str]
        List of IDs of output files.
    success_criteria : SuccessCriteria, optional
    licensing : Licensing, optional
        A :class:`Licensing` object.
    software_requirements : list[Software], optional
        A list of :class:`Software` objects.
    resource_requirements : ResourceRequirements, optional
        A :class:`ResourceRequirements` object.

    """

    class Meta:
        schema = TaskDefinitionSchema
        rest_name = "task_definitions"

    def __init__(self,
        id=missing,
        creation_time=missing,
        modification_time=missing,
        created_by=missing,
        modified_by=missing,
        name=missing,
        execution_command=missing,
        use_execution_script=missing,
        execution_script_id=missing,
        execution_level=missing,
        execution_context=missing,
        environment=missing,
        max_execution_time=missing,
        num_trials=missing,
        store_output=missing,
        input_file_ids=missing,
        output_file_ids=missing,
        success_criteria=missing,
        licensing=missing,
        software_requirements=missing,
        resource_requirements=missing,
        **kwargs
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.name = name
        self.execution_command = execution_command
        self.use_execution_script = use_execution_script
        self.execution_script_id = execution_script_id
        self.execution_level = execution_level
        self.execution_context = execution_context
        self.environment = environment
        self.max_execution_time = max_execution_time
        self.num_trials = num_trials
        self.store_output = store_output
        self.input_file_ids = input_file_ids
        self.output_file_ids = output_file_ids
        self.success_criteria = success_criteria
        self.licensing = licensing
        self.software_requirements = software_requirements
        self.resource_requirements = resource_requirements

        self.obj_type = self.__class__.__name__

TaskDefinitionSchema.Meta.object_class = TaskDefinition
