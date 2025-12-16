"""Protocols for Codeforces API responses."""

import typing


class ResponseProtocol(typing.Protocol):
    """Protocol describing the structure of a Codeforces API response."""

    status: str
    comment: str | None

    @property
    def result(self) -> object:
        """The result payload of the API response."""
        ...
