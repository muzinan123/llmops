#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field


class ToolEntity(BaseModel):
    id: str = Field(default="", description="xxxxxx")
    name: str = Field(default="", description="xxxxxx")
    url: str = Field(default="", description="xxxxxx")
    method: str = Field(default="get", description="xxxxx")
    description: str = Field(default="", description="xxxxxx")
    headers: list[dict] = Field(default_factory=list, description="xxxxxxx")
    parameters: list[dict] = Field(default_factory=list, description="xxxxxxx")
