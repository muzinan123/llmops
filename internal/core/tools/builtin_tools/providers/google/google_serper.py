#!/usr/bin/env python
# -*- coding: utf-8 -*-

from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="xxxxx.")


@add_attribute("args_schema", GoogleSerperArgsSchema)
def google_serper(**kwargs) -> BaseTool:
    return GoogleSerperRun(
        name="google_serper",
        description="xxxxxxxxxxxx",
        args_schema=GoogleSerperArgsSchema,
        api_wrapper=GoogleSerperAPIWrapper(),
    )
