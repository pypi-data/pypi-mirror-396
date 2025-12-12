# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bountylab import Bountylab, AsyncBountylab
from tests.utils import assert_matches_type
from bountylab.types import (
    RawUserGraphResponse,
    RawUserByLoginResponse,
    RawUserRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRawUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Bountylab) -> None:
        raw_user = client.raw_users.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Bountylab) -> None:
        raw_user = client.raw_users.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Bountylab) -> None:
        response = client.raw_users.with_raw_response.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = response.parse()
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Bountylab) -> None:
        with client.raw_users.with_streaming_response.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = response.parse()
            assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_by_login(self, client: Bountylab) -> None:
        raw_user = client.raw_users.by_login(
            logins=["octocat", "torvalds"],
        )
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_by_login_with_all_params(self, client: Bountylab) -> None:
        raw_user = client.raw_users.by_login(
            logins=["octocat", "torvalds"],
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_by_login(self, client: Bountylab) -> None:
        response = client.raw_users.with_raw_response.by_login(
            logins=["octocat", "torvalds"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = response.parse()
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_by_login(self, client: Bountylab) -> None:
        with client.raw_users.with_streaming_response.by_login(
            logins=["octocat", "torvalds"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = response.parse()
            assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_graph(self, client: Bountylab) -> None:
        raw_user = client.raw_users.graph(
            relationship="followers",
            id="id",
        )
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_graph_with_all_params(self, client: Bountylab) -> None:
        raw_user = client.raw_users.graph(
            relationship="followers",
            id="id",
            after="eyJvZmZzZXQiOjEwMH0=",
            first=100,
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "contributors": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owner": True,
                "owner_devrank": True,
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "starrers": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_graph(self, client: Bountylab) -> None:
        response = client.raw_users.with_raw_response.graph(
            relationship="followers",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = response.parse()
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_graph(self, client: Bountylab) -> None:
        with client.raw_users.with_streaming_response.graph(
            relationship="followers",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = response.parse()
            assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_graph(self, client: Bountylab) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.raw_users.with_raw_response.graph(
                relationship="followers",
                id="",
            )


class TestAsyncRawUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBountylab) -> None:
        response = await async_client.raw_users.with_raw_response.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = await response.parse()
        assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBountylab) -> None:
        async with async_client.raw_users.with_streaming_response.retrieve(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = await response.parse()
            assert_matches_type(RawUserRetrieveResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_by_login(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.by_login(
            logins=["octocat", "torvalds"],
        )
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_by_login_with_all_params(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.by_login(
            logins=["octocat", "torvalds"],
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 10,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_by_login(self, async_client: AsyncBountylab) -> None:
        response = await async_client.raw_users.with_raw_response.by_login(
            logins=["octocat", "torvalds"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = await response.parse()
        assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_by_login(self, async_client: AsyncBountylab) -> None:
        async with async_client.raw_users.with_streaming_response.by_login(
            logins=["octocat", "torvalds"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = await response.parse()
            assert_matches_type(RawUserByLoginResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_graph(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.graph(
            relationship="followers",
            id="id",
        )
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_graph_with_all_params(self, async_client: AsyncBountylab) -> None:
        raw_user = await async_client.raw_users.graph(
            relationship="followers",
            id="id",
            after="eyJvZmZzZXQiOjEwMH0=",
            first=100,
            include_attributes={
                "contributes": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "contributors": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "devrank": True,
                "followers": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "following": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "owner": True,
                "owner_devrank": True,
                "owns": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "starrers": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
                "stars": {
                    "first": 1,
                    "after": "after",
                    "filters": {
                        "field": "resolvedCountry",
                        "op": "Eq",
                        "value": "string",
                    },
                },
            },
        )
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_graph(self, async_client: AsyncBountylab) -> None:
        response = await async_client.raw_users.with_raw_response.graph(
            relationship="followers",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        raw_user = await response.parse()
        assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_graph(self, async_client: AsyncBountylab) -> None:
        async with async_client.raw_users.with_streaming_response.graph(
            relationship="followers",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            raw_user = await response.parse()
            assert_matches_type(RawUserGraphResponse, raw_user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_graph(self, async_client: AsyncBountylab) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.raw_users.with_raw_response.graph(
                relationship="followers",
                id="",
            )
