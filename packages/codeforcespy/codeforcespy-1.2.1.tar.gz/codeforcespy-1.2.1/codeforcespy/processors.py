"""
🚀 Codeforces API Processors.
================================

This module acts as the central hub for synchronous and asynchronous interactions
with the Codeforces API. It aggregates domain-specific logic into unified client
classes, ensuring a seamless developer experience.

✨ Key Features
-------------------
- 🔄 Unified Clients: `SyncMethod` and `AsyncMethod` consolidate all API features.
- 🔐 Secure Auth: Optional API key and secret handling for private endpoints.
- ⚡ High Performance: Optimized for both blocking and non-blocking I/O contexts.
- 🛡️ Type Safety: Fully typed strict compliance (PEP 484).

📦 Classes
--------------
- `SyncMethod`: Synchronous client inheriting all feature mixins.
- `AsyncMethod`: Asynchronous client inheriting all feature mixins.

📝 Compliance
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import typing

import msgspec

import codeforcespy.abc.protocols
import codeforcespy.base
import codeforcespy.clients
import codeforcespy.errors
import codeforcespy.features.blog
import codeforcespy.features.contest
import codeforcespy.features.problemset
import codeforcespy.features.recent
import codeforcespy.features.user


class SyncMethod(
    codeforcespy.base.BaseClient,
    codeforcespy.features.user.SyncUser,
    codeforcespy.features.blog.SyncBlog,
    codeforcespy.features.contest.SyncContest,
    codeforcespy.features.problemset.SyncProblemset,
    codeforcespy.features.recent.SyncRecent,
):
    """
    Synchronous Codeforces API client for executing requests with optional authentication.

    Attributes
    ----------
    _client : codeforcespy.clients.SyncClient
        Synchronous HTTP client for making API requests.
    """

    def __init__(
        self,
        enable_auth: bool | None = False,
        auth_key: str | None = None,
        unix_time: int | None = None,
        secret: str | None = None,
    ) -> None:
        """
        Initialize the synchronous client.

        Parameters
        ----------
        enable_auth : bool | None, optional
            Whether to enable authentication (default is False).
        auth_key : str | None, optional
            API authentication key (default is None).
        unix_time : int | None, optional
            Unix timestamp for signing requests (default is None).
        secret : str | None, optional
            API secret for signing requests (default is None).
        """
        super().__init__(enable_auth, auth_key, unix_time, secret)
        self._client: codeforcespy.clients.SyncClient = (
            codeforcespy.clients.SyncClient()
        )

    def _generate_response(self, url: str) -> bytes:
        """
        Execute an HTTP GET request and return the response content.

        Parameters
        ----------
        url : str
            The URL to request.

        Returns
        -------
        bytes
            The raw response content.
        """
        with self._client as socket:
            response = socket.get(url=url)
            return response.content

    @typing.override
    def _execute_request(
        self,
        method_name: str,
        endpoint_url: str,
        response_cls: type[codeforcespy.abc.protocols.ResponseProtocol],
    ) -> list[object]:
        """
        Execute an API request synchronously and decode the response.

        Parameters
        ----------
        method_name : str
            The API method name.
        endpoint_url : str
            The raw endpoint URL.
        response_cls : type[ResponseProtocol]
            The class used to decode the JSON response.

        Returns
        -------
        list[object]
            The decoded result wrapped as a list.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        final_url: str = self._generate_authorisation(
            method_name=method_name, end_point_url=endpoint_url
        )
        response_bytes: bytes = self._generate_response(url=final_url)
        base = msgspec.json.decode(response_bytes, strict=False, type=response_cls)

        if base.status != "FAILED":
            return self._ensure_list(base.result)
        else:
            raise codeforcespy.errors.APIError(base.comment)

    def close(self) -> None:
        """Close the underlying synchronous HTTP client."""
        self._client.close()


class AsyncMethod(
    codeforcespy.base.BaseClient,
    codeforcespy.features.user.AsyncUser,
    codeforcespy.features.blog.AsyncBlog,
    codeforcespy.features.contest.AsyncContest,
    codeforcespy.features.problemset.AsyncProblemset,
    codeforcespy.features.recent.AsyncRecent,
):
    """
    Asynchronous Codeforces API client for executing requests with optional authentication.

    Attributes
    ----------
    _client : codeforcespy.clients.AsyncClient
        Asynchronous HTTP client for making API requests.
    """

    def __init__(
        self,
        enable_auth: bool | None = False,
        auth_key: str | None = None,
        unix_time: int | None = None,
        secret: str | None = None,
    ) -> None:
        """
        Initialize the asynchronous client.

        Parameters
        ----------
        enable_auth : bool | None, optional
            Whether to enable authentication (default is False).
        auth_key : str | None, optional
            API authentication key (default is None).
        unix_time : int | None, optional
            Unix timestamp for signing requests (default is None).
        secret : str | None, optional
            API secret for signing requests (default is None).
        """
        super().__init__(enable_auth, auth_key, unix_time, secret)
        self._client: codeforcespy.clients.AsyncClient = (
            codeforcespy.clients.AsyncClient()
        )

    async def _generate_response(self, url: str) -> bytes:
        """
        Execute an asynchronous HTTP GET request and return the response content.

        Parameters
        ----------
        url : str
            The URL to request.

        Returns
        -------
        bytes
            The raw response content.
        """
        async with self._client as socket:
            response = await socket.get(url=url)
            return response.read()

    @typing.override
    async def _execute_request(
        self,
        method_name: str,
        endpoint_url: str,
        response_cls: type[codeforcespy.abc.protocols.ResponseProtocol],
    ) -> list[object]:
        """
        Execute an asynchronous API request and decode the response.

        Parameters
        ----------
        method_name : str
            The API method name.
        endpoint_url : str
            The raw endpoint URL.
        response_cls : type[ResponseProtocol]
            The class used to decode the JSON response.

        Returns
        -------
        list[object]
            The decoded result wrapped as a list.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        final_url: str = self._generate_authorisation(
            method_name=method_name, end_point_url=endpoint_url
        )
        response_bytes: bytes = await self._generate_response(url=final_url)
        base = msgspec.json.decode(response_bytes, strict=False, type=response_cls)

        if base.status != "FAILED":
            return self._ensure_list(base.result)
        else:
            raise codeforcespy.errors.APIError(base.comment)

    async def close(self) -> None:
        """Asynchronously close the underlying HTTP client."""
        await self._client.aclose()
