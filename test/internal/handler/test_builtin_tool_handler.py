#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from pkg.response import HttpCode


class TestBuiltinToolHandler:

    def test_get_categories(self, client):
        resp = client.get("/builtin-tools/categories")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    def test_get_builtin_tools(self, client):
        resp = client.get("/builtin-tools")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    @pytest.mark.parametrize(
        "provider_name, tool_name",
        [
            ("google", "google_serper"),
        ]
    )
    def test_get_provider_tool(self, provider_name, tool_name, client):
        resp = client.get(f"/builtin-tools/{provider_name}/tools/{tool_name}")
        assert resp.status_code == 200
        if provider_name == "google":
            assert resp.json.get("code") == HttpCode.SUCCESS
            assert resp.json.get("data").get("name") == tool_name
        elif provider_name == "xxx":
            assert resp.json.get("code") == HttpCode.NOT_FOUND

    @pytest.mark.parametrize("provider_name", ["google",])
    def test_get_provider_icon(self, provider_name, client):
        resp = client.get(f"/builtin-tools/{provider_name}/icon")
        assert resp.status_code == 200
        if provider_name == "xxxxx":
            assert resp.json.get("code") == HttpCode.NOT_FOUND
