#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class CompletionReq(FlaskForm):
    query = StringField("query", validators=[
        DataRequired(message="xxxxxxx"),
        Length(max=2000, message="xxxxxxxxxxxx"),
    ])
