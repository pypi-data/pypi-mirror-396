# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast
from typing_extensions import Literal

import httpx

from ..types import raw_repo_graph_params, raw_repo_retrieve_params, raw_repo_by_fullname_params
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
from ..types.raw_repo_graph_response import RawRepoGraphResponse
from ..types.raw_repo_retrieve_response import RawRepoRetrieveResponse
from ..types.raw_repo_by_fullname_response import RawRepoByFullnameResponse

__all__ = ["RawReposResource", "AsyncRawReposResource"]


class RawReposResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RawReposResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return RawReposResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RawReposResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return RawReposResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        github_ids: SequenceNotStr[str],
        include_attributes: raw_repo_retrieve_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoRetrieveResponse:
        """Fetch GitHub repositories by their node IDs.

        Supports batch requests (1-100
        IDs). Requires RAW service. Credits: 1 per result returned + graph relationship
        credits if includeAttributes is specified.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          include_attributes: Optional graph relationships to include (owner, contributors, starrers)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/raw/repos",
            body=maybe_transform(
                {
                    "github_ids": github_ids,
                    "include_attributes": include_attributes,
                },
                raw_repo_retrieve_params.RawRepoRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawRepoRetrieveResponse,
        )

    def by_fullname(
        self,
        *,
        full_names: SequenceNotStr[str],
        include_attributes: raw_repo_by_fullname_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoByFullnameResponse:
        """Fetch GitHub repositories by their full names (owner/repo format).

        Supports
        batch requests (1-100 repos). Requires RAW service. Credits: 1 per result
        returned.

        Args:
          full_names: Array of repository full names in "owner/name" format (1-100)

          include_attributes: Optional graph relationships to include (owner, contributors, starrers)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/raw/repos/by-fullname",
            body=maybe_transform(
                {
                    "full_names": full_names,
                    "include_attributes": include_attributes,
                },
                raw_repo_by_fullname_params.RawRepoByFullnameParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawRepoByFullnameResponse,
        )

    def graph(
        self,
        relationship: Literal["stars", "contributes", "owns"],
        *,
        id: str,
        after: str | Omit = omit,
        first: float | Omit = omit,
        include_attributes: raw_repo_graph_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoGraphResponse:
        """Get graph relationships for a repository (stars, contributes, owns).

        Supports
        pagination and includeAttributes. Requires RAW service. Credits: 1 per result +
        graph relationship credits if includeAttributes is specified.

        Args:
          id: GitHub node ID or BountyLab ID of the repository

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
            RawRepoGraphResponse,
            self._post(
                f"/api/raw/repos/{id}/graph/{relationship}",
                body=maybe_transform(
                    {
                        "after": after,
                        "first": first,
                        "include_attributes": include_attributes,
                    },
                    raw_repo_graph_params.RawRepoGraphParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, RawRepoGraphResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncRawReposResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRawReposResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncRawReposResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRawReposResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bountylaboratories/python-sdk#with_streaming_response
        """
        return AsyncRawReposResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        github_ids: SequenceNotStr[str],
        include_attributes: raw_repo_retrieve_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoRetrieveResponse:
        """Fetch GitHub repositories by their node IDs.

        Supports batch requests (1-100
        IDs). Requires RAW service. Credits: 1 per result returned + graph relationship
        credits if includeAttributes is specified.

        Args:
          github_ids: Array of GitHub node IDs (1-100)

          include_attributes: Optional graph relationships to include (owner, contributors, starrers)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/raw/repos",
            body=await async_maybe_transform(
                {
                    "github_ids": github_ids,
                    "include_attributes": include_attributes,
                },
                raw_repo_retrieve_params.RawRepoRetrieveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawRepoRetrieveResponse,
        )

    async def by_fullname(
        self,
        *,
        full_names: SequenceNotStr[str],
        include_attributes: raw_repo_by_fullname_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoByFullnameResponse:
        """Fetch GitHub repositories by their full names (owner/repo format).

        Supports
        batch requests (1-100 repos). Requires RAW service. Credits: 1 per result
        returned.

        Args:
          full_names: Array of repository full names in "owner/name" format (1-100)

          include_attributes: Optional graph relationships to include (owner, contributors, starrers)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/raw/repos/by-fullname",
            body=await async_maybe_transform(
                {
                    "full_names": full_names,
                    "include_attributes": include_attributes,
                },
                raw_repo_by_fullname_params.RawRepoByFullnameParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RawRepoByFullnameResponse,
        )

    async def graph(
        self,
        relationship: Literal["stars", "contributes", "owns"],
        *,
        id: str,
        after: str | Omit = omit,
        first: float | Omit = omit,
        include_attributes: raw_repo_graph_params.IncludeAttributes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RawRepoGraphResponse:
        """Get graph relationships for a repository (stars, contributes, owns).

        Supports
        pagination and includeAttributes. Requires RAW service. Credits: 1 per result +
        graph relationship credits if includeAttributes is specified.

        Args:
          id: GitHub node ID or BountyLab ID of the repository

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
            RawRepoGraphResponse,
            await self._post(
                f"/api/raw/repos/{id}/graph/{relationship}",
                body=await async_maybe_transform(
                    {
                        "after": after,
                        "first": first,
                        "include_attributes": include_attributes,
                    },
                    raw_repo_graph_params.RawRepoGraphParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, RawRepoGraphResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class RawReposResourceWithRawResponse:
    def __init__(self, raw_repos: RawReposResource) -> None:
        self._raw_repos = raw_repos

        self.retrieve = to_raw_response_wrapper(
            raw_repos.retrieve,
        )
        self.by_fullname = to_raw_response_wrapper(
            raw_repos.by_fullname,
        )
        self.graph = to_raw_response_wrapper(
            raw_repos.graph,
        )


class AsyncRawReposResourceWithRawResponse:
    def __init__(self, raw_repos: AsyncRawReposResource) -> None:
        self._raw_repos = raw_repos

        self.retrieve = async_to_raw_response_wrapper(
            raw_repos.retrieve,
        )
        self.by_fullname = async_to_raw_response_wrapper(
            raw_repos.by_fullname,
        )
        self.graph = async_to_raw_response_wrapper(
            raw_repos.graph,
        )


class RawReposResourceWithStreamingResponse:
    def __init__(self, raw_repos: RawReposResource) -> None:
        self._raw_repos = raw_repos

        self.retrieve = to_streamed_response_wrapper(
            raw_repos.retrieve,
        )
        self.by_fullname = to_streamed_response_wrapper(
            raw_repos.by_fullname,
        )
        self.graph = to_streamed_response_wrapper(
            raw_repos.graph,
        )


class AsyncRawReposResourceWithStreamingResponse:
    def __init__(self, raw_repos: AsyncRawReposResource) -> None:
        self._raw_repos = raw_repos

        self.retrieve = async_to_streamed_response_wrapper(
            raw_repos.retrieve,
        )
        self.by_fullname = async_to_streamed_response_wrapper(
            raw_repos.by_fullname,
        )
        self.graph = async_to_streamed_response_wrapper(
            raw_repos.graph,
        )
