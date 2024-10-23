#!/usr/bin/env python
# -*- coding: utf-8 -*-

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


class DDGInput(BaseModel):
    query: str = Field(description="xxxxx")


@add_attribute("args_schema", DDGInput)
def duckduckgo_search(**kwargs) -> BaseTool:
    return DuckDuckGoSearchRun(
        description="xxxxxxxxxxx",
        args_schema=DDGInput,
    )
