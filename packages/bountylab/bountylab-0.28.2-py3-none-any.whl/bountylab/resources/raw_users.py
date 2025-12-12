# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast
from typing_extensions import Literal

import httpx

from ..types import raw_user_graph_params, raw_user_by_login_params, raw_user_retrieve_params
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
from ..types.raw_user_graph_response import RawUserGraphResponse
from ..types.raw_user_by_login_response import RawUserByLoginResponse
from ..types.raw_user_retrieve_response import RawUserRetrieveResponse

__all__ = ["RawUsersResource", "AsyncRawUsersResource"]


class RawUsersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RawUsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return RawUsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RawUsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return RawUsersResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        github_ids: SequenceNotStr[str],
        include_attributes: raw_user_retrieve_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserRetrieveResponse:
        """Fetch GitHub users by their node IDs.

        Supports batch requests (1-100 IDs).
        Requires RAW service. Credits: 1 per result returned + graph relationship
        credits if includeAttributes is specified.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          include_attributes: Optional graph relationships to include (followers, following, stars, owns,
              contributes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/raw/users",
            body=maybe_transform(
                {
                    "github_ids": github_ids,
                    "include_attributes": include_attributes,
                },
                raw_user_retrieve_params.RawUserRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawUserRetrieveResponse,
        )

    def by_login(
        self,
        *,
        logins: SequenceNotStr[str],
        include_attributes: raw_user_by_login_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserByLoginResponse:
        """Fetch GitHub users by their usernames (login).

        Supports batch requests (1-100
        logins). Requires RAW service. Credits: 1 per result returned.

        Args:
          logins: Array of GitHub usernames (1-100)

          include_attributes: Optional graph relationships to include (followers, following, stars, owns,
              contributes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/raw/users/by-login",
            body=maybe_transform(
                {
                    "logins": logins,
                    "include_attributes": include_attributes,
                },
                raw_user_by_login_params.RawUserByLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawUserByLoginResponse,
        )

    def graph(
        self,
        relationship: Literal["followers", "following", "owns", "stars", "contributes"],
        *,
        id: str,
        after: str | Omit = omit,
        first: float | Omit = omit,
        include_attributes: raw_user_graph_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserGraphResponse:
        """
        Get graph relationships for a user (followers, following, owns, stars,
        contributes). Supports pagination and includeAttributes. Requires RAW service.
        Credits: 1 per result + graph relationship credits if includeAttributes is
        specified.

        Args:
          id: GitHub node ID or BountyLab ID of the user

          relationship: Graph relationship type

          after: Cursor for pagination (opaque base64-encoded string from previous response)

          first: Number of items to return (default: 100, max: 100)

          include_attributes: Optional graph relationships to include. Use user attributes (followers,
              following, owns, stars, contributes) for user-returning relationships, or repo
              attributes (owner, contributors, starrers) for repo-returning relationships.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not relationship:
            raise ValueError(f"Expected a non-empty value for `relationship` but received {relationship!r}")
        return cast(
            RawUserGraphResponse,
            self._post(
                f"/api/raw/users/{id}/graph/{relationship}",
                body=maybe_transform(
                    {
                        "after": after,
                        "first": first,
                        "include_attributes": include_attributes,
                    },
                    raw_user_graph_params.RawUserGraphParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, RawUserGraphResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncRawUsersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRawUsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncRawUsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRawUsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return AsyncRawUsersResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        github_ids: SequenceNotStr[str],
        include_attributes: raw_user_retrieve_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserRetrieveResponse:
        """Fetch GitHub users by their node IDs.

        Supports batch requests (1-100 IDs).
        Requires RAW service. Credits: 1 per result returned + graph relationship
        credits if includeAttributes is specified.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          include_attributes: Optional graph relationships to include (followers, following, stars, owns,
              contributes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/raw/users",
            body=await async_maybe_transform(
                {
                    "github_ids": github_ids,
                    "include_attributes": include_attributes,
                },
                raw_user_retrieve_params.RawUserRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawUserRetrieveResponse,
        )

    async def by_login(
        self,
        *,
        logins: SequenceNotStr[str],
        include_attributes: raw_user_by_login_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserByLoginResponse:
        """Fetch GitHub users by their usernames (login).

        Supports batch requests (1-100
        logins). Requires RAW service. Credits: 1 per result returned.

        Args:
          logins: Array of GitHub usernames (1-100)

          include_attributes: Optional graph relationships to include (followers, following, stars, owns,
              contributes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/raw/users/by-login",
            body=await async_maybe_transform(
                {
                    "logins": logins,
                    "include_attributes": include_attributes,
                },
                raw_user_by_login_params.RawUserByLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawUserByLoginResponse,
        )

    async def graph(
        self,
        relationship: Literal["followers", "following", "owns", "stars", "contributes"],
        *,
        id: str,
        after: str | Omit = omit,
        first: float | Omit = omit,
        include_attributes: raw_user_graph_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawUserGraphResponse:
        """
        Get graph relationships for a user (followers, following, owns, stars,
        contributes). Supports pagination and includeAttributes. Requires RAW service.
        Credits: 1 per result + graph relationship credits if includeAttributes is
        specified.

        Args:
          id: GitHub node ID or BountyLab ID of the user

          relationship: Graph relationship type

          after: Cursor for pagination (opaque base64-encoded string from previous response)

          first: Number of items to return (default: 100, max: 100)

          include_attributes: Optional graph relationships to include. Use user attributes (followers,
              following, owns, stars, contributes) for user-returning relationships, or repo
              attributes (owner, contributors, starrers) for repo-returning relationships.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not relationship:
            raise ValueError(f"Expected a non-empty value for `relationship` but received {relationship!r}")
        return cast(
            RawUserGraphResponse,
            await self._post(
                f"/api/raw/users/{id}/graph/{relationship}",
                body=await async_maybe_transform(
                    {
                        "after": after,
                        "first": first,
                        "include_attributes": include_attributes,
                    },
                    raw_user_graph_params.RawUserGraphParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, RawUserGraphResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class RawUsersResourceWithRawResponse:
    def __init__(self, raw_users: RawUsersResource) -> None:
        self._raw_users = raw_users

        self.retrieve = to_raw_response_wrapper(
            raw_users.retrieve,
        )
        self.by_login = to_raw_response_wrapper(
            raw_users.by_login,
        )
        self.graph = to_raw_response_wrapper(
            raw_users.graph,
        )


class AsyncRawUsersResourceWithRawResponse:
    def __init__(self, raw_users: AsyncRawUsersResource) -> None:
        self._raw_users = raw_users

        self.retrieve = async_to_raw_response_wrapper(
            raw_users.retrieve,
        )
        self.by_login = async_to_raw_response_wrapper(
            raw_users.by_login,
        )
        self.graph = async_to_raw_response_wrapper(
            raw_users.graph,
        )


class RawUsersResourceWithStreamingResponse:
    def __init__(self, raw_users: RawUsersResource) -> None:
        self._raw_users = raw_users

        self.retrieve = to_streamed_response_wrapper(
            raw_users.retrieve,
        )
        self.by_login = to_streamed_response_wrapper(
            raw_users.by_login,
        )
        self.graph = to_streamed_response_wrapper(
            raw_users.graph,
        )


class AsyncRawUsersResourceWithStreamingResponse:
    def __init__(self, raw_users: AsyncRawUsersResource) -> None:
        self._raw_users = raw_users

        self.retrieve = async_to_streamed_response_wrapper(
            raw_users.retrieve,
        )
        self.by_login = async_to_streamed_response_wrapper(
            raw_users.by_login,
        )
        self.graph = async_to_streamed_response_wrapper(
            raw_users.graph,
        )
