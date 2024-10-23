#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject

from internal.core.file_extractor import FileExtractor
from internal.model import UploadFile
from internal.schema.dataset_schema import (
    CreateDatasetReq,
    GetDatasetResp,
    UpdateDatasetReq,
    GetDatasetsWithPageReq,
    GetDatasetsWithPageResp,
)
from internal.service import DatasetService, EmbeddingsService, JiebaService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_message, success_json
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class DatasetHandler:
    dataset_service: DatasetService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    file_extractor: FileExtractor
    db: SQLAlchemy

    def embeddings_query(self):
        upload_file = self.db.session.query(UploadFile).get("0092971c-1f1f-4a1e-a7bd-4aac5f2c6991")
        content = self.file_extractor.load(upload_file, True)
        return success_json({"content": content})

    def create_dataset(self):

        req = CreateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.dataset_service.create_dataset(req)

        return success_message("xxxx")

    def get_dataset(self, dataset_id: UUID):
        dataset = self.dataset_service.get_dataset(dataset_id)
        resp = GetDatasetResp()

        return success_json(resp.dump(dataset))

    def update_dataset(self, dataset_id: UUID):
        req = UpdateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.dataset_service.update_dataset(dataset_id, req)

        return success_message("xxxxx")

    def get_datasets_with_page(self):
        req = GetDatasetsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        datasets, paginator = self.dataset_service.get_datasets_with_page(req)

        resp = GetDatasetsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(datasets), paginator=paginator))
