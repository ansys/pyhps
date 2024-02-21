# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

# generated by datamodel-codegen:
#   filename:  rms_openapi.json
#   timestamp: 2024-02-05T12:33:03+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Literal


class ApplicationInfo(BaseModel):
    name: str = Field(..., description="Application name.", title="Name")
    version: str = Field(..., description="Application version.", title="Version")
    install_path: str = Field(
        ..., description="Installation path of application.", title="Install Path"
    )
    executable: str = Field(
        ..., description="Executable path to run application.", title="Executable"
    )
    environment: Optional[Dict[str, Any]] = Field(
        None, description="Environment setup for the process.", title="Environment"
    )
    capabilities: Optional[List[str]] = Field(
        None, description="Capabilities of the application.", title="Capabilities"
    )
    customization_hook: Optional[Dict[str, Any]] = Field(
        None,
        description="Details of a custom hook used to modify the configuration before runs are performed.",
        title="Customization Hook",
    )


class EvaluatorTaskDirectoryCleanup(Enum):
    always = "always"
    on_success = "on_success"
    never = "never"


class ContextUpdate(BaseModel):
    custom: Optional[Dict[str, Optional[Union[int, bool, str, float]]]] = Field(
        {}, description="Custom runtime properties.", title="Custom"
    )


class CrsCountResponse(BaseModel):
    num_compute_resource_sets: Optional[int] = Field(0, title="Num Compute Resource Sets")


class TaskDirectoryCleanupEnum(Enum):
    always = "always"
    on_success = "on_success"
    never = "never"


class EvaluatorRegistration(BaseModel):
    id: Optional[str] = Field(None, description="Unique ID for this worker.", title="Id")
    name: Optional[str] = Field(
        None, description="User-defined name for this worker.", title="Name"
    )
    last_modified: Optional[datetime] = Field(
        None,
        description="Date and time when the registration was last modified.",
        title="Last Modified",
    )
    host_id: Optional[str] = Field(
        None, description="Static, hardware and configuration-based UUID.", title="Host Id"
    )
    host_name: Optional[str] = Field(
        None, description="Name of the host that the worker is running on.", title="Host Name"
    )
    username: Optional[str] = Field(
        None, description="Username that the worker authenticated with.", title="Username"
    )
    platform: Optional[str] = Field(
        None, description="OS that the evaluator is running on.", title="Platform"
    )
    build_info: Optional[Dict[str, Any]] = Field(
        {}, description="Detailed build information.", title="Build Info"
    )
    compute_resource_set_id: Optional[str] = Field(
        None,
        description="ID of the compute resource set that the evaluator belongs to.",
        title="Compute Resource Set Id",
    )
    change_requested: Optional[datetime] = Field(
        None,
        description="Date and time of the configuration's last modification request.",
        title="Change Requested",
    )


class EvaluatorsCountResponse(BaseModel):
    num_evaluators: Optional[int] = Field(0, title="Num Evaluators")


class EvaluatorsRequest(BaseModel):
    evaluators: List[EvaluatorRegistration] = Field(
        ..., description="Evaluator details", title="Evaluators"
    )


class EvaluatorsResponse(BaseModel):
    evaluators: List[EvaluatorRegistration] = Field(
        ..., description="Evaluator details", title="Evaluators"
    )


class HpcResources(BaseModel):
    num_cores_per_node: Optional[int] = Field(
        None, description="Number of cores per node.", title="Num Cores Per Node"
    )
    num_gpus_per_node: Optional[int] = Field(
        None, description="Number of GPUs per node.", title="Num Gpus Per Node"
    )
    exclusive: Optional[bool] = Field(
        None, description="To not share nodes with other running jobs.", title="Exclusive"
    )
    queue: Optional[str] = Field(None, description="Scheduler's queue.", title="Queue")


class KubernetesKedaBackend(BaseModel):
    plugin_name: Literal["kubernetes"] = Field(..., title="Plugin Name")
    debug: Optional[bool] = Field(
        False, description="Enable additional debugging of the backend", title="Debug"
    )
    job_script_template_path: Optional[str] = Field(
        None,
        description="Path to the job script template to use in the backend.",
        title="Job Script Template Path",
    )
    working_dir: Optional[str] = Field(
        None, description="Working directory to use in the backend.", title="Working Dir"
    )
    env: Optional[Dict[str, Any]] = Field(
        None, description="Static environment variables needed for job execution.", title="Env"
    )
    cpu_limit: Optional[str] = Field(
        "1.0", description="CPU limit applied to each evaluator instance.", title="Cpu Limit"
    )
    memory_limit: Optional[str] = Field(
        "250M", description="Memory limit applied to each evaluator instance.", title="Memory Limit"
    )
    namespace: Optional[str] = Field(
        "default", description="Kubernetes namespace to use to scale evaluators.", title="Namespace"
    )
    target_resource_kind: Optional[str] = Field(
        "job",
        description="Kubernetes resource kind that the REP scaler should target. Options are ``job``, ``deployment`` and ``statefulset``.",
        title="Target Resource Kind",
    )


class KubernetesResourceScaling(BaseModel):
    plugin_name: Literal["kubernetes_resource_scaling"] = Field(..., title="Plugin Name")
    target_resource_kind: Optional[str] = Field(
        "job",
        description="Kubernetes resource kind that the REP scaler should target. Options are ``job``, ``deployment`` and ``statefulset``.",
        title="Target Resource Kind",
    )


class LocalBackend(BaseModel):
    plugin_name: Literal["local"] = Field(..., title="Plugin Name")
    debug: Optional[bool] = Field(
        False, description="Enable additional debugging of the backend", title="Debug"
    )
    working_dir: Optional[str] = Field(
        None, description="Working directory to use in the backend.", title="Working Dir"
    )
    env: Optional[Dict[str, Any]] = Field(
        None, description="Static environment variables needed for job execution.", title="Env"
    )


class Machine(BaseModel):
    name: str = Field(..., description="Name of the machine", title="Name")
    num_cores: int = Field(..., description="Number of cores available", title="Num Cores")


class MaxAvailableResourceScaling(BaseModel):
    plugin_name: Literal["max_available_resource_scaling"] = Field(..., title="Plugin Name")
    match_all_requirements: Optional[bool] = Field(
        False,
        description="Whether scaling should work with available resource properties specified in compute resource set (default) or require a match of all requirements of the task definition.",
        title="Match All Requirements",
    )


class MockupBackend(BaseModel):
    plugin_name: Literal["mockup"] = Field(..., title="Plugin Name")
    debug: Optional[bool] = Field(
        False, description="Enable additional debugging of the backend", title="Debug"
    )


class Node(BaseModel):
    name: Optional[str] = Field(None, description="Node name", title="Name")
    total_memory_mb: Optional[int] = Field(
        ..., description="Total memory.", title="Total Memory Mb"
    )
    total_cores: Optional[int] = Field(..., description="Number of cores.", title="Total Cores")
    additional_props: Optional[Dict[str, Any]] = Field({}, title="Additional Props")


class NodeGroup(BaseModel):
    node_names: List[str] = Field(..., title="Node Names")
    memory_per_node_mb: Optional[int] = Field(
        ..., description="Memory per node.", title="Memory Per Node Mb"
    )
    cores_per_node: Optional[int] = Field(
        ..., description="Cores per node.", title="Cores Per Node"
    )


class PlatformEnum(Enum):
    windows = "windows"
    linux = "linux"
    darwin = "darwin"


class ProblemDetail(BaseModel):
    type: Optional[str] = Field(None, title="Type")
    title: Optional[str] = Field(None, title="Title")
    status: int = Field(..., title="Status")
    detail: str = Field(..., title="Detail")
    instance: Optional[str] = Field(None, title="Instance")


class ProcessLauncherProcessRunner(BaseModel):
    plugin_name: Literal["process_launcher_module"] = Field(..., title="Plugin Name")
    default_user: Optional[str] = Field(
        None, description="User to use when none is specified.", title="Default User"
    )
    timeout: Optional[int] = Field(
        30, description="Timeout in seconds before the request is aborted.", title="Timeout"
    )
    allowed_users: Optional[List[str]] = Field(
        None, description="Users allowed to launch processes.", title="Allowed Users"
    )
    disallowed_users: Optional[List[str]] = Field(
        ["root"], description="Users not allowed to launch processes.", title="Disallowed Users"
    )
    user_mapping: Optional[Dict[str, str]] = Field(
        {}, description="Map of calling user to system user.", title="User Mapping"
    )
    minimum_uid: Optional[int] = Field(
        1000, description="Minimum UID of users allowed to launch processes.", title="Minimum Uid"
    )
    minimum_gid: Optional[int] = Field(
        1000, description="Minimum GID of users allowed to launch processes.", title="Minimum Gid"
    )


class Queue(BaseModel):
    name: Optional[str] = Field(None, description="Queue name", title="Name")
    node_groups: Optional[List[NodeGroup]] = Field(
        None,
        description="List of node groups associated with the queue (if available).",
        title="Node Groups",
    )
    additional_props: Optional[Dict[str, Any]] = Field({}, title="Additional Props")


class Resources(BaseModel):
    num_cores: Optional[int] = Field(None, description="Number of cores.", title="Num Cores")
    platform: Optional[PlatformEnum] = Field(
        None, description="Basic platform information. Options are ``'linux'`` and ``'windows'``."
    )
    memory: Optional[int] = Field(None, description="Amount of RAM in bytes.", title="Memory")
    disk_space: Optional[int] = Field(
        None, description="Amount of disk space in bytes.", title="Disk Space"
    )
    custom: Optional[Dict[str, Optional[Union[bool, int, str, float]]]] = Field(
        {}, description="Custom resource properties.", title="Custom"
    )
    num_instances: Optional[int] = Field(
        None,
        description="Number of instances/jobs that can be created on the compute resource set.",
        title="Num Instances",
    )


class RestLauncherProcessRunner(BaseModel):
    plugin_name: Literal["process_launcher_service"] = Field(..., title="Plugin Name")
    launcher_url: Optional[str] = Field(
        "http://localhost:4911",
        description="URL to use when none is specified.",
        title="Launcher Url",
    )
    verify_ssl: Optional[bool] = Field(
        True, description="Check the SSL certificate for HTTPS launchers.", title="Verify Ssl"
    )
    timeout: Optional[int] = Field(
        30, description="Timeout in seconds before the request is aborted.", title="Timeout"
    )
    shell: Optional[bool] = Field(
        True, description="Enable the shell interpretation on subprocess run.", title="Shell"
    )


class ScalerApplicationInfo(BaseModel):
    name: str = Field(..., description="Application name.", title="Name")
    version: str = Field(..., description="Application version.", title="Version")
    install_path: str = Field(
        ..., description="Installation path of application.", title="Install Path"
    )
    executable: str = Field(
        ..., description="Executable path to run application.", title="Executable"
    )
    environment: Optional[Dict[str, Any]] = Field(
        None, description="Environment setup for the process.", title="Environment"
    )
    capabilities: Optional[List[str]] = Field(
        None, description="Capabilities of the application.", title="Capabilities"
    )
    customization_hook: Optional[Dict[str, Any]] = Field(
        None,
        description="Details of a custom hook used to modify the configuration before runs are performed.",
        title="Customization Hook",
    )
    resource_name: Optional[str] = Field(
        None,
        description="Kubernetes object (deployment/statefulset) name or solver image used as target resource by KEDA",
        title="Resource Name",
    )
    evaluator_image: Optional[str] = Field(
        None, description="Evaluator image to be used", title="Evaluator Image"
    )
    scaling_max_eval_instances: Optional[int] = Field(
        1,
        description="Maximum number of instances that can be created when scaling up.",
        title="Scaling Max Eval Instances",
    )
    scaling_min_eval_instances: Optional[int] = Field(
        0,
        description="Minimum number of instances than can be terminated when scaling down.",
        title="Scaling Min Eval Instances",
    )
    scaling_threshold: Optional[int] = Field(
        1,
        description="Threshold value to determine when Kubernetes deployments should be scaled up or down.",
        title="Scaling Threshold",
    )
    cool_down_period: Optional[int] = Field(
        60,
        description="Period to wait before scaling down the resource to 0 instances.",
        title="Cool Down Period",
    )


class ScalerRegistration(BaseModel):
    id: Optional[str] = Field(None, description="Unique ID for this worker.", title="Id")
    name: Optional[str] = Field(
        None, description="User-defined name for this worker.", title="Name"
    )
    last_modified: Optional[datetime] = Field(
        None,
        description="Date and time when the registration was last modified.",
        title="Last Modified",
    )
    host_id: Optional[str] = Field(
        None, description="Static, hardware and configuration-based UUID.", title="Host Id"
    )
    host_name: Optional[str] = Field(
        None, description="Name of the host that the worker is running on.", title="Host Name"
    )
    username: Optional[str] = Field(
        None, description="Username that the worker authenticated with.", title="Username"
    )
    platform: Optional[str] = Field(
        None, description="OS that the evaluator is running on.", title="Platform"
    )
    build_info: Optional[Dict[str, Any]] = Field(
        {}, description="Detailed build information.", title="Build Info"
    )
    config_modified: Optional[datetime] = Field(
        None,
        description="Date and time of the configuration's last modification.",
        title="Config Modified",
    )


class ScalersCountResponse(BaseModel):
    num_scalers: Optional[int] = Field(0, title="Num Scalers")


class ScalersRequest(BaseModel):
    scalers: List[ScalerRegistration] = Field(..., description="Scaler details", title="Scalers")


class ScalersResponse(BaseModel):
    scalers: List[ScalerRegistration] = Field(..., description="Scaler details", title="Scalers")


class ServiceUserProcessRunner(BaseModel):
    plugin_name: Literal["service_user_module"] = Field(..., title="Plugin Name")


class Status(BaseModel):
    time: str = Field(..., title="Time")
    build: Dict[str, Any] = Field(..., title="Build")


class ClusterInfo(BaseModel):
    id: Optional[str] = Field(None, description="Unique ID for the database.", title="Id")
    crs_id: Optional[str] = Field(None, description="Compute resource set ID.", title="Crs Id")
    name: Optional[str] = Field(None, description="Cluster name.", title="Name")
    queues: Optional[List[Queue]] = Field([], title="Queues")
    nodes: Optional[List[Node]] = Field([], title="Nodes")
    additional_props: Optional[Dict[str, Dict[str, Any]]] = Field({}, title="Additional Props")


class Context(BaseModel):
    custom: Optional[Dict[str, Optional[Union[int, bool, str, float]]]] = Field(
        {}, description="Custom runtime properties.", title="Custom"
    )
    machines_list: Optional[List[Machine]] = Field(
        None,
        description="List of machines for distributed parallel processing.",
        title="Machines List",
    )


class EvaluatorResources(BaseModel):
    num_cores: Optional[int] = Field(None, description="Number of cores.", title="Num Cores")
    platform: Optional[PlatformEnum] = Field(
        None, description="Basic platform information. Options are ``'linux'`` and ``'windows'``."
    )
    memory: Optional[int] = Field(None, description="Amount of RAM in bytes.", title="Memory")
    disk_space: Optional[int] = Field(
        None, description="Amount of disk space in bytes.", title="Disk Space"
    )
    custom: Optional[Dict[str, Optional[Union[bool, int, str, float]]]] = Field(
        {}, description="Custom resource properties.", title="Custom"
    )
    hpc_resources: Optional[HpcResources] = None


class OrchestrationInterfacesBackend(BaseModel):
    plugin_name: Literal["orchestration_interfaces"] = Field(..., title="Plugin Name")
    debug: Optional[bool] = Field(
        False, description="Enable additional debugging of the backend", title="Debug"
    )
    scheduler_type: Optional[str] = Field(
        "slurm",
        description="Job scheduler type, such as ``slurm``, ``pbs``, ``uge``, or ``lsf`` to use in the backend.",
        title="Scheduler Type",
    )
    scheduler_queue_default: Optional[str] = Field(
        None,
        description="Job scheduler queue to use for submission.",
        title="Scheduler Queue Default",
    )
    scheduler_command_override: Optional[str] = Field(
        None,
        description="Path to the JSON file with custom scheduler command definitions.",
        title="Scheduler Command Override",
    )
    scheduler_script_override: Optional[str] = Field(
        None,
        description="Path to the shell script to template for the scheduler.",
        title="Scheduler Script Override",
    )
    exclusive_default: Optional[bool] = Field(
        False,
        description="Request the scheduler to hold the nodes exclusively for one request.",
        title="Exclusive Default",
    )
    distributed_default: Optional[bool] = Field(
        True,
        description="Allow the scheduler to provide multiple machines to fulfill the request.",
        title="Distributed Default",
    )
    num_cores_default: Optional[int] = Field(
        1,
        description="Number of cores to request from the scheduler for a task.",
        title="Num Cores Default",
    )
    working_dir: Optional[str] = Field(
        None, description="Working directory to use in the backend.", title="Working Dir"
    )
    env: Optional[Dict[str, Any]] = Field(
        None, description="Static environment variables needed for job execution.", title="Env"
    )
    process_runner: Optional[
        Union[ServiceUserProcessRunner, ProcessLauncherProcessRunner, RestLauncherProcessRunner]
    ] = Field(
        {"plugin_name": "service_user_module"},
        description="Process runner used to execute commands.",
        discriminator="plugin_name",
        title="Process Runner",
    )
    create_workdir: Optional[bool] = Field(
        True,
        description="Create base and/or user-specific working directories at runtime.",
        title="Create Workdir",
    )
    use_templates: Optional[bool] = Field(
        True,
        description="Use the templated versions of the scripts and write them to the working directory.",
        title="Use Templates",
    )


class ComputeResourceSet(BaseModel):
    name: Optional[str] = Field(
        "default", description="Name of the compute resource set.", title="Name"
    )
    id: Optional[str] = Field(None, description="ID for this set.", title="Id")
    scaler_id: Optional[str] = Field(
        None,
        description="Temporary. To be removed after transitioning to client_id.",
        title="Scaler Id",
    )
    last_modified: Optional[datetime] = Field(
        None, description="Last modified time.", title="Last Modified"
    )
    backend: Optional[
        Union[KubernetesKedaBackend, OrchestrationInterfacesBackend, LocalBackend, MockupBackend]
    ] = Field(
        {"debug": False, "plugin_name": "local"},
        description="Backend to use in this compute resource set.",
        discriminator="plugin_name",
        title="Backend",
    )
    scaling_strategy: Optional[
        Union[MaxAvailableResourceScaling, KubernetesResourceScaling]
    ] = Field(
        {"match_all_requirements": False, "plugin_name": "max_available_resource_scaling"},
        description="Scaling strategy to use in this compute resource set.",
        discriminator="plugin_name",
        title="Scaling Strategy",
    )
    available_resources: Optional[Resources] = Field(
        {"custom": {}}, description="Available resources in the compute resource set."
    )
    available_applications: Optional[List[ScalerApplicationInfo]] = Field(
        [], description="List of available applications.", title="Available Applications"
    )
    evaluator_requirements_matching: Optional[bool] = Field(
        False,
        description="Whether the evaluators should do matching of resource and software requirements.",
        title="Evaluator Requirements Matching",
    )
    evaluator_task_directory_cleanup: Optional[EvaluatorTaskDirectoryCleanup] = Field(
        "always",
        description="Cleanup policy for task directories that are passed to evaluators.",
        title="Evaluator Task Directory Cleanup",
    )
    evaluator_auto_shutdown_time: Optional[int] = Field(
        20,
        description="Time after which to shutdown the evaluator if not running any jobs.",
        title="Evaluator Auto Shutdown Time",
    )
    evaluator_loop_interval: Optional[int] = Field(
        5,
        description="Number of seconds between each iteration of the evaluator's main loop.",
        title="Evaluator Loop Interval",
    )


class ComputeResourceSetsRequest(BaseModel):
    compute_resource_sets: List[ComputeResourceSet] = Field(
        ..., description="Compute resource set details", title="Compute Resource Sets"
    )


class ComputeResourceSetsResponse(BaseModel):
    compute_resource_sets: List[ComputeResourceSet] = Field(
        ..., description="Compute resource set details", title="Compute Resource Sets"
    )


class EvaluatorConfiguration(BaseModel):
    id: Optional[str] = Field(None, description="Unique database ID (read-only).", title="Id")
    evaluator_id: Optional[str] = Field(
        None, description="ID of the parent evaluator (read-only).", title="Evaluator Id"
    )
    last_modified: Optional[datetime] = Field(
        None, description="Last modified time", title="Last Modified"
    )
    working_directory: Optional[str] = Field(None, title="Working Directory")
    local_file_cache_max_size: Optional[int] = Field(
        None, description="Maximum allowed cache size in bytes.", title="Local File Cache Max Size"
    )
    max_num_parallel_tasks: Optional[int] = Field(None, title="Max Num Parallel Tasks")
    task_directory_cleanup: Optional[TaskDirectoryCleanupEnum] = Field(
        None, title="Task Directory Cleanup"
    )
    resources: Optional[EvaluatorResources] = {"custom": {}}
    task_manager_type: Optional[str] = Field(None, title="Task Manager Type")
    loop_interval: Optional[float] = Field(
        5.0,
        description="Number of seconds between each iteration of the evaluator's main loop.",
        title="Loop Interval",
    )
    local_file_cache: Optional[bool] = Field(
        True,
        description="Whether to configure a local file cache in the file tool.",
        title="Local File Cache",
    )
    applications: Optional[List[ApplicationInfo]] = Field(
        [], description="List of available applications.", title="Applications"
    )
    project_server_select: Optional[bool] = Field(
        True,
        description="Get project assignments from the server instead of using the locally set values",
        title="Project Server Select",
    )
    project_list: Optional[List[str]] = Field(
        [],
        description="IDs of projects that the evaluator should work on, in order",
        title="Project List",
    )
    project_assignment_mode: Optional[str] = Field(
        "all_active",
        description="Specifies how the evaluator selects projects to work on.             One of: disabled, all_active, list",
        title="Project Assignment Mode",
    )
    context: Optional[Context] = Field(
        {"custom": {}}, description="Runtime properties to pass to executed tasks."
    )


class EvaluatorConfigurationUpdate(BaseModel):
    id: Optional[str] = Field(None, description="Unique database ID (read-only).", title="Id")
    evaluator_id: Optional[str] = Field(
        None, description="ID of the parent evaluator (read-only).", title="Evaluator Id"
    )
    last_modified: Optional[datetime] = Field(
        None, description="Last modified time", title="Last Modified"
    )
    working_directory: Optional[str] = Field(None, title="Working Directory")
    local_file_cache_max_size: Optional[int] = Field(
        None, description="Maximum allowed cache size in bytes.", title="Local File Cache Max Size"
    )
    max_num_parallel_tasks: Optional[int] = Field(None, title="Max Num Parallel Tasks")
    task_directory_cleanup: Optional[TaskDirectoryCleanupEnum] = Field(
        None, title="Task Directory Cleanup"
    )
    resources: Optional[EvaluatorResources] = {"custom": {}}
    name: Optional[str] = Field(
        None,
        description="Update the name of the evaluator (updating the registration).",
        title="Name",
    )
    loop_interval: Optional[float] = Field(
        None,
        description="Number of seconds between each iteration of the evaluator's main loop.",
        title="Loop Interval",
    )
    local_file_cache: Optional[bool] = Field(
        None,
        description="Whether to configure a local file cache in the file tool.",
        title="Local File Cache",
    )
    applications: Optional[List[ApplicationInfo]] = Field(
        [], description="List of available applications.", title="Applications"
    )
    project_list: Optional[List[str]] = Field(
        None,
        description="IDs of projects that the evaluator should work on in order.",
        title="Project List",
    )
    project_assignment_mode: Optional[str] = Field(
        None,
        description="How the evaluator selects projects to work on. Options are: disabled, all_active, list.",
        title="Project Assignment Mode",
    )
    context: Optional[ContextUpdate] = Field(
        {"custom": {}}, description="Runtime properties to pass to executed tasks."
    )


class EvaluatorConfigurationUpdatesRequest(BaseModel):
    configuration_updates: List[EvaluatorConfigurationUpdate] = Field(
        ..., description="Configuration update details", title="Configuration Updates"
    )


class EvaluatorConfigurationUpdatesResponse(BaseModel):
    configuration_updates: List[EvaluatorConfigurationUpdate] = Field(
        ..., description="Configuration update details", title="Configuration Updates"
    )


class EvaluatorConfigurationsResponse(BaseModel):
    configurations: List[EvaluatorConfiguration] = Field(
        ..., description="Evaluator configurations", title="Configurations"
    )
