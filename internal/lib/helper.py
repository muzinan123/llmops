#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)

def add_attribute(attr_name: str, attr_value: Any):

    def decorator(func):
        setattr(func, attr_name, attr_value)
        return func

    return decorator
