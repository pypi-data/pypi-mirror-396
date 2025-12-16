# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import Dict, Iterable, Optional

import httpx

from ..types import (
    prompt_get_params,
    prompt_set_params,
    prompt_list_params,
    prompt_create_params,
    prompt_batch_set_params,
    prompt_create_batch_params,
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
from ..types.message_param import MessageParam
from ..types.prompt_response import PromptResponse
from ..types.prompt_list_response import PromptListResponse
from ..types.prompt_batch_set_response import PromptBatchSetResponse
from ..types.prompt_create_batch_response import PromptCreateBatchResponse

__all__ = ["PromptsResource", "AsyncPromptsResource"]


class PromptsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PromptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return PromptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PromptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return PromptsResourceWithStreamingResponse(self)

    def create(
        self,
        repo_name: str,
        *,
        messages: Iterable[MessageParam],
        prompt_name: str,
        user_id: Optional[str] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """Creates a new prompt.

        Idempotent: if prompt exists with same content, returns
        existing (200). If exists with different content, returns 409 Conflict.

        Args:
          messages: List of messages in the prompt

          prompt_name: Name of the prompt

          user_id: User ID override (requires master API key)

          tools: List of available tools/functions (OpenAI format)

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
            f"/v1/repo/{repo_name}/prompts",
            body=maybe_transform(
                {
                    "messages": messages,
                    "prompt_name": prompt_name,
                    "tools": tools,
                },
                prompt_create_params.PromptCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, prompt_create_params.PromptCreateParams),
            ),
            cast_to=PromptResponse,
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
    ) -> PromptListResponse:
        """
        Lists prompts in the repository for discovery and validation.

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
            f"/v1/repo/{repo_name}/prompts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, prompt_list_params.PromptListParams),
            ),
            cast_to=PromptListResponse,
        )

    @typing_extensions.deprecated("deprecated")
    def batch_set(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptBatchSetResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/prompts/batch instead.

        Creates or
        updates multiple prompts. Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

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
            f"/v1/repo/{repo_name}/prompts/batch",
            body=maybe_transform({"prompts": prompts}, prompt_batch_set_params.PromptBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, prompt_batch_set_params.PromptBatchSetParams),
            ),
            cast_to=PromptBatchSetResponse,
        )

    def create_batch(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptCreateBatchResponse:
        """Creates or updates multiple prompts.

        Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

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
            f"/v1/repo/{repo_name}/prompts/batch",
            body=maybe_transform({"prompts": prompts}, prompt_create_batch_params.PromptCreateBatchParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, prompt_create_batch_params.PromptCreateBatchParams),
            ),
            cast_to=PromptCreateBatchResponse,
        )

    def get(
        self,
        prompt_name: str,
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
    ) -> PromptResponse:
        """
        Returns the prompt definition and metadata.

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
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._get(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"user_id": user_id}, prompt_get_params.PromptGetParams),
            ),
            cast_to=PromptResponse,
        )

    @typing_extensions.deprecated("deprecated")
    def set(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        messages: Iterable[MessageParam],
        user_id: Optional[str] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/prompts instead.

        Creates or updates a
        single prompt. Idempotent; invalid names return 422. This endpoint will be
        removed in a future version.

        Args:
          messages: List of messages in the prompt

          user_id: User ID override (requires master API key)

          tools: List of available tools/functions (OpenAI format)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return self._put(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            body=maybe_transform(
                {
                    "messages": messages,
                    "tools": tools,
                },
                prompt_set_params.PromptSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"user_id": user_id}, prompt_set_params.PromptSetParams),
            ),
            cast_to=PromptResponse,
        )


class AsyncPromptsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPromptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncPromptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPromptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncPromptsResourceWithStreamingResponse(self)

    async def create(
        self,
        repo_name: str,
        *,
        messages: Iterable[MessageParam],
        prompt_name: str,
        user_id: Optional[str] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """Creates a new prompt.

        Idempotent: if prompt exists with same content, returns
        existing (200). If exists with different content, returns 409 Conflict.

        Args:
          messages: List of messages in the prompt

          prompt_name: Name of the prompt

          user_id: User ID override (requires master API key)

          tools: List of available tools/functions (OpenAI format)

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
            f"/v1/repo/{repo_name}/prompts",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "prompt_name": prompt_name,
                    "tools": tools,
                },
                prompt_create_params.PromptCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, prompt_create_params.PromptCreateParams),
            ),
            cast_to=PromptResponse,
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
    ) -> PromptListResponse:
        """
        Lists prompts in the repository for discovery and validation.

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
            f"/v1/repo/{repo_name}/prompts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, prompt_list_params.PromptListParams),
            ),
            cast_to=PromptListResponse,
        )

    @typing_extensions.deprecated("deprecated")
    async def batch_set(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptBatchSetResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/prompts/batch instead.

        Creates or
        updates multiple prompts. Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

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
            f"/v1/repo/{repo_name}/prompts/batch",
            body=await async_maybe_transform({"prompts": prompts}, prompt_batch_set_params.PromptBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, prompt_batch_set_params.PromptBatchSetParams),
            ),
            cast_to=PromptBatchSetResponse,
        )

    async def create_batch(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        user_id: Optional[str] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptCreateBatchResponse:
        """Creates or updates multiple prompts.

        Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

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
            f"/v1/repo/{repo_name}/prompts/batch",
            body=await async_maybe_transform({"prompts": prompts}, prompt_create_batch_params.PromptCreateBatchParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform(
                    {"user_id": user_id}, prompt_create_batch_params.PromptCreateBatchParams
                ),
            ),
            cast_to=PromptCreateBatchResponse,
        )

    async def get(
        self,
        prompt_name: str,
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
    ) -> PromptResponse:
        """
        Returns the prompt definition and metadata.

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
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._get(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"user_id": user_id}, prompt_get_params.PromptGetParams),
            ),
            cast_to=PromptResponse,
        )

    @typing_extensions.deprecated("deprecated")
    async def set(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        messages: Iterable[MessageParam],
        user_id: Optional[str] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        x_user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """[DEPRECATED] Use POST /v1/repo/{repo_name}/prompts instead.

        Creates or updates a
        single prompt. Idempotent; invalid names return 422. This endpoint will be
        removed in a future version.

        Args:
          messages: List of messages in the prompt

          user_id: User ID override (requires master API key)

          tools: List of available tools/functions (OpenAI format)

          x_user_id: User ID override via header (requires master API key)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        extra_headers = {**strip_not_given({"X-User-Id": x_user_id}), **(extra_headers or {})}
        return await self._put(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "tools": tools,
                },
                prompt_set_params.PromptSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform({"user_id": user_id}, prompt_set_params.PromptSetParams),
            ),
            cast_to=PromptResponse,
        )


class PromptsResourceWithRawResponse:
    def __init__(self, prompts: PromptsResource) -> None:
        self._prompts = prompts

        self.create = to_raw_response_wrapper(
            prompts.create,
        )
        self.list = to_raw_response_wrapper(
            prompts.list,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                prompts.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = to_raw_response_wrapper(
            prompts.create_batch,
        )
        self.get = to_raw_response_wrapper(
            prompts.get,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                prompts.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncPromptsResourceWithRawResponse:
    def __init__(self, prompts: AsyncPromptsResource) -> None:
        self._prompts = prompts

        self.create = async_to_raw_response_wrapper(
            prompts.create,
        )
        self.list = async_to_raw_response_wrapper(
            prompts.list,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                prompts.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = async_to_raw_response_wrapper(
            prompts.create_batch,
        )
        self.get = async_to_raw_response_wrapper(
            prompts.get,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                prompts.set,  # pyright: ignore[reportDeprecated],
            )
        )


class PromptsResourceWithStreamingResponse:
    def __init__(self, prompts: PromptsResource) -> None:
        self._prompts = prompts

        self.create = to_streamed_response_wrapper(
            prompts.create,
        )
        self.list = to_streamed_response_wrapper(
            prompts.list,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                prompts.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = to_streamed_response_wrapper(
            prompts.create_batch,
        )
        self.get = to_streamed_response_wrapper(
            prompts.get,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                prompts.set,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncPromptsResourceWithStreamingResponse:
    def __init__(self, prompts: AsyncPromptsResource) -> None:
        self._prompts = prompts

        self.create = async_to_streamed_response_wrapper(
            prompts.create,
        )
        self.list = async_to_streamed_response_wrapper(
            prompts.list,
        )
        self.batch_set = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                prompts.batch_set,  # pyright: ignore[reportDeprecated],
            )
        )
        self.create_batch = async_to_streamed_response_wrapper(
            prompts.create_batch,
        )
        self.get = async_to_streamed_response_wrapper(
            prompts.get,
        )
        self.set = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                prompts.set,  # pyright: ignore[reportDeprecated],
            )
        )
