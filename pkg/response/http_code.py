#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum


class HttpCode(str, Enum):
    SUCCESS = "success"  
    FAIL = "fail"  
    NOT_FOUND = "not_found"  
    UNAUTHORIZED = "unauthorized"  
    FORBIDDEN = "forbidden"  
    VALIDATE_ERROR = "validate_error"  
