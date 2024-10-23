#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from internal.lib.helper import dynamic_import
from .tool_entity import ToolEntity


class ProviderEntity(BaseModel):

    name: str  
    label: str  
    description: str 
    icon: str 
    background: str  
    category: str 
    created_at: int = 0 


class Provider(BaseModel):
    name: str  
    position: int  
    provider_entity: ProviderEntity  
    tool_entity_map: dict[str, ToolEntity] = Field(default_factory=dict)  
    tool_func_map: dict[str, Any] = Field(default_factory=dict) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._provider_init()

    def get_tool(self, tool_name: str) -> Any:
        return self.tool_func_map.get(tool_name)

    def get_tool_entity(self, tool_name: str) -> ToolEntity:

        return self.tool_entity_map.get(tool_name)

    def get_tool_entities(self) -> list[ToolEntity]:
        return list(self.tool_entity_map.values())

    def _provider_init(self):

        current_path = os.path.abspath(__file__)
        entities_path = os.path.dirname(current_path)
        provider_path = os.path.join(os.path.dirname(entities_path), "providers", self.name)

        positions_yaml_path = os.path.join(provider_path, "positions.yaml")
        with open(positions_yaml_path, encoding="utf-8") as f:
            positions_yaml_data = yaml.safe_load(f)

        for tool_name in positions_yaml_data:
            tool_yaml_path = os.path.join(provider_path, f"{tool_name}.yaml")
            with open(tool_yaml_path, encoding="utf-8") as f:
                tool_yaml_data = yaml.safe_load(f)

            self.tool_entity_map[tool_name] = ToolEntity(**tool_yaml_data)

            self.tool_func_map[tool_name] = dynamic_import(
                f"internal.core.tools.builtin_tools.providers.{self.name}",
                tool_name,
            )
