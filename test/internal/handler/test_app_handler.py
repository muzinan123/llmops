#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from pkg.response import HttpCode


class TestAppHandler:

    @pytest.mark.parametrize(
        "app_id, query",
        [
            ("e0d13c78-870b-46df-b2f5-693ae9d5d727", None),
            ("e0d13c78-870b-46df-b2f5-693ae9d5d727", "xxxxx")
        ]
    )
    def test_completion(self, app_id, query, client):
        resp = client.post(f"/apps/{app_id}/debug", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
