# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import logging
import typing_extensions
from typing import Iterable, Optional

import httpx

from ..types import (
    bake_get_params,
    bake_run_params,
    bake_set_params,
    bake_list_params,
    bake_create_params,
    bake_delete_params,
    bake_download_params,
    bake_batch_set_params,
    bake_get_metrics_params,
    bake_create_batch_params,
)
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
from ..types.bake_response import BakeResponse
from ..types.delete_response import DeleteResponse
from ..types.bake_list_response import BakeListResponse
from ..types.bake_config_base_param import BakeConfigBaseParam
from ..types.bake_download_response import BakeDownloadResponse
from ..types.bake_batch_set_response import BakeBatchSetResponse
from ..types.bake_get_metrics_response import BakeGetMetricsResponse
from ..types.bake_create_batch_response import BakeCreateBatchResponse

__all__ = ["BakesResource", "AsyncBakesResource"]

log = logging.getLogger(__name__)


class BakesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BakesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return BakesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BakesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return BakesResourceWithStreamingResponse(self)

    def create(
        self,
        repo_name: str,
        *,
        bake_name: str,
        template: str,
        user_id: Optional[str] | Omit = omit,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """Creates a new bake.

        Idempotent: if bake exists with same config, returns
        existing (200). If exists with different config, returns 409 Conflict.

        Args:
          bake_name: Name of the bake

          template: Template: 'default' or existing bake name

          user_id: User ID override (requires master API key)

          overrides: Base bake configuration fields (for responses - all optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._post(
            f"/v1/repo/{repo_name}/bakes",
            body=maybe_transform(
                {
                    "bake_name": bake_name,
                    "template": template,
                    "overrides": overrides,
                },
                bake_create_params.BakeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_create_params.BakeCreateParams),
            ),
            cast_to=BakeResponse,
        )

    def list(
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
    ) -> BakeListResponse:
        """
        Lists bakes in the repository for discovery and validation.

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
            f"/v1/repo/{repo_name}/bakes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, bake_list_params.BakeListParams),
            ),
            cast_to=BakeListResponse,
        )

    def delete(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> DeleteResponse:
        """
        Deletes a bake from the repository.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._delete(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_delete_params.BakeDeleteParams),
            ),
            cast_to=DeleteResponse,
        )

    @typing_extensions.deprecated("deprecated")
    def batch_set(
        self,
        repo_name: str,
        *,
        bakes: Iterable[bake_batch_set_params.Bake],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeBatchSetResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/bakes/batch instead.

        Create or update
        multiple bakes (idempotent).

        Args:
          bakes: List of bakes to create/update

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._put(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=maybe_transform({"bakes": bakes}, bake_batch_set_params.BakeBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_batch_set_params.BakeBatchSetParams),
            ),
            cast_to=BakeBatchSetResponse,
        )

    def create_batch(
        self,
        repo_name: str,
        *,
        bakes: Iterable[bake_create_batch_params.Bake],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeCreateBatchResponse:
        """Creates multiple bakes.

        Idempotent: if bake exists with same config, returns
        existing. If exists with different config, returns 409 Conflict.

        Args:
          bakes: List of bakes to create/update

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._post(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=maybe_transform({"bakes": bakes}, bake_create_batch_params.BakeCreateBatchParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_create_batch_params.BakeCreateBatchParams),
            ),
            cast_to=BakeCreateBatchResponse,
        )

    def download(
        self,
        bake_name: str,
        *,
        repo_name: str,
        checkpoint: Optional[int] | Omit = omit,
        expires_in: Optional[int] | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeDownloadResponse:
        """
        Get presigned URL for downloading model weights.

            Downloads the latest checkpoint by default, or specify checkpoint number via query parameter.
            Returns a presigned URL valid for 1 hour (configurable via R2_PRESIGNED_URL_EXPIRY).

        Args:
          checkpoint: Checkpoint number (defaults to latest)

          expires_in: URL expiry in seconds (1-604800, default 3600)

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "checkpoint": checkpoint,
                        "expires_in": expires_in,
                        "user_id": user_id,
                    },
                    bake_download_params.BakeDownloadParams,
                ),
            ),
            cast_to=BakeDownloadResponse,
        )

    def get(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeResponse:
        """
        Get bake definition and metadata.

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
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, bake_get_params.BakeGetParams),
            ),
            cast_to=BakeResponse,
        )

    def get_metrics(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeGetMetricsResponse:
        """
        Get training metrics for a bake.

            Returns all metrics from train_log_metrics.jsonl as a JSON array.
            Each entry contains metrics like iter, loss, train_loss, lr, etc.
            Useful for plotting loss curves and other training metrics on the frontend.

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
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, bake_get_metrics_params.BakeGetMetricsParams),
            ),
            cast_to=BakeGetMetricsResponse,
        )

    def run(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        poll: bool = True,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """
        Queue a bake (model training) job for the specified bake.

        Prereqs: bake config is complete (datasets + training settings); all referenced
        targets have completed rollouts; sufficient credit balance. Idempotent: repeated
        calls while a job exists return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET bake to monitor (status/job) and access
        artifacts after completion.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)
          poll: Poll for the bake job status until it is complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        response = self._post(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_run_params.BakeRunParams),
            ),
            cast_to=BakeResponse,
        )
    
        if poll:
            while response.status in ("not_started", "preparing", "pending", "running", "incomplete"):
                log.info("Status: %s, Percentage: %s", response.status, response.progress_percent)
                self._sleep(30.0)
                response = self.get(bake_name, repo_name=repo_name)
            
            if response.status == "complete":
                log.info("Bake job completed")
            elif response.status == "failed":
                log.warning("Bake job failed")

        return response

    @typing_extensions.deprecated("deprecated")
    def set(
        self,
        bake_name: str,
        *,
        repo_name: str,
        template: str,
        user_id: Optional[str] | Omit = omit,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/bakes instead.

        Create or update a
        bake (idempotent). This endpoint will be removed in a future version.

        Args:
          template: Template: 'default' or existing bake name

          user_id: User ID override (requires master API key)

          overrides: Base bake configuration fields (for responses - all optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._put(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            body=maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                bake_set_params.BakeSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, bake_set_params.BakeSetParams),
            ),
            cast_to=BakeResponse,
        )


class AsyncBakesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBakesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncBakesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBakesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncBakesResourceWithStreamingResponse(self)

    async def create(
        self,
        repo_name: str,
        *,
        bake_name: str,
        template: str,
        user_id: Optional[str] | Omit = omit,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """Creates a new bake.

        Idempotent: if bake exists with same config, returns
        existing (200). If exists with different config, returns 409 Conflict.

        Args:
          bake_name: Name of the bake

          template: Template: 'default' or existing bake name

          user_id: User ID override (requires master API key)

          overrides: Base bake configuration fields (for responses - all optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._post(
            f"/v1/repo/{repo_name}/bakes",
            body=await async_maybe_transform(
                {
                    "bake_name": bake_name,
                    "template": template,
                    "overrides": overrides,
                },
                bake_create_params.BakeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_create_params.BakeCreateParams),
            ),
            cast_to=BakeResponse,
        )

    async def list(
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
    ) -> BakeListResponse:
        """
        Lists bakes in the repository for discovery and validation.

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
            f"/v1/repo/{repo_name}/bakes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, bake_list_params.BakeListParams),
            ),
            cast_to=BakeListResponse,
        )

    async def delete(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> DeleteResponse:
        """
        Deletes a bake from the repository.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._delete(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_delete_params.BakeDeleteParams),
            ),
            cast_to=DeleteResponse,
        )

    @typing_extensions.deprecated("deprecated")
    async def batch_set(
        self,
        repo_name: str,
        *,
        bakes: Iterable[bake_batch_set_params.Bake],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeBatchSetResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/bakes/batch instead.

        Create or update
        multiple bakes (idempotent).

        Args:
          bakes: List of bakes to create/update

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._put(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=await async_maybe_transform({"bakes": bakes}, bake_batch_set_params.BakeBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_batch_set_params.BakeBatchSetParams),
            ),
            cast_to=BakeBatchSetResponse,
        )

    async def create_batch(
        self,
        repo_name: str,
        *,
        bakes: Iterable[bake_create_batch_params.Bake],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeCreateBatchResponse:
        """Creates multiple bakes.

        Idempotent: if bake exists with same config, returns
        existing. If exists with different config, returns 409 Conflict.

        Args:
          bakes: List of bakes to create/update

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._post(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=await async_maybe_transform({"bakes": bakes}, bake_create_batch_params.BakeCreateBatchParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_create_batch_params.BakeCreateBatchParams),
            ),
            cast_to=BakeCreateBatchResponse,
        )

    async def download(
        self,
        bake_name: str,
        *,
        repo_name: str,
        checkpoint: Optional[int] | Omit = omit,
        expires_in: Optional[int] | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeDownloadResponse:
        """
        Get presigned URL for downloading model weights.

            Downloads the latest checkpoint by default, or specify checkpoint number via query parameter.
            Returns a presigned URL valid for 1 hour (configurable via R2_PRESIGNED_URL_EXPIRY).

        Args:
          checkpoint: Checkpoint number (defaults to latest)

          expires_in: URL expiry in seconds (1-604800, default 3600)

          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "checkpoint": checkpoint,
                        "expires_in": expires_in,
                        "user_id": user_id,
                    },
                    bake_download_params.BakeDownloadParams,
                ),
            ),
            cast_to=BakeDownloadResponse,
        )

    async def get(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeResponse:
        """
        Get bake definition and metadata.

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
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, bake_get_params.BakeGetParams),
            ),
            cast_to=BakeResponse,
        )

    async def get_metrics(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeGetMetricsResponse:
        """
        Get training metrics for a bake.

            Returns all metrics from train_log_metrics.jsonl as a JSON array.
            Each entry contains metrics like iter, loss, train_loss, lr, etc.
            Useful for plotting loss curves and other training metrics on the frontend.

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
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, bake_get_metrics_params.BakeGetMetricsParams),
            ),
            cast_to=BakeGetMetricsResponse,
        )

    async def run(
        self,
        bake_name: str,
        *,
        repo_name: str,
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        poll: bool = True,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """
        Queue a bake (model training) job for the specified bake.

        Prereqs: bake config is complete (datasets + training settings); all referenced
        targets have completed rollouts; sufficient credit balance. Idempotent: repeated
        calls while a job exists return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET bake to monitor (status/job) and access
        artifacts after completion.

        Args:
          user_id: User ID override (requires master API key)

          x_user_id: User ID override via header (requires master API key)
          
          poll: Poll for the bake job status until it is complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        response = await self._post(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_run_params.BakeRunParams),
            ),
            cast_to=BakeResponse,
        )
        
        if poll:
            while response.status in ("not_started", "preparing", "pending", "running", "incomplete"):
                log.info("Status: %s, Percentage: %s", response.status, response.progress_percent)
                await self._sleep(30.0)
                response = await self.get(bake_name, repo_name=repo_name)
            
            if response.status == "complete":
                log.info("Bake job completed")
            elif response.status == "failed":
                log.warning("Bake job failed")

        return response

    @typing_extensions.deprecated("deprecated")
    async def set(
        self,
        bake_name: str,
        *,
        repo_name: str,
        template: str,
        user_id: Optional[str] | Omit = omit,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/bakes instead.

        Create or update a
        bake (idempotent). This endpoint will be removed in a future version.

        Args:
          template: Template: 'default' or existing bake name

          user_id: User ID override (requires master API key)

          overrides: Base bake configuration fields (for responses - all optional)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._put(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            body=await async_maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                bake_set_params.BakeSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, bake_set_params.BakeSetParams),
            ),
            cast_to=BakeResponse,
        )


class BakesResourceWithRawResponse:
    def __init__(self, bakes: BakesResource) -> None:
        self._bakes = bakes

        self.create = to_raw_response_wrapper(
            bakes.create,
        )
        self.list = to_raw_response_wrapper(
            bakes.list,
        )
        self.delete = to_raw_response_wrapper(
            bakes.delete,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                bakes.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = to_raw_response_wrapper(
            bakes.create_batch,
        )
        self.download = to_raw_response_wrapper(
            bakes.download,
        )
        self.get = to_raw_response_wrapper(
            bakes.get,
        )
        self.get_metrics = to_raw_response_wrapper(
            bakes.get_metrics,
        )
        self.run = to_raw_response_wrapper(
            bakes.run,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                bakes.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncBakesResourceWithRawResponse:
    def __init__(self, bakes: AsyncBakesResource) -> None:
        self._bakes = bakes

        self.create = async_to_raw_response_wrapper(
            bakes.create,
        )
        self.list = async_to_raw_response_wrapper(
            bakes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            bakes.delete,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                bakes.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = async_to_raw_response_wrapper(
            bakes.create_batch,
        )
        self.download = async_to_raw_response_wrapper(
            bakes.download,
        )
        self.get = async_to_raw_response_wrapper(
            bakes.get,
        )
        self.get_metrics = async_to_raw_response_wrapper(
            bakes.get_metrics,
        )
        self.run = async_to_raw_response_wrapper(
            bakes.run,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                bakes.set,  # pyright: ignore[reportDeprecated],
            )
        )


class BakesResourceWithStreamingResponse:
    def __init__(self, bakes: BakesResource) -> None:
        self._bakes = bakes

        self.create = to_streamed_response_wrapper(
            bakes.create,
        )
        self.list = to_streamed_response_wrapper(
            bakes.list,
        )
        self.delete = to_streamed_response_wrapper(
            bakes.delete,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                bakes.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = to_streamed_response_wrapper(
            bakes.create_batch,
        )
        self.download = to_streamed_response_wrapper(
            bakes.download,
        )
        self.get = to_streamed_response_wrapper(
            bakes.get,
        )
        self.get_metrics = to_streamed_response_wrapper(
            bakes.get_metrics,
        )
        self.run = to_streamed_response_wrapper(
            bakes.run,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                bakes.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncBakesResourceWithStreamingResponse:
    def __init__(self, bakes: AsyncBakesResource) -> None:
        self._bakes = bakes

        self.create = async_to_streamed_response_wrapper(
            bakes.create,
        )
        self.list = async_to_streamed_response_wrapper(
            bakes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            bakes.delete,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                bakes.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = async_to_streamed_response_wrapper(
            bakes.create_batch,
        )
        self.download = async_to_streamed_response_wrapper(
            bakes.download,
        )
        self.get = async_to_streamed_response_wrapper(
            bakes.get,
        )
        self.get_metrics = async_to_streamed_response_wrapper(
            bakes.get_metrics,
        )
        self.run = async_to_streamed_response_wrapper(
            bakes.run,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                bakes.set,  # pyright: ignore[reportDeprecated],
            )
        )
