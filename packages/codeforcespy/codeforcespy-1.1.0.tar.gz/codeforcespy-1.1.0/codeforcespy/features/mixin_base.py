"""
🏗️ **Feature Mixin Bases**.
===========================

Base classes for synchronizing and asynchronous feature implementation.

✨🧩 **Mixin Architecture**.
-------------------
- 🏗️ **FeatureMixin**: Common base for all feature modules.
- 🔄 **SyncFeatureMixin**: Base for synchronous implementations.
- ⚡ **AsyncFeatureMixin**: Base for asynchronous implementations.
- 🔌 **Abstract Methods**: Defines `_execute_request` contract.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    import codeforcespy.abc.endpoints
    import codeforcespy.abc.protocols


class FeatureMixin(abc.ABC):
    """Base class for all feature mixins."""

    if typing.TYPE_CHECKING:
        _url_generator: "codeforcespy.abc.endpoints.CodeForcesAPI"


class SyncFeatureMixin(FeatureMixin, abc.ABC):
    """Base class for synchronous feature mixins."""

    @abc.abstractmethod
    def _execute_request(
        self,
        method_name: str,
        endpoint_url: str,
        response_cls: type["codeforcespy.abc.protocols.ResponseProtocol"],
    ) -> list[object]:
        """Abstract method for executing synchronous requests."""
        ...


class AsyncFeatureMixin(FeatureMixin, abc.ABC):
    """Base class for asynchronous feature mixins."""

    @abc.abstractmethod
    async def _execute_request(
        self,
        method_name: str,
        endpoint_url: str,
        response_cls: type["codeforcespy.abc.protocols.ResponseProtocol"],
    ) -> list[object]:
        """Abstract method for executing asynchronous requests."""
        ...
