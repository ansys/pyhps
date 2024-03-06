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

"""Module providing the task command schema."""

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo


class TaskCommandSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    task_id = fields.String(
        allow_none=False,
        metadata={"description": "ID of the :class:`Task` instance that the command is linked to."},
    )
    command_def_id = fields.String(  # todo better: command_definition_id
        allow_none=False,
        metadata={
            "description": "ID of the :class:`TaskCommandDefinition` instance"
            " that the command is linked to."
        },
    )

    # todo, name what for??
    name = fields.String(
        allow_none=False,
        load_only=True,
        metadata={
            "description": "Name of the command (corresponds to the "
            "function name in the execution script)."
        },
    )

    # todo: maybe argument values?
    arguments = fields.Dict(
        allow_none=True,
        load_only=True,
        metadata={"description": "Values of the command arguments."},
    )

    running_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the command was set to running."},
    )
    finished_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the command was completed."},
    )

    status = fields.String(
        allow_none=True, metadata={"description": "Evaluation status."}
    )  # todo OneOf
