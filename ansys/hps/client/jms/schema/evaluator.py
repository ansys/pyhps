# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import marshmallow
from marshmallow import fields
from marshmallow.validate import OneOf

from ansys.hps.client.common import ObjectSchema, RestrictedValue

project_assignment_modes = ["disabled", "all_active", "project_list"]


class EvaluatorConfigurationUpdateSchema(ObjectSchema):
    class Meta:
        ordered = True

    name = fields.String(allow_none=True)
    applications = fields.List(fields.Dict(), allow_none=True)
    max_num_parallel_tasks = fields.Integer(allow_none=True)
    loop_interval = fields.Float(allow_none=True)
    working_directory = fields.String(allow_none=True)
    local_file_cache = fields.Boolean(allow_none=True)
    local_file_cache_max_size = fields.Integer(allow_none=True)
    task_directory_cleanup = fields.String(
        validate=OneOf(["always", "on_success", "never"]), allow_none=True
    )
    custom_resource_properties = fields.Dict(allow_none=True)


class EvaluatorRegistrationConfigurationContextSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.INCLUDE

    custom = fields.Dict(allow_none=True, keys=fields.Str(), values=RestrictedValue())


class EvaluatorRegistrationConfigurationResourcesSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.INCLUDE

    custom = fields.Dict(allow_none=True, keys=fields.Str(), values=RestrictedValue())


class EvaluatorRegistrationConfigurationSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.INCLUDE

    context = fields.Nested(EvaluatorRegistrationConfigurationContextSchema, allow_none=True)
    resources = fields.Nested(EvaluatorRegistrationConfigurationResourcesSchema, allow_none=True)


class EvaluatorSchema(ObjectSchema):
    class Meta:
        ordered = True

    host_id = fields.String(
        metadata={
            "description": "Unique identifier built from hardware information and "
            "selected configuration details of an evaluator."
        }
    )
    name = fields.String(allow_none=True, metadata={"description": "Name of the evaluator."})
    hostname = fields.String(
        allow_none=True,
        metadata={"description": "Name of the host on which the evaluator is running."},
    )
    username = fields.String(
        allow_none=True,
        metadata={"description": "HPS user the evaluator is connected to JMS as."},
    )
    platform = fields.String(
        allow_none=True,
        metadata={"description": "Operating system on which the evaluator is running."},
    )
    task_manager_type = fields.String(
        allow_none=True, metadata={"description": "Type of the task manager used by the evaluator."}
    )
    project_server_select = fields.Bool(
        allow_none=True,
        metadata={
            "description": "Whether the evaluator allows "
            "server-driven assignment of projects or uses "
            "it's own local settings."
        },
    )
    alive_update_interval = fields.Int(
        allow_none=True,
        metadata={
            "description": "Minimal time (in seconds) between evaluator registration updates."
        },
    )
    update_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "Last time the evaluator updated it's registration details. "
            "Used to check which evaluators are alive."
        },
    )
    external_access_port = fields.Integer(
        allow_none=True,
        metadata={"description": "Port number for external access to the evaluator."},
    )
    project_assignment_mode = fields.String(
        validate=OneOf(project_assignment_modes),
        allow_none=True,
        metadata={"description": "Which strategy to use for selecting projects to work on."},
    )
    project_list = fields.List(
        fields.String,
        metadata={"description": "List of projects on which this evaluator should be working."},
    )
    configuration = fields.Nested(
        EvaluatorRegistrationConfigurationSchema,
        allow_none=True,
        metadata={
            "description": "Details of the evaluator configuration, "
            "including hardware info and available applications."
        },
    )
    configuration_updates = fields.Nested(
        EvaluatorConfigurationUpdateSchema,
        allow_none=True,
        metadata={"description": "Changes to the evaluator configurations."},
    )
    build_info = fields.Dict(
        allow_none=True,
        metadata={"description": "Evaluator's build information."},
    )
