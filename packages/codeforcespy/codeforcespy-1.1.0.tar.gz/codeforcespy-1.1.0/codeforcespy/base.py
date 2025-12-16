"""
🏗️ **Base Client Architecture**.
================================

This module provides the foundational `BaseClient` class, which establishes the
core infrastructure for authentication, request handling, and response validation.

🔧 **Core Capabilities**
------------------------
- 🔑 **Authentication**: Secure generation of API signatures (SHA-512).
- 📡 **Request Handling**: Robust mechanism for executing HTTP operations.
- 🧹 **Data Sanitization**: Utilities for normalizing API inputs (e.g., list conversions).
- 🧩 **Extensibility**: Designed as an abstract base for specific client implementations.

📦 **Classes**
--------------
- `BaseClient`: Abstract base class implementing shared client logic.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import collections
import hashlib
import random
import time
import typing
import urllib.parse

import codeforcespy.abc.endpoints

T = typing.TypeVar("T", bound=object)


class BaseClient:
    """
    Abstract base class for Codeforces API clients.

    Attributes
    ----------
    _url_generator : codeforcespy.abc.endpoints.CodeForcesAPI
        Instance for generating API endpoint URLs.
    _auth_key : str | None
        Authentication key for API requests.
    _secret : str | None
        Secret key for request signing.
    _time : int | None
        Unix timestamp used for request signing.
    _auth_enabled : bool
        Indicates if authentication is enabled.
    """

    __slots__: tuple[str, ...] = (
        "_auth_enabled",
        "_auth_key",
        "_secret",
        "_time",
        "_url_generator",
    )

    def __init__(
        self,
        enable_auth: bool | None = False,
        auth_key: str | None = None,
        unix_time: int | None = None,
        secret: str | None = None,
    ) -> None:
        """
        Initialize the base client.

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
        self._url_generator: codeforcespy.abc.endpoints.CodeForcesAPI = (
            codeforcespy.abc.endpoints.CodeForcesAPI()
        )
        self._auth_key: str | None = auth_key
        self._secret: str | None = secret
        self._time: int | None = unix_time
        self._auth_enabled: bool = bool(enable_auth)

    def _generate_authorisation(
        self,
        end_point_url: str,
        method_name: str,
    ) -> str:
        """
        Generate an authorised URL for a given API endpoint.

        Parameters
        ----------
        end_point_url : str
            The raw endpoint URL.
        method_name : str
            The API method name.

        Returns
        -------
        str
            The authorised URL if authentication is enabled; otherwise, the original endpoint URL.
        """
        if self._auth_enabled:
            # Use current time if fixed time not set
            current_time = self._time if self._time is not None else int(time.time())

            random_six_digit = random.randint(111111, 999999)
            prefix = f"https://codeforces.com/api/{method_name}?"
            head = end_point_url.removeprefix(prefix)

            params = {
                x.split("=")[0]: x.split("=")[1]
                for x in head.split("&")
                if x and "=" in x
            }
            sorted_params = collections.OrderedDict(sorted(params.items()))
            encoded_params = urllib.parse.urlencode(sorted_params, safe=";")

            to_hash = (
                f"{random_six_digit}/{method_name}?apiKey={self._auth_key}&"
                f"{encoded_params}&time={current_time}#{self._secret}"
            )
            hashed_string = hashlib.sha512(to_hash.encode("utf8")).hexdigest()

            final_url = (
                f"https://codeforces.com/api/{method_name}?"
                f"{encoded_params}&apiKey={self._auth_key}&time={current_time}"
                f"&apiSig={random_six_digit}{hashed_string}"
            )
            return final_url
        return end_point_url

    @staticmethod
    def _ensure_list(
        result: list[T] | T | None,
    ) -> list[T]:
        """
        Ensure that the API result is returned as a list.

        Parameters
        ----------
        result : list[T] | T | None
            The API result.

        Returns
        -------
        list[T]
            The result as a list.

        Raises
        ------
        TypeError
            If the result is compatible but we need strict types.
        """
        if result is None:
            # Explicitly cast empty list to list[T] to avoid unknown type warning
            return typing.cast("list[T]", [])
        if isinstance(result, list):
            return typing.cast("list[T]", result)
        return [result]
