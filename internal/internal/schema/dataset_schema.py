#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL, Optional

from internal.model import Dataset
from pkg.paginator import PaginatorReq


class CreateDatasetReq(FlaskForm):
    name = StringField("name", validators=[
        DataRequired("xxxxx"),
        Length(max=100, message="xxxxxx"),
    ])
    icon = StringField("icon", validators=[
        DataRequired("xxxxxx"),
        URL("xxxxxx"),
    ])
    description = StringField("description", default="", validators=[
        Optional(),
        Length(max=2000, message="xxxxxxxx")
    ])


class GetDatasetResp(Schema):

    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "hit_count": data.hit_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


class UpdateDatasetReq(FlaskForm):

    name = StringField("name", validators=[
        DataRequired("xxxxxxxx"),
        Length(max=100, message="xxxxx"),
    ])
    icon = StringField("icon", validators=[
        DataRequired("xxxxx"),
        URL("xxxxxxx"),
    ])
    description = StringField("description", default="", validators=[
        Optional(),
        Length(max=2000, message="xxxxxxx")
    ])


class GetDatasetsWithPageReq(PaginatorReq):
    search_word = StringField("search_word", default="", validators=[
        Optional(),
    ])


class GetDatasetsWithPageResp(Schema):
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }
