# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import ios_instance_list_params, ios_instance_create_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncItems, AsyncItems
from .._base_client import AsyncPaginator, make_request_options
from ..types.ios_instance import IosInstance

__all__ = ["IosInstancesResource", "AsyncIosInstancesResource"]


class IosInstancesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IosInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return IosInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IosInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return IosInstancesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        reuse_if_exists: bool | Omit = omit,
        wait: bool | Omit = omit,
        metadata: ios_instance_create_params.Metadata | Omit = omit,
        spec: ios_instance_create_params.Spec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IosInstance:
        """
        Create an iOS instance

        Args:
          reuse_if_exists: If there is another instance with given labels and region, return that one
              instead of creating a new instance.

          wait: Return after the instance is ready to connect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/ios_instances",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "spec": spec,
                },
                ios_instance_create_params.IosInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "reuse_if_exists": reuse_if_exists,
                        "wait": wait,
                    },
                    ios_instance_create_params.IosInstanceCreateParams,
                ),
            ),
            cast_to=IosInstance,
        )

    def list(
        self,
        *,
        ending_before: str | Omit = omit,
        label_selector: str | Omit = omit,
        limit: int | Omit = omit,
        region: str | Omit = omit,
        starting_after: str | Omit = omit,
        state: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncItems[IosInstance]:
        """
        List iOS instances

        Args:
          label_selector: Labels filter to apply to instances to return. Expects a comma-separated list of
              key=value pairs (e.g., env=prod,region=us-west).

          limit: Maximum number of items to be returned. The default is 50.

          region: Region where the instance is scheduled on.

          state: State filter to apply to Android instances to return. Each comma-separated state
              will be used as part of an OR clause, e.g. "assigned,ready" will return all
              instances that are either assigned or ready.

              Valid states: creating, assigned, ready, terminated, unknown

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/ios_instances",
            page=SyncItems[IosInstance],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ending_before": ending_before,
                        "label_selector": label_selector,
                        "limit": limit,
                        "region": region,
                        "starting_after": starting_after,
                        "state": state,
                    },
                    ios_instance_list_params.IosInstanceListParams,
                ),
            ),
            model=IosInstance,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete iOS instance with given name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/ios_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IosInstance:
        """
        Get iOS instance with given ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v1/ios_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IosInstance,
        )


class AsyncIosInstancesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIosInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncIosInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIosInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return AsyncIosInstancesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        reuse_if_exists: bool | Omit = omit,
        wait: bool | Omit = omit,
        metadata: ios_instance_create_params.Metadata | Omit = omit,
        spec: ios_instance_create_params.Spec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IosInstance:
        """
        Create an iOS instance

        Args:
          reuse_if_exists: If there is another instance with given labels and region, return that one
              instead of creating a new instance.

          wait: Return after the instance is ready to connect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/ios_instances",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "spec": spec,
                },
                ios_instance_create_params.IosInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "reuse_if_exists": reuse_if_exists,
                        "wait": wait,
                    },
                    ios_instance_create_params.IosInstanceCreateParams,
                ),
            ),
            cast_to=IosInstance,
        )

    def list(
        self,
        *,
        ending_before: str | Omit = omit,
        label_selector: str | Omit = omit,
        limit: int | Omit = omit,
        region: str | Omit = omit,
        starting_after: str | Omit = omit,
        state: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[IosInstance, AsyncItems[IosInstance]]:
        """
        List iOS instances

        Args:
          label_selector: Labels filter to apply to instances to return. Expects a comma-separated list of
              key=value pairs (e.g., env=prod,region=us-west).

          limit: Maximum number of items to be returned. The default is 50.

          region: Region where the instance is scheduled on.

          state: State filter to apply to Android instances to return. Each comma-separated state
              will be used as part of an OR clause, e.g. "assigned,ready" will return all
              instances that are either assigned or ready.

              Valid states: creating, assigned, ready, terminated, unknown

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/ios_instances",
            page=AsyncItems[IosInstance],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ending_before": ending_before,
                        "label_selector": label_selector,
                        "limit": limit,
                        "region": region,
                        "starting_after": starting_after,
                        "state": state,
                    },
                    ios_instance_list_params.IosInstanceListParams,
                ),
            ),
            model=IosInstance,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete iOS instance with given name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/ios_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IosInstance:
        """
        Get iOS instance with given ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v1/ios_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IosInstance,
        )


class IosInstancesResourceWithRawResponse:
    def __init__(self, ios_instances: IosInstancesResource) -> None:
        self._ios_instances = ios_instances

        self.create = to_raw_response_wrapper(
            ios_instances.create,
        )
        self.list = to_raw_response_wrapper(
            ios_instances.list,
        )
        self.delete = to_raw_response_wrapper(
            ios_instances.delete,
        )
        self.get = to_raw_response_wrapper(
            ios_instances.get,
        )


class AsyncIosInstancesResourceWithRawResponse:
    def __init__(self, ios_instances: AsyncIosInstancesResource) -> None:
        self._ios_instances = ios_instances

        self.create = async_to_raw_response_wrapper(
            ios_instances.create,
        )
        self.list = async_to_raw_response_wrapper(
            ios_instances.list,
        )
        self.delete = async_to_raw_response_wrapper(
            ios_instances.delete,
        )
        self.get = async_to_raw_response_wrapper(
            ios_instances.get,
        )


class IosInstancesResourceWithStreamingResponse:
    def __init__(self, ios_instances: IosInstancesResource) -> None:
        self._ios_instances = ios_instances

        self.create = to_streamed_response_wrapper(
            ios_instances.create,
        )
        self.list = to_streamed_response_wrapper(
            ios_instances.list,
        )
        self.delete = to_streamed_response_wrapper(
            ios_instances.delete,
        )
        self.get = to_streamed_response_wrapper(
            ios_instances.get,
        )


class AsyncIosInstancesResourceWithStreamingResponse:
    def __init__(self, ios_instances: AsyncIosInstancesResource) -> None:
        self._ios_instances = ios_instances

        self.create = async_to_streamed_response_wrapper(
            ios_instances.create,
        )
        self.list = async_to_streamed_response_wrapper(
            ios_instances.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            ios_instances.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            ios_instances.get,
        )
