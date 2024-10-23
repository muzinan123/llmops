#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class ToolParamType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class ToolParam(BaseModel):
    name: str  
    label: str  
    type: ToolParamType  
    required: bool = False  
    default: Optional[Any] = None  
    min: Optional[float] = None 
    max: Optional[float] = None  
    options: list[dict[str, Any]] = Field(default_factory=list)  


class ToolEntity(BaseModel):
    name: str 
    label: str  
    description: str 
    params: list[ToolParam] = Field(default_factory=list) 
