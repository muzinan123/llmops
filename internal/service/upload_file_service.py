#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from injector import inject

from internal.model import UploadFile
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class UploadFileService(BaseService):

    db: SQLAlchemy

    def create_upload_file(self, **kwargs) -> UploadFile:

        return self.create(UploadFile, **kwargs)
