#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel, field_validator

from internal.exception import FailException


class CategoryEntity(BaseModel):

    category: str 
    name: str  
    icon: str  

    @field_validator("icon")
    def check_icon_extension(cls, value: str):

        if not value.endswith(".svg"):
            raise FailException("xxxxxxx")
        return value
