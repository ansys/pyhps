# generated by datamodel-codegen:
#   filename:  jms.json
#   timestamp: 2022-09-01T05:00:53+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Task Definition Templates
class TaskDefinitionTemplate(BaseModel):
    id: Optional[str] = Field(
        None,
        description="Object's identifier, assigned by the server at creation time. Not controlled by the user",
    )
    modification_time: Optional[datetime] = None
    creation_time: Optional[datetime] = None
    name: str = None
    version: Optional[str] = None

# Parameter Definitions
class ParameterDefinitionBase(BaseModel):
    id: Optional[str] = Field(
        None,
        description="Object's identifier, assigned by the server at creation time. Not controlled by the user",
    )
    name: Optional[str] = None
    version: Optional[str] = None
    quantity_name: Optional[str] = Field(
        None,
        description="Name of the quantity the parameter represents, e.g. Length.",
    )
    units: Optional[str] = Field(
        None,
        description="Units for the parameter.",
    )
    display_text: Optional[str] = Field(
        None,
        description="Text to display as the parameter name.",
    )
    mode: Optional[str] = Field(
        None,
        description="Indicates whether it's an input or output parameter. Filled server side.",
    )

class FloatParameterDefinition(ParameterDefinitionBase):
    default: Optional[float] = None
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    step: Optional[float] = None
    cyclic: Optional[bool] = None
    value_list: Optional[List[float]] = None
    

class IntParameterDefinition(ParameterDefinitionBase):
    default: Optional[int] = None
    lower_limit: Optional[int] = None
    upper_limit: Optional[int] = None
    step: Optional[int] = None
    cyclic: Optional[bool] = None

class BoolParameterDefinition(ParameterDefinitionBase):
    default: Optional[bool] = None

class StringParameterDefinition(ParameterDefinitionBase):
    default: Optional[str] = None
    value_list: Optional[List[str]] = None

class ParameterDefinition(BaseModel):
     __root__: Union[FloatParameterDefinition, IntParameterDefinition, BoolParameterDefinition, StringParameterDefinition]