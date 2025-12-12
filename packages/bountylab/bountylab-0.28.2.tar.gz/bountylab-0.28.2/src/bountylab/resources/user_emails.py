# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import user_email_best_email_params, user_email_reply_signal_params, user_email_best_email_by_login_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.user_email_best_email_response import UserEmailBestEmailResponse
from ..types.user_email_reply_signal_response import UserEmailReplySignalResponse
from ..types.user_email_best_email_by_login_response import UserEmailBestEmailByLoginResponse

__all__ = ["UserEmailsResource", "AsyncUserEmailsResource"]


class UserEmailsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserEmailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return UserEmailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserEmailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return UserEmailsResourceWithStreamingResponse(self)

    def best_email(
        self,
        *,
        github_ids: SequenceNotStr[str],
        signals: user_email_best_email_params.Signals | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailBestEmailResponse:
        """Fetch the best email address for GitHub users by their node IDs.

        Uses
        intelligent selection to prioritize personal emails over work emails and
        verifies domain validity. Returns the best email plus all other email
        candidates. Supports batch requests (1-100 IDs). Requires RAW service. Credits:
        1 per result returned.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          signals: Optional signal data for tracking email context (body, subject, sender)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/users/best-email",
            body=maybe_transform(
                {
                    "github_ids": github_ids,
                    "signals": signals,
                },
                user_email_best_email_params.UserEmailBestEmailParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailBestEmailResponse,
        )

    def best_email_by_login(
        self,
        *,
        logins: SequenceNotStr[str],
        signals: user_email_best_email_by_login_params.Signals | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailBestEmailByLoginResponse:
        """Fetch the best email address for GitHub users by their usernames (login).

        Uses
        intelligent selection to prioritize personal emails over work emails and
        verifies domain validity. Returns the best email plus all other email
        candidates. Supports batch requests (1-100 logins). Requires RAW service.
        Credits: 1 per result returned.

        Args:
          logins: Array of GitHub usernames (1-100)

          signals: Optional signal data for tracking email context (body, subject, sender)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/users/best-email/by-login",
            body=maybe_transform(
                {
                    "logins": logins,
                    "signals": signals,
                },
                user_email_best_email_by_login_params.UserEmailBestEmailByLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailBestEmailByLoginResponse,
        )

    def reply_signal(
        self,
        *,
        github_ids: SequenceNotStr[str],
        email_reply_body: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailReplySignalResponse:
        """Track when users reply to emails.

        This endpoint logs reply signals for analytics
        purposes. Does not consume credits. Requires RAW service.

        Args:
          github_ids: Array of GitHub node IDs for users who replied (1-100)

          email_reply_body: The body content of the user's reply email

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/users/best-email/signal/reply",
            body=maybe_transform(
                {
                    "github_ids": github_ids,
                    "email_reply_body": email_reply_body,
                },
                user_email_reply_signal_params.UserEmailReplySignalParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailReplySignalResponse,
        )


class AsyncUserEmailsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserEmailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncUserEmailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserEmailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return AsyncUserEmailsResourceWithStreamingResponse(self)

    async def best_email(
        self,
        *,
        github_ids: SequenceNotStr[str],
        signals: user_email_best_email_params.Signals | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailBestEmailResponse:
        """Fetch the best email address for GitHub users by their node IDs.

        Uses
        intelligent selection to prioritize personal emails over work emails and
        verifies domain validity. Returns the best email plus all other email
        candidates. Supports batch requests (1-100 IDs). Requires RAW service. Credits:
        1 per result returned.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          signals: Optional signal data for tracking email context (body, subject, sender)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/users/best-email",
            body=await async_maybe_transform(
                {
                    "github_ids": github_ids,
                    "signals": signals,
                },
                user_email_best_email_params.UserEmailBestEmailParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailBestEmailResponse,
        )

    async def best_email_by_login(
        self,
        *,
        logins: SequenceNotStr[str],
        signals: user_email_best_email_by_login_params.Signals | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailBestEmailByLoginResponse:
        """Fetch the best email address for GitHub users by their usernames (login).

        Uses
        intelligent selection to prioritize personal emails over work emails and
        verifies domain validity. Returns the best email plus all other email
        candidates. Supports batch requests (1-100 logins). Requires RAW service.
        Credits: 1 per result returned.

        Args:
          logins: Array of GitHub usernames (1-100)

          signals: Optional signal data for tracking email context (body, subject, sender)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/users/best-email/by-login",
            body=await async_maybe_transform(
                {
                    "logins": logins,
                    "signals": signals,
                },
                user_email_best_email_by_login_params.UserEmailBestEmailByLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailBestEmailByLoginResponse,
        )

    async def reply_signal(
        self,
        *,
        github_ids: SequenceNotStr[str],
        email_reply_body: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserEmailReplySignalResponse:
        """Track when users reply to emails.

        This endpoint logs reply signals for analytics
        purposes. Does not consume credits. Requires RAW service.

        Args:
          github_ids: Array of GitHub node IDs for users who replied (1-100)

          email_reply_body: The body content of the user's reply email

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/users/best-email/signal/reply",
            body=await async_maybe_transform(
                {
                    "github_ids": github_ids,
                    "email_reply_body": email_reply_body,
                },
                user_email_reply_signal_params.UserEmailReplySignalParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserEmailReplySignalResponse,
        )


class UserEmailsResourceWithRawResponse:
    def __init__(self, user_emails: UserEmailsResource) -> None:
        self._user_emails = user_emails

        self.best_email = to_raw_response_wrapper(
            user_emails.best_email,
        )
        self.best_email_by_login = to_raw_response_wrapper(
            user_emails.best_email_by_login,
        )
        self.reply_signal = to_raw_response_wrapper(
            user_emails.reply_signal,
        )


class AsyncUserEmailsResourceWithRawResponse:
    def __init__(self, user_emails: AsyncUserEmailsResource) -> None:
        self._user_emails = user_emails

        self.best_email = async_to_raw_response_wrapper(
            user_emails.best_email,
        )
        self.best_email_by_login = async_to_raw_response_wrapper(
            user_emails.best_email_by_login,
        )
        self.reply_signal = async_to_raw_response_wrapper(
            user_emails.reply_signal,
        )


class UserEmailsResourceWithStreamingResponse:
    def __init__(self, user_emails: UserEmailsResource) -> None:
        self._user_emails = user_emails

        self.best_email = to_streamed_response_wrapper(
            user_emails.best_email,
        )
        self.best_email_by_login = to_streamed_response_wrapper(
            user_emails.best_email_by_login,
        )
        self.reply_signal = to_streamed_response_wrapper(
            user_emails.reply_signal,
        )


class AsyncUserEmailsResourceWithStreamingResponse:
    def __init__(self, user_emails: AsyncUserEmailsResource) -> None:
        self._user_emails = user_emails

        self.best_email = async_to_streamed_response_wrapper(
            user_emails.best_email,
        )
        self.best_email_by_login = async_to_streamed_response_wrapper(
            user_emails.best_email_by_login,
        )
        self.reply_signal = async_to_streamed_response_wrapper(
            user_emails.reply_signal,
        )
