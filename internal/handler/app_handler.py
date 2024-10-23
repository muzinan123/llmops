#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Dict
from uuid import UUID

from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.documents import Document
from langchain_core.memory import BaseMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI

from internal.schema.app_schema import CompletionReq
from internal.service import AppService, VectorDatabaseService, ApiToolService
from internal.task.demo_task import demo_task
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    app_service: AppService
    vector_database_service: VectorDatabaseService
    api_tool_service: ApiToolService

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"xxxxx{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"xxxxx{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"xxxxx{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"xxxxx{app.id}")

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self, app_id: UUID):
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        system_prompt = "xxxxxxxx。\n\n<context>{context}</context>"
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("history"),
            ("human", "{query}"),
        ])
        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt"),
        )

        llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

        retriever = self.vector_database_service.get_retriever() | self.vector_database_service.combine_documents
        chain = (RunnablePassthrough.assign(
            history=RunnableLambda(self._load_memory_variables) | itemgetter("history"),
            context=itemgetter("query") | retriever
        ) | prompt | llm | StrOutputParser()).with_listeners(on_end=self._save_context)

        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input, config={"configurable": {"memory": memory}})

        return success_json({"content": content})

    @classmethod
    def _combine_documents(cls, documents: list[Document]) -> str:
        return "\n\n".join([document.page_content for document in documents])

    def ping(self):
        demo_task.delay(uuid.uuid4())
        return self.api_tool_service.api_tool_invoke()
