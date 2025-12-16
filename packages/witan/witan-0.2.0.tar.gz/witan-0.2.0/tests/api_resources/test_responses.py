# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from witan import Witan, AsyncWitan
from tests.utils import assert_matches_type
from witan.types import ResponseCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResponses:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Witan) -> None:
        response = client.responses.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Witan) -> None:
        response = client.responses.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
            include=["reasoning.encrypted_content"],
            model="witan-alfred",
            stream=True,
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Witan) -> None:
        http_response = client.responses.with_raw_response.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Witan) -> None:
        with client.responses.with_streaming_response.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseCreateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True


class TestAsyncResponses:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWitan) -> None:
        response = await async_client.responses.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWitan) -> None:
        response = await async_client.responses.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
            include=["reasoning.encrypted_content"],
            model="witan-alfred",
            stream=True,
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWitan) -> None:
        http_response = await async_client.responses.with_raw_response.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWitan) -> None:
        async with async_client.responses.with_streaming_response.create(
            input=[
                {
                    "content": [
                        {
                            "text": "x",
                            "type": "input_text",
                        }
                    ],
                    "role": "user",
                }
            ],
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseCreateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True
