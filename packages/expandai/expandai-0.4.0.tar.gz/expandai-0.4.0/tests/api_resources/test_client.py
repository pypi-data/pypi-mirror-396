# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from expandai import Expand, AsyncExpand
from tests.utils import assert_matches_type
from expandai.types import FetchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch(self, client: Expand) -> None:
        client_ = client.fetch(
            url="url",
        )
        assert_matches_type(FetchResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_with_all_params(self, client: Expand) -> None:
        client_ = client.fetch(
            url="url",
            browser_config={"scroll_full_page": True},
            select={
                "html": True,
                "markdown": True,
                "meta": True,
                "response": {"include_headers": True},
                "screenshot": True,
                "snippets": {
                    "query": "pricing plans",
                    "max_snippets": 5,
                    "min_score": 0.5,
                    "target_snippet_size": 384,
                },
                "summary": True,
            },
        )
        assert_matches_type(FetchResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_fetch(self, client: Expand) -> None:
        response = client.with_raw_response.fetch(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(FetchResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_fetch(self, client: Expand) -> None:
        with client.with_streaming_response.fetch(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(FetchResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch(self, async_client: AsyncExpand) -> None:
        client = await async_client.fetch(
            url="url",
        )
        assert_matches_type(FetchResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_with_all_params(self, async_client: AsyncExpand) -> None:
        client = await async_client.fetch(
            url="url",
            browser_config={"scroll_full_page": True},
            select={
                "html": True,
                "markdown": True,
                "meta": True,
                "response": {"include_headers": True},
                "screenshot": True,
                "snippets": {
                    "query": "pricing plans",
                    "max_snippets": 5,
                    "min_score": 0.5,
                    "target_snippet_size": 384,
                },
                "summary": True,
            },
        )
        assert_matches_type(FetchResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_fetch(self, async_client: AsyncExpand) -> None:
        response = await async_client.with_raw_response.fetch(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(FetchResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_fetch(self, async_client: AsyncExpand) -> None:
        async with async_client.with_streaming_response.fetch(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(FetchResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True
