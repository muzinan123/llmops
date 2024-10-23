#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, AnyOf, Optional

from .schema import ListField, DictField


class CreateDocumentsReq(FlaskForm):
    upload_file_ids = ListField("upload_file_ids", validators=[
        DataRequired("xxxxx"),
    ])
    process_type = StringField("process_type", validators=[
        DataRequired("xxxxxx"),
        AnyOf(values=["automic", "custom"], message="xxxxxxx"),
    ])
    rule = DictField("process_rule", validators=[
        Optional(),
    ])
