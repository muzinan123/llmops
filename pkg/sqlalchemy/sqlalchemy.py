#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQAlchemy


class SQLAlchemy(_SQAlchemy):

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
