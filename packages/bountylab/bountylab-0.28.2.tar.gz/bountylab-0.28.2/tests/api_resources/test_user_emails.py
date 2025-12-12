# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bountylab import Bountylab, AsyncBountylab
from tests.utils import assert_matches_type
from bountylab.types import (
    UserEmailBestEmailResponse,
    UserEmailReplySignalResponse,
    UserEmailBestEmailByLoginResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserEmails:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_best_email(self, client: Bountylab) -> None:
        user_email = client.user_emails.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_best_email_with_all_params(self, client: Bountylab) -> None:
        user_email = client.user_emails.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
            signals={
                "email_body": "emailBody",
                "email_subject": "emailSubject",
                "reason_for_email_natural_language": "reasonForEmailNaturalLanguage",
                "repo_reason_for_email": "repoReasonForEmail",
                "sender": "sender",
            },
        )
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_best_email(self, client: Bountylab) -> None:
        response = client.user_emails.with_raw_response.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = response.parse()
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_best_email(self, client: Bountylab) -> None:
        with client.user_emails.with_streaming_response.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = response.parse()
            assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_best_email_by_login(self, client: Bountylab) -> None:
        user_email = client.user_emails.best_email_by_login(
            logins=["octocat", "torvalds"],
        )
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_best_email_by_login_with_all_params(self, client: Bountylab) -> None:
        user_email = client.user_emails.best_email_by_login(
            logins=["octocat", "torvalds"],
            signals={
                "email_body": "emailBody",
                "email_subject": "emailSubject",
                "reason_for_email_natural_language": "reasonForEmailNaturalLanguage",
                "repo_reason_for_email": "repoReasonForEmail",
                "sender": "sender",
            },
        )
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_best_email_by_login(self, client: Bountylab) -> None:
        response = client.user_emails.with_raw_response.best_email_by_login(
            logins=["octocat", "torvalds"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = response.parse()
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_best_email_by_login(self, client: Bountylab) -> None:
        with client.user_emails.with_streaming_response.best_email_by_login(
            logins=["octocat", "torvalds"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = response.parse()
            assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reply_signal(self, client: Bountylab) -> None:
        user_email = client.user_emails.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        )
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reply_signal_with_all_params(self, client: Bountylab) -> None:
        user_email = client.user_emails.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
            email_reply_body="emailReplyBody",
        )
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reply_signal(self, client: Bountylab) -> None:
        response = client.user_emails.with_raw_response.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = response.parse()
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reply_signal(self, client: Bountylab) -> None:
        with client.user_emails.with_streaming_response.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = response.parse()
            assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUserEmails:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_best_email(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_best_email_with_all_params(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
            signals={
                "email_body": "emailBody",
                "email_subject": "emailSubject",
                "reason_for_email_natural_language": "reasonForEmailNaturalLanguage",
                "repo_reason_for_email": "repoReasonForEmail",
                "sender": "sender",
            },
        )
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_best_email(self, async_client: AsyncBountylab) -> None:
        response = await async_client.user_emails.with_raw_response.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = await response.parse()
        assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_best_email(self, async_client: AsyncBountylab) -> None:
        async with async_client.user_emails.with_streaming_response.best_email(
            github_ids=["MDQ6VXNlcjU4MzIzMQ==", "MDQ6VXNlcjE="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = await response.parse()
            assert_matches_type(UserEmailBestEmailResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_best_email_by_login(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.best_email_by_login(
            logins=["octocat", "torvalds"],
        )
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_best_email_by_login_with_all_params(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.best_email_by_login(
            logins=["octocat", "torvalds"],
            signals={
                "email_body": "emailBody",
                "email_subject": "emailSubject",
                "reason_for_email_natural_language": "reasonForEmailNaturalLanguage",
                "repo_reason_for_email": "repoReasonForEmail",
                "sender": "sender",
            },
        )
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_best_email_by_login(self, async_client: AsyncBountylab) -> None:
        response = await async_client.user_emails.with_raw_response.best_email_by_login(
            logins=["octocat", "torvalds"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = await response.parse()
        assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_best_email_by_login(self, async_client: AsyncBountylab) -> None:
        async with async_client.user_emails.with_streaming_response.best_email_by_login(
            logins=["octocat", "torvalds"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = await response.parse()
            assert_matches_type(UserEmailBestEmailByLoginResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reply_signal(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        )
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reply_signal_with_all_params(self, async_client: AsyncBountylab) -> None:
        user_email = await async_client.user_emails.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
            email_reply_body="emailReplyBody",
        )
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reply_signal(self, async_client: AsyncBountylab) -> None:
        response = await async_client.user_emails.with_raw_response.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_email = await response.parse()
        assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reply_signal(self, async_client: AsyncBountylab) -> None:
        async with async_client.user_emails.with_streaming_response.reply_signal(
            github_ids=["MDQ6VXNlcjU4MzIzMQ=="],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_email = await response.parse()
            assert_matches_type(UserEmailReplySignalResponse, user_email, path=["response"])

        assert cast(Any, response.is_closed) is True
