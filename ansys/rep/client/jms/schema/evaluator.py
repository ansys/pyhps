# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from marshmallow import fields
from marshmallow.validate import OneOf

from .base import ObjectSchema

project_assignment_modes = ["disabled", "all_active", "project_list"]


class EvaluatorSchema(ObjectSchema):
    class Meta:
        ordered = True

    host_id = fields.String(
        description="Unique identifier built from hardware information and "
        "selected job_definition details of an evaluator."
    )
    name = fields.String(allow_none=True, description="Name of the evaluator.")
    hostname = fields.String(
        allow_none=True, description="Name of the host on which the evaluator is running."
    )
    platform = fields.String(
        allow_none=True, description="Operating system on which the evaluator is running."
    )
    task_manager_type = fields.String(
        allow_none=True, description="Type of the task manager used by the evaluator."
    )
    project_server_select = fields.Bool(
        allow_none=True,
        description="Whether the evaluator allows server-driven assignment of projects or uses "
        "it's own local settings.",
    )
    alive_update_interval = fields.Int(
        allow_none=True,
        description="Minimal time (in seconds) between evaluator registration updates.",
    )
    update_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="Last time the evaluator updated it's registration details. "
        "Used to check which evaluators are alive.",
    )
    external_access_port = fields.Integer(
        allow_none=True, description="Port number for external access to the evaluator."
    )
    project_assignment_mode = fields.String(
        validate=OneOf(project_assignment_modes),
        allow_none=True,
        description="Which strategy to use for selecting projects to work on.",
    )
    project_list = fields.List(
        fields.String, description="List of projects on which this evaluator should be working."
    )
    configuration = fields.Dict(
        allow_none=True,
        description="Details of the evaluator configuration, "
        "including hardware info and available applications.",
    )
