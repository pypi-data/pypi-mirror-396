# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import Any, Optional, cast

import httpx

from ..types import repo_get_params, repo_set_params, repo_list_params, repo_create_params, repo_get_tree_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.repo_response import RepoResponse
from ..types.repo_list_response import RepoListResponse
from ..types.repo_get_tree_response import RepoGetTreeResponse

__all__ = ["RepoResource", "AsyncRepoResource"]


class RepoResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return RepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return RepoResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        base_model: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """Creates a new repository.

        Idempotent: if repo exists with same base_model,
        returns existing (200). If exists with different base_model, returns 409
        Conflict.

        Args:
          repo_name: Name of the repository

          user_id: User ID override (requires master API key)

          base_model: Base model for the repository (optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._post(
            "/v1/repo",
            body=maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_create_params.RepoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, repo_create_params.RepoCreateParams),
            ),
            cast_to=RepoResponse,
        )

    def list(
        self,
        *,
        include_metadata: bool | Omit = omit,
        limit: Optional[int] | Omit = omit,
        offset: int | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """
        Returns repositories visible to the authenticated team.

            - Default: Returns simple list of repo names (backward compatible)
            - With metadata: Use ?include_metadata=true to get repos with base_model
            - Pagination: Use ?include_metadata=true&offset=0&limit=50 for paginated results

        Args:
          include_metadata: Include base_model metadata for each repo

          limit: Page size for pagination (only used with include_metadata=true)

          offset: Starting offset for pagination (only used with include_metadata=true)

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return cast(
            RepoListResponse,
            self._get(
                "/v1/repo",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {
                            "include_metadata": include_metadata,
                            "limit": limit,
                            "offset": offset,
                            "user_id": user_id,
                        },
                        repo_list_params.RepoListParams,
                    ),
                ),
                cast_to=cast(Any, RepoListResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def get(
        self,
        repo_name: str,
        *,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoResponse:
        """
        Returns repository configuration and metadata.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, repo_get_params.RepoGetParams),
            ),
            cast_to=RepoResponse,
        )

    def get_tree(
        self,
        repo_name: str,
        *,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoGetTreeResponse:
        """
        Get the complete model lineage tree for a repository.

            Returns all bakes in the repository with their parent-child relationships,
            status, checkpoints, and full model paths. This provides a complete view of
            model evolution without requiring a specific starting bake.

            Unlike dependency-graph which starts from a specific bake, this endpoint
            returns the entire repository's model lineage tree in a single call.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}/tree",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, repo_get_tree_params.RepoGetTreeParams),
            ),
            cast_to=RepoGetTreeResponse,
        )

    @typing_extensions.deprecated("deprecated")
    def set(
        self,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        base_model: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """[DEPRECATED] Use POST /v1/repo instead.

        Creates the repository if missing or
        returns the existing one. Idempotent; base_model cannot be changed (409 on
        conflict). This endpoint will be removed in a future version.

        Args:
          repo_name: Name of the repository

          user_id: User ID override (requires master API key)

          base_model: Base model for the repository (optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._put(
            "/v1/repo",
            body=maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_set_params.RepoSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, repo_set_params.RepoSetParams),
            ),
            cast_to=RepoResponse,
        )


class AsyncRepoResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncRepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncRepoResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        base_model: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """Creates a new repository.

        Idempotent: if repo exists with same base_model,
        returns existing (200). If exists with different base_model, returns 409
        Conflict.

        Args:
          repo_name: Name of the repository

          user_id: User ID override (requires master API key)

          base_model: Base model for the repository (optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._post(
            "/v1/repo",
            body=await async_maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_create_params.RepoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, repo_create_params.RepoCreateParams),
            ),
            cast_to=RepoResponse,
        )

    async def list(
        self,
        *,
        include_metadata: bool | Omit = omit,
        limit: Optional[int] | Omit = omit,
        offset: int | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """
        Returns repositories visible to the authenticated team.

            - Default: Returns simple list of repo names (backward compatible)
            - With metadata: Use ?include_metadata=true to get repos with base_model
            - Pagination: Use ?include_metadata=true&offset=0&limit=50 for paginated results

        Args:
          include_metadata: Include base_model metadata for each repo

          limit: Page size for pagination (only used with include_metadata=true)

          offset: Starting offset for pagination (only used with include_metadata=true)

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return cast(
            RepoListResponse,
            await self._get(
                "/v1/repo",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {
                            "include_metadata": include_metadata,
                            "limit": limit,
                            "offset": offset,
                            "user_id": user_id,
                        },
                        repo_list_params.RepoListParams,
                    ),
                ),
                cast_to=cast(Any, RepoListResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def get(
        self,
        repo_name: str,
        *,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoResponse:
        """
        Returns repository configuration and metadata.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, repo_get_params.RepoGetParams),
            ),
            cast_to=RepoResponse,
        )

    async def get_tree(
        self,
        repo_name: str,
        *,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoGetTreeResponse:
        """
        Get the complete model lineage tree for a repository.

            Returns all bakes in the repository with their parent-child relationships,
            status, checkpoints, and full model paths. This provides a complete view of
            model evolution without requiring a specific starting bake.

            Unlike dependency-graph which starts from a specific bake, this endpoint
            returns the entire repository's model lineage tree in a single call.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}/tree",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, repo_get_tree_params.RepoGetTreeParams),
            ),
            cast_to=RepoGetTreeResponse,
        )

    @typing_extensions.deprecated("deprecated")
    async def set(
        self,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        base_model: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """[DEPRECATED] Use POST /v1/repo instead.

        Creates the repository if missing or
        returns the existing one. Idempotent; base_model cannot be changed (409 on
        conflict). This endpoint will be removed in a future version.

        Args:
          repo_name: Name of the repository

          user_id: User ID override (requires master API key)

          base_model: Base model for the repository (optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._put(
            "/v1/repo",
            body=await async_maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_set_params.RepoSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, repo_set_params.RepoSetParams),
            ),
            cast_to=RepoResponse,
        )


class RepoResourceWithRawResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.create = to_raw_response_wrapper(
            repo.create,
        )
        self.list = to_raw_response_wrapper(
            repo.list,
        )
        self.get = to_raw_response_wrapper(
            repo.get,
        )
        self.get_tree = to_raw_response_wrapper(
            repo.get_tree,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                repo.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncRepoResourceWithRawResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.create = async_to_raw_response_wrapper(
            repo.create,
        )
        self.list = async_to_raw_response_wrapper(
            repo.list,
        )
        self.get = async_to_raw_response_wrapper(
            repo.get,
        )
        self.get_tree = async_to_raw_response_wrapper(
            repo.get_tree,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                repo.set,  # pyright: ignore[reportDeprecated],
            )
        )


class RepoResourceWithStreamingResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.create = to_streamed_response_wrapper(
            repo.create,
        )
        self.list = to_streamed_response_wrapper(
            repo.list,
        )
        self.get = to_streamed_response_wrapper(
            repo.get,
        )
        self.get_tree = to_streamed_response_wrapper(
            repo.get_tree,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                repo.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncRepoResourceWithStreamingResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.create = async_to_streamed_response_wrapper(
            repo.create,
        )
        self.list = async_to_streamed_response_wrapper(
            repo.list,
        )
        self.get = async_to_streamed_response_wrapper(
            repo.get,
        )
        self.get_tree = async_to_streamed_response_wrapper(
            repo.get_tree,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                repo.set,  # pyright: ignore[reportDeprecated],
            )
        )
