"""
🧩 **Problemset Features Mixins**.
=================================

Domain-specific logic for problemset-related API endpoints.

✨ **Capabilities**
-------------------
- 📚 **Problems**: Retrieve list of problems from the problemset.
- 📨 **Recent**: Access recent submissions.
- 📂 **Filtering**: Filter problems by tags and difficulty.

📦 **Classes**
--------------
- `SyncProblemset`: Synchronous mixin for problemset operations.
- `AsyncProblemset`: Asynchronous mixin for problemset operations.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import abc
import typing

import codeforcespy.abc.cobjects
import codeforcespy.abc.interactions
import codeforcespy.abc.objects
from codeforcespy.features.mixin_base import AsyncFeatureMixin
from codeforcespy.features.mixin_base import SyncFeatureMixin


class SyncProblemset(SyncFeatureMixin, abc.ABC):
    """Mixin for synchronous problemset-related operations."""

    def get_problemset_problems(
        self, tags: str | None = None, problemset_name: str | None = None
    ) -> list[codeforcespy.abc.cobjects.ProblemSetProblems]:
        """
        Retrieve problems from the problem set.

        Parameters
        ----------
        tags : str | None, optional
            Semicolon-separated list of tags (default is None).
        problemset_name : str | None, optional
            Custom problem set name (default is None).

        Returns
        -------
        list[codeforcespy.abc.cobjects.ProblemSetProblems]
            A list of problem set problems objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.problemset_problems(
            tags=tags, problemset_name=problemset_name
        )
        result = self._execute_request(
            "problemset.problems",
            endpoint_url,
            codeforcespy.abc.interactions.ProblemSetProblemsResponse,
        )
        return typing.cast("list[codeforcespy.abc.cobjects.ProblemSetProblems]", result)

    def get_problemset_recent_status(
        self, count: int, problemset_name: str | None = None
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Retrieve recent submissions for the problem set.

        Parameters
        ----------
        count : int
            The number of submissions to retrieve.
        problemset_name : str | None, optional
            Custom problem set name (default is None).

        Returns
        -------
        list[codeforcespy.abc.objects.Submission]
            A list of submission objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.problemset_recent_status(
            count=count, problemset_name=problemset_name
        )
        result = self._execute_request(
            "problemset.recentStatus",
            endpoint_url,
            codeforcespy.abc.interactions.ProblemSetRecentStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)


class AsyncProblemset(AsyncFeatureMixin, abc.ABC):
    """Mixin for asynchronous problemset-related operations."""

    async def get_problemset_problems(
        self, tags: str | None = None, problemset_name: str | None = None
    ) -> list[codeforcespy.abc.cobjects.ProblemSetProblems]:
        """
        Asynchronously retrieve problems from the problem set.

        Parameters
        ----------
        tags : str | None, optional
            Semicolon-separated list of tags (default is None).
        problemset_name : str | None, optional
            Custom problem set name (default is None).

        Returns
        -------
        list[codeforcespy.abc.cobjects.ProblemSetProblems]
            A list of problem set problems objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.problemset_problems(
            tags=tags, problemset_name=problemset_name
        )
        result = await self._execute_request(
            "problemset.problems",
            endpoint_url,
            codeforcespy.abc.interactions.ProblemSetProblemsResponse,
        )
        return typing.cast("list[codeforcespy.abc.cobjects.ProblemSetProblems]", result)

    async def get_problemset_recent_status(
        self, count: int, problemset_name: str | None = None
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Asynchronously retrieve recent submissions for the problem set.

        Parameters
        ----------
        count : int
            The number of submissions to retrieve.
        problemset_name : str | None, optional
            Custom problem set name (default is None).

        Returns
        -------
        list[codeforcespy.abc.objects.Submission]
            A list of submission objects.

        Raises
        ------
        Exception
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.problemset_recent_status(
            count=count, problemset_name=problemset_name
        )
        result = await self._execute_request(
            "problemset.recentStatus",
            endpoint_url,
            codeforcespy.abc.interactions.ProblemSetRecentStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)
