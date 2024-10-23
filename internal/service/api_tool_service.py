#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from injector import inject
from sqlalchemy import desc

from internal.core.tools.api_tools.entities import OpenAPISchema
from internal.core.tools.api_tools.providers import ApiProviderManager
from internal.exception import (
    ValidateErrorException,
    NotFoundException,
)
from internal.model import ApiToolProvider, ApiTool
from internal.schema.api_tool_schema import (
    CreateApiToolReq,
    GetApiToolProvidersWithPageReq,
    UpdateApiToolProviderReq,
)
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class ApiToolService(BaseService):

    db: SQLAlchemy
    api_provider_manager: ApiProviderManager

    def update_api_tool_provider(self, provider_id: UUID, req: UpdateApiToolProviderReq):

        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"


        api_tool_provider = self.get(ApiToolProvider, provider_id)
        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise ValidateErrorException("xxxxxx")

        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)

        check_api_tool_provider = self.db.session.query(ApiToolProvider).filter(
            ApiToolProvider.account_id == account_id,
            ApiToolProvider.name == req.name.data,
            ApiToolProvider.id != api_tool_provider.id,
        ).one_or_none()
        if check_api_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name.data}已存在")


        with self.db.auto_commit():

            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == api_tool_provider.id,
                ApiTool.account_id == account_id,
            ).delete()


        self.update(
            api_tool_provider,
            name=req.name.data,
            icon=req.icon.data,
            headers=req.headers.data,
            description=openapi_schema.description,
            openapi_schema=req.openapi_schema.data,
        )

        # 7.新增工具信息从而完成覆盖更新
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    def get_api_tool_providers_with_page(self, req: GetApiToolProvidersWithPageReq) -> tuple[list[Any], Paginator]:

        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        paginator = Paginator(db=self.db, req=req)

        filters = [ApiToolProvider.account_id == account_id]
        if req.search_word.data:
            filters.append(ApiToolProvider.name.ilike(f"%{req.search_word.data}%"))

        api_tool_providers = paginator.paginate(
            self.db.session.query(ApiToolProvider).filter(*filters).order_by(desc("created_at"))
        )

        return api_tool_providers, paginator

    def get_api_tool(self, provider_id: UUID, tool_name: str) -> ApiTool:

        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        api_tool = self.db.session.query(ApiTool).filter_by(
            provider_id=provider_id,
            name=tool_name,
        ).one_or_none()

        if api_tool is None or str(api_tool.account_id) != account_id:
            raise NotFoundException("xxxxx")

        return api_tool

    def get_api_tool_provider(self, provider_id: UUID) -> ApiToolProvider:

        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        api_tool_provider = self.get(ApiToolProvider, provider_id)

        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise NotFoundException("xxxxx")

        return api_tool_provider

    def create_api_tool(self, req: CreateApiToolReq) -> None:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)

        api_tool_provider = self.db.session.query(ApiToolProvider).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()
        if api_tool_provider:
            raise ValidateErrorException(f"xxxxxxxx{req.name.data}")

        api_tool_provider = self.create(
            ApiToolProvider,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=openapi_schema.description,
            openapi_schema=req.openapi_schema.data,
            headers=req.headers.data,
        )

        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    def delete_api_tool_provider(self, provider_id: UUID):

        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        api_tool_provider = self.get(ApiToolProvider, provider_id)
        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise NotFoundException("xxxxxxx")

        with self.db.auto_commit():
            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == provider_id,
                ApiTool.account_id == account_id,
            ).delete()

            self.db.session.delete(api_tool_provider)

    @classmethod
    def parse_openapi_schema(cls, openapi_schema_str: str) -> OpenAPISchema:

        try:
            data = json.loads(openapi_schema_str.strip())
            if not isinstance(data, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("xxxxxxxxxx")

        return OpenAPISchema(**data)

    def api_tool_invoke(self):
        provider_id = "d72bb9d7-8794-4caf-bd60-1f992c537065"
        tool_name = "YoudaoSuggest"

        api_tool = self.db.session.query(ApiTool).filter(
            ApiTool.provider_id == provider_id,
            ApiTool.name == tool_name,
        ).one_or_none()
        api_tool_provider = api_tool.provider

        from internal.core.tools.api_tools.entities import ToolEntity
        tool = self.api_provider_manager.get_tool(ToolEntity(
            id=provider_id,
            name=tool_name,
            url=api_tool.url,
            method=api_tool.method,
            description=api_tool.description,
            headers=api_tool_provider.headers,
            parameters=api_tool.parameters,
        ))
        return tool.invoke({"q": "love", "doctype": "json"})
