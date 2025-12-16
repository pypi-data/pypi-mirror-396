"""
🕒 **Recent Features Mixins**.
=============================

Domain-specific logic for recent action-related API endpoints.

✨ **Capabilities**
-------------------
- 📜 **Actions**: Retrieve recent actions across the platform.
- 🆕 **Updates**: Stay updated with the latest community activities.

📦 **Classes**
--------------
- `SyncRecent`: Synchronous mixin for recent action operations.
- `AsyncRecent`: Asynchronous mixin for recent action operations.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import abc
import typing

import codeforcespy.abc.interactions
import codeforcespy.abc.objects
from codeforcespy.features.mixin_base import AsyncFeatureMixin
from codeforcespy.features.mixin_base import SyncFeatureMixin


class SyncRecent(SyncFeatureMixin, abc.ABC):
    """Mixin for synchronous recent action-related operations."""

    def get_recent_actions(
        self, max_count: int
    ) -> list[codeforcespy.abc.objects.RecentAction]:
        """
        Retrieve recent actions.

        Parameters
        ----------
        max_count : int
            The maximum number of recent actions to retrieve.

        Returns
        -------
        list[codeforcespy.abc.objects.RecentAction]
            A list of recent action objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.recent_actions(max_count=max_count)
        result = self._execute_request(
            "recentActions",
            endpoint_url,
            codeforcespy.abc.interactions.RecentActionsResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RecentAction]", result)


class AsyncRecent(AsyncFeatureMixin, abc.ABC):
    """Mixin for asynchronous recent action-related operations."""

    async def get_recent_actions(
        self, max_count: int
    ) -> list[codeforcespy.abc.objects.RecentAction]:
        """
        Asynchronously retrieve recent actions.

        Parameters
        ----------
        max_count : int
            The maximum number of recent actions to retrieve.

        Returns
        -------
        list[codeforcespy.abc.objects.RecentAction]
            A list of recent action objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.recent_actions(max_count=max_count)
        result = await self._execute_request(
            "recentActions",
            endpoint_url,
            codeforcespy.abc.interactions.RecentActionsResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RecentAction]", result)
