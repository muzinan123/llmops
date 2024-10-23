#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, Length, URL, Optional

from internal.model import ApiToolProvider, ApiTool
from pkg.paginator import PaginatorReq
from .schema import ListField


class ValidateOpenAPISchemaReq(FlaskForm):
    openapi_schema = StringField("openapi_schema", validators=[
        DataRequired(message="openapi_schema")
    ])


class GetApiToolProvidersWithPageReq(PaginatorReq):
    search_word = StringField("search_word", validators=[
        Optional()
    ])


class CreateApiToolReq(FlaskForm):
    name = StringField("name", validators=[
        DataRequired(message="xxxx"),
        Length(min=1, max=30, message="xxxxxx"),
    ])
    icon = StringField("icon", validators=[
        DataRequired(message="xxxxxxx"),
        URL(message="xxxxxxxxx"),
    ])
    openapi_schema = StringField("openapi_schema", validators=[
        DataRequired(message="xxxxxx")
    ])
    headers = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidationError("xxxxxxx")
            if set(header.keys()) != {"key", "value"}:
                raise ValidationError("xxxxxxxxx")


class UpdateApiToolProviderReq(FlaskForm):
    name = StringField("name", validators=[
        DataRequired(message="xxxxx"),
        Length(min=1, max=30, message="xxxxx"),
    ])
    icon = StringField("icon", validators=[
        DataRequired(message="xxxxxx"),
        URL(message="xxxxxx"),
    ])
    openapi_schema = StringField("openapi_schema", validators=[
        DataRequired(message="openapi_schemaxxxxxx")
    ])
    headers = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidationError("xxxxxxxx")
            if set(header.keys()) != {"key", "value"}:
                raise ValidationError("xxxxxxxx")


class GetApiToolProviderResp(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    openapi_schema = fields.String()
    headers = fields.List(fields.Dict, default=[])
    created_at = fields.Integer(default=0)

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "openapi_schema": data.openapi_schema,
            "headers": data.headers,
            "created_at": int(data.created_at.timestamp()),
        }


class GetApiToolResp(Schema):
    id = fields.UUID()
    name = fields.String()
    description = fields.String()
    inputs = fields.List(fields.Dict, default=[])
    provider = fields.Dict()

    @pre_dump
    def process_data(self, data: ApiTool, **kwargs):
        provider = data.provider
        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            "inputs": [{k: v for k, v in parameter.items() if k != "in"} for parameter in data.parameters],
            "provider": {
                "id": provider.id,
                "name": provider.name,
                "icon": provider.icon,
                "description": provider.description,
                "headers": provider.headers,
            }
        }


class GetApiToolProvidersWithPageResp(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    headers = fields.List(fields.Dict, default=[])
    tools = fields.List(fields.Dict, default=[])
    created_at = fields.Integer(default=0)

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        tools = data.tools
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "headers": data.headers,
            "tools": [{
                "id": tool.id,
                "description": tool.description,
                "name": tool.name,
                "inputs": [{k: v for k, v in parameter.items() if k != "in"} for parameter in tool.parameters]
            } for tool in tools],
            "created_at": int(data.created_at.timestamp())
        }
