# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import recipe_get_recreation_plan_params, recipe_get_dependency_graph_params
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
from ..types.recipe_get_recreation_plan_response import RecipeGetRecreationPlanResponse
from ..types.recipe_get_dependency_graph_response import RecipeGetDependencyGraphResponse

__all__ = ["RecipesResource", "AsyncRecipesResource"]


class RecipesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RecipesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return RecipesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RecipesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return RecipesResourceWithStreamingResponse(self)

    def get_dependency_graph(
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
    ) -> RecipeGetDependencyGraphResponse:
        """
        Get the dependency graph for a bake.

            Returns all resources (bakes, targets, prompts) and their dependencies
            needed to recreate this bake, including parent bakes and all transitive dependencies.
            The graph is built using BFS traversal starting from the specified bake.

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
            f"/v1/repo/{repo_name}/recipe/{bake_name}/dependency-graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"user_id": user_id}, recipe_get_dependency_graph_params.RecipeGetDependencyGraphParams
                ),
            ),
            cast_to=RecipeGetDependencyGraphResponse,
        )

    def get_recreation_plan(
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
    ) -> RecipeGetRecreationPlanResponse:
        """
        Get the recreation plan for a bake.

            Returns a step-by-step plan to recreate the bake, including all dependencies.
            The plan includes all prompts, targets, and bakes needed, in the correct execution order.
            Parent bake checkpoints are assumed to use the final checkpoint from each bake.

            The plan is topologically sorted to ensure dependencies are created before dependents.
            All configurations are cleaned and ready for use (no internal file paths).

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
            f"/v1/repo/{repo_name}/recipe/{bake_name}/recreation-plan",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"user_id": user_id}, recipe_get_recreation_plan_params.RecipeGetRecreationPlanParams
                ),
            ),
            cast_to=RecipeGetRecreationPlanResponse,
        )


class AsyncRecipesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRecipesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncRecipesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRecipesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncRecipesResourceWithStreamingResponse(self)

    async def get_dependency_graph(
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
    ) -> RecipeGetDependencyGraphResponse:
        """
        Get the dependency graph for a bake.

            Returns all resources (bakes, targets, prompts) and their dependencies
            needed to recreate this bake, including parent bakes and all transitive dependencies.
            The graph is built using BFS traversal starting from the specified bake.

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
            f"/v1/repo/{repo_name}/recipe/{bake_name}/dependency-graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"user_id": user_id}, recipe_get_dependency_graph_params.RecipeGetDependencyGraphParams
                ),
            ),
            cast_to=RecipeGetDependencyGraphResponse,
        )

    async def get_recreation_plan(
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
    ) -> RecipeGetRecreationPlanResponse:
        """
        Get the recreation plan for a bake.

            Returns a step-by-step plan to recreate the bake, including all dependencies.
            The plan includes all prompts, targets, and bakes needed, in the correct execution order.
            Parent bake checkpoints are assumed to use the final checkpoint from each bake.

            The plan is topologically sorted to ensure dependencies are created before dependents.
            All configurations are cleaned and ready for use (no internal file paths).

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
            f"/v1/repo/{repo_name}/recipe/{bake_name}/recreation-plan",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"user_id": user_id}, recipe_get_recreation_plan_params.RecipeGetRecreationPlanParams
                ),
            ),
            cast_to=RecipeGetRecreationPlanResponse,
        )


class RecipesResourceWithRawResponse:
    def __init__(self, recipes: RecipesResource) -> None:
        self._recipes = recipes

        self.get_dependency_graph = to_raw_response_wrapper(
            recipes.get_dependency_graph,
        )
        self.get_recreation_plan = to_raw_response_wrapper(
            recipes.get_recreation_plan,
        )


class AsyncRecipesResourceWithRawResponse:
    def __init__(self, recipes: AsyncRecipesResource) -> None:
        self._recipes = recipes

        self.get_dependency_graph = async_to_raw_response_wrapper(
            recipes.get_dependency_graph,
        )
        self.get_recreation_plan = async_to_raw_response_wrapper(
            recipes.get_recreation_plan,
        )


class RecipesResourceWithStreamingResponse:
    def __init__(self, recipes: RecipesResource) -> None:
        self._recipes = recipes

        self.get_dependency_graph = to_streamed_response_wrapper(
            recipes.get_dependency_graph,
        )
        self.get_recreation_plan = to_streamed_response_wrapper(
            recipes.get_recreation_plan,
        )


class AsyncRecipesResourceWithStreamingResponse:
    def __init__(self, recipes: AsyncRecipesResource) -> None:
        self._recipes = recipes

        self.get_dependency_graph = async_to_streamed_response_wrapper(
            recipes.get_dependency_graph,
        )
        self.get_recreation_plan = async_to_streamed_response_wrapper(
            recipes.get_recreation_plan,
        )
