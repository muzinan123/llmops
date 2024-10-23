#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from langchain_core.tools import BaseTool


class CurrentTimeTool(BaseTool):

    name = "current_time"
    description = "xxxxxx"

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


def current_time(**kwargs) -> BaseTool:
    return CurrentTimeTool()
