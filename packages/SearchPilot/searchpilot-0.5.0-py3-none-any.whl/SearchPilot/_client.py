# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import rules, steps, values, accounts, sections, customers, experiments, seo_experiment_results
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, SearchPilotError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "SearchPilot",
    "AsyncSearchPilot",
    "Client",
    "AsyncClient",
]


class SearchPilot(SyncAPIClient):
    customers: customers.CustomersResource
    accounts: accounts.AccountsResource
    sections: sections.SectionsResource
    rules: rules.RulesResource
    steps: steps.StepsResource
    values: values.ValuesResource
    experiments: experiments.ExperimentsResource
    seo_experiment_results: seo_experiment_results.SeoExperimentResultsResource
    with_raw_response: SearchPilotWithRawResponse
    with_streaming_response: SearchPilotWithStreamedResponse

    # client options
    api_jwt: str

    def __init__(
        self,
        *,
        api_jwt: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous SearchPilot client instance.

        This automatically infers the `api_jwt` argument from the `SEARCHPILOT_API_JWT` environment variable if it is not provided.
        """
        if api_jwt is None:
            api_jwt = os.environ.get("SEARCHPILOT_API_JWT")
        if api_jwt is None:
            raise SearchPilotError(
                "The api_jwt client option must be set either by passing api_jwt to the client or by setting the SEARCHPILOT_API_JWT environment variable"
            )
        self.api_jwt = api_jwt

        if base_url is None:
            base_url = os.environ.get("SEARCHPILOT_BASE_URL")
        if base_url is None:
            base_url = f"https://app.searchpilot.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.customers = customers.CustomersResource(self)
        self.accounts = accounts.AccountsResource(self)
        self.sections = sections.SectionsResource(self)
        self.rules = rules.RulesResource(self)
        self.steps = steps.StepsResource(self)
        self.values = values.ValuesResource(self)
        self.experiments = experiments.ExperimentsResource(self)
        self.seo_experiment_results = seo_experiment_results.SeoExperimentResultsResource(self)
        self.with_raw_response = SearchPilotWithRawResponse(self)
        self.with_streaming_response = SearchPilotWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="repeat")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_jwt = self.api_jwt
        return {"Authorization": f"Bearer {api_jwt}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_jwt: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_jwt=api_jwt or self.api_jwt,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncSearchPilot(AsyncAPIClient):
    customers: customers.AsyncCustomersResource
    accounts: accounts.AsyncAccountsResource
    sections: sections.AsyncSectionsResource
    rules: rules.AsyncRulesResource
    steps: steps.AsyncStepsResource
    values: values.AsyncValuesResource
    experiments: experiments.AsyncExperimentsResource
    seo_experiment_results: seo_experiment_results.AsyncSeoExperimentResultsResource
    with_raw_response: AsyncSearchPilotWithRawResponse
    with_streaming_response: AsyncSearchPilotWithStreamedResponse

    # client options
    api_jwt: str

    def __init__(
        self,
        *,
        api_jwt: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncSearchPilot client instance.

        This automatically infers the `api_jwt` argument from the `SEARCHPILOT_API_JWT` environment variable if it is not provided.
        """
        if api_jwt is None:
            api_jwt = os.environ.get("SEARCHPILOT_API_JWT")
        if api_jwt is None:
            raise SearchPilotError(
                "The api_jwt client option must be set either by passing api_jwt to the client or by setting the SEARCHPILOT_API_JWT environment variable"
            )
        self.api_jwt = api_jwt

        if base_url is None:
            base_url = os.environ.get("SEARCHPILOT_BASE_URL")
        if base_url is None:
            base_url = f"https://app.searchpilot.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.customers = customers.AsyncCustomersResource(self)
        self.accounts = accounts.AsyncAccountsResource(self)
        self.sections = sections.AsyncSectionsResource(self)
        self.rules = rules.AsyncRulesResource(self)
        self.steps = steps.AsyncStepsResource(self)
        self.values = values.AsyncValuesResource(self)
        self.experiments = experiments.AsyncExperimentsResource(self)
        self.seo_experiment_results = seo_experiment_results.AsyncSeoExperimentResultsResource(self)
        self.with_raw_response = AsyncSearchPilotWithRawResponse(self)
        self.with_streaming_response = AsyncSearchPilotWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="repeat")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_jwt = self.api_jwt
        return {"Authorization": f"Bearer {api_jwt}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_jwt: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_jwt=api_jwt or self.api_jwt,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class SearchPilotWithRawResponse:
    def __init__(self, client: SearchPilot) -> None:
        self.customers = customers.CustomersResourceWithRawResponse(client.customers)
        self.accounts = accounts.AccountsResourceWithRawResponse(client.accounts)
        self.sections = sections.SectionsResourceWithRawResponse(client.sections)
        self.rules = rules.RulesResourceWithRawResponse(client.rules)
        self.steps = steps.StepsResourceWithRawResponse(client.steps)
        self.values = values.ValuesResourceWithRawResponse(client.values)
        self.experiments = experiments.ExperimentsResourceWithRawResponse(client.experiments)
        self.seo_experiment_results = seo_experiment_results.SeoExperimentResultsResourceWithRawResponse(
            client.seo_experiment_results
        )


class AsyncSearchPilotWithRawResponse:
    def __init__(self, client: AsyncSearchPilot) -> None:
        self.customers = customers.AsyncCustomersResourceWithRawResponse(client.customers)
        self.accounts = accounts.AsyncAccountsResourceWithRawResponse(client.accounts)
        self.sections = sections.AsyncSectionsResourceWithRawResponse(client.sections)
        self.rules = rules.AsyncRulesResourceWithRawResponse(client.rules)
        self.steps = steps.AsyncStepsResourceWithRawResponse(client.steps)
        self.values = values.AsyncValuesResourceWithRawResponse(client.values)
        self.experiments = experiments.AsyncExperimentsResourceWithRawResponse(client.experiments)
        self.seo_experiment_results = seo_experiment_results.AsyncSeoExperimentResultsResourceWithRawResponse(
            client.seo_experiment_results
        )


class SearchPilotWithStreamedResponse:
    def __init__(self, client: SearchPilot) -> None:
        self.customers = customers.CustomersResourceWithStreamingResponse(client.customers)
        self.accounts = accounts.AccountsResourceWithStreamingResponse(client.accounts)
        self.sections = sections.SectionsResourceWithStreamingResponse(client.sections)
        self.rules = rules.RulesResourceWithStreamingResponse(client.rules)
        self.steps = steps.StepsResourceWithStreamingResponse(client.steps)
        self.values = values.ValuesResourceWithStreamingResponse(client.values)
        self.experiments = experiments.ExperimentsResourceWithStreamingResponse(client.experiments)
        self.seo_experiment_results = seo_experiment_results.SeoExperimentResultsResourceWithStreamingResponse(
            client.seo_experiment_results
        )


class AsyncSearchPilotWithStreamedResponse:
    def __init__(self, client: AsyncSearchPilot) -> None:
        self.customers = customers.AsyncCustomersResourceWithStreamingResponse(client.customers)
        self.accounts = accounts.AsyncAccountsResourceWithStreamingResponse(client.accounts)
        self.sections = sections.AsyncSectionsResourceWithStreamingResponse(client.sections)
        self.rules = rules.AsyncRulesResourceWithStreamingResponse(client.rules)
        self.steps = steps.AsyncStepsResourceWithStreamingResponse(client.steps)
        self.values = values.AsyncValuesResourceWithStreamingResponse(client.values)
        self.experiments = experiments.AsyncExperimentsResourceWithStreamingResponse(client.experiments)
        self.seo_experiment_results = seo_experiment_results.AsyncSeoExperimentResultsResourceWithStreamingResponse(
            client.seo_experiment_results
        )


Client = SearchPilot

AsyncClient = AsyncSearchPilot
