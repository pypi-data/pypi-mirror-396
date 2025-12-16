"""
🏆 Contest Features Mixins.
==============================

Domain-specific logic for contest-related API endpoints.

✨ Capabilities
-------------------
- 📅 List: Retrieve list of available contests.
- 📊 Standings: Access contest standings and rating changes.
- 🕵️ Hacks: Inspect successful and unsuccessful hacks.
- 🏁 Status: Check submissions within a specific contest.

📦 Classes
--------------
- `SyncContest`: Synchronous mixin for contest operations.
- `AsyncContest`: Asynchronous mixin for contest operations.

📝 Compliance
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import abc
import typing

import codeforcespy.abc.cobjects
import codeforcespy.abc.interactions
import codeforcespy.abc.objects
import codeforcespy.features.mixin_base


class SyncContest(codeforcespy.features.mixin_base.SyncFeatureMixin, abc.ABC):
    """Mixin for synchronous contest-related operations."""

    def get_contest_hacks(
        self, contest_id: int, as_manager: bool | None = False
    ) -> list[codeforcespy.abc.objects.Hack]:
        """
        Retrieve contest hacks for a specific contest.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve hacks as a contest manager (default is False).

        Returns
        -------
        list[codeforcespy.abc.objects.Hack]
            A list of hack objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_hacks(
            contest_id=contest_id, as_manager=as_manager
        )
        result = self._execute_request(
            "contest.hacks",
            endpoint_url,
            codeforcespy.abc.interactions.ContestHacksResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Hack]", result)

    def get_contest_list(
        self, of_gym: bool | None = False
    ) -> list[codeforcespy.abc.objects.Contest]:
        """
        Retrieve a list of contests.

        Parameters
        ----------
        of_gym : bool | None, optional
            Whether to include gym contests (default is False).

        Returns
        -------
        list[codeforcespy.abc.objects.Contest]
            A list of contest objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_list(gym=of_gym)
        result = self._execute_request(
            "contest.list",
            endpoint_url,
            codeforcespy.abc.interactions.ContestListResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Contest]", result)

    def get_contest_rating_changes(
        self, contest_id: int
    ) -> list[codeforcespy.abc.objects.RatingChange]:
        """
        Retrieve rating changes for a specific contest.

        Parameters
        ----------
        contest_id : int
            The contest ID.

        Returns
        -------
        list[codeforcespy.abc.objects.RatingChange]
            A list of rating change objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_rating_changes(
            contest_id=contest_id
        )
        result = self._execute_request(
            "contest.ratingChanges",
            endpoint_url,
            codeforcespy.abc.interactions.ContestRatingChangeResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RatingChange]", result)

    def get_contest_standings(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        from_index: int = 1,
        count: int = 5,
        show_unofficial: bool | None = True,
    ) -> list[codeforcespy.abc.cobjects.Standings]:
        """
        Retrieve contest standings.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve standings as a contest manager (default is False).
        from_index : int, optional
            The starting index for standings (default is 1).
        count : int, optional
            The number of standings rows to retrieve (default is 5).
        show_unofficial : bool | None, optional
            Whether to show unofficial standings (default is True).

        Returns
        -------
        list[codeforcespy.abc.cobjects.Standings]
            A list of standings objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_standings(
            contest_id=contest_id,
            as_manager=as_manager,
            from_index=from_index,
            count=count,
            show_unofficial=show_unofficial,
        )
        result = self._execute_request(
            "contest.standings",
            endpoint_url,
            codeforcespy.abc.interactions.ContestStandingResponse,
        )
        return typing.cast("list[codeforcespy.abc.cobjects.Standings]", result)

    def get_contest_status(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        handle: str | None = None,
        from_index: int = 1,
        count: int = 10,
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Retrieve contest submissions.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve status as a contest manager (default is False).
        handle : str | None, optional
            The user handle to filter submissions (default is None).
        from_index : int, optional
            The starting index for submissions (default is 1).
        count : int, optional
            The number of submissions to retrieve (default is 10).

        Returns
        -------
        list[codeforcespy.abc.objects.Submission]
            A list of submission objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_status(
            contest_id=contest_id,
            as_manager=as_manager,
            handle=handle,
            from_index=from_index,
            count=count,
        )
        result = self._execute_request(
            "contest.status",
            endpoint_url,
            codeforcespy.abc.interactions.ContestStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)


class AsyncContest(codeforcespy.features.mixin_base.AsyncFeatureMixin, abc.ABC):
    """Mixin for asynchronous contest-related operations."""

    async def get_contest_hacks(
        self, contest_id: int, as_manager: bool | None = False
    ) -> list[codeforcespy.abc.objects.Hack]:
        """
        Asynchronously retrieve contest hacks for a specific contest.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve hacks as a contest manager (default is False).

        Returns
        -------
        list[codeforcespy.abc.objects.Hack]
            A list of hack objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_hacks(
            contest_id=contest_id, as_manager=as_manager
        )
        result = await self._execute_request(
            "contest.hacks",
            endpoint_url,
            codeforcespy.abc.interactions.ContestHacksResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Hack]", result)

    async def get_contest_list(
        self, of_gym: bool | None = False
    ) -> list[codeforcespy.abc.objects.Contest]:
        """
        Asynchronously retrieve a list of contests.

        Parameters
        ----------
        of_gym : bool | None, optional
            Whether to include gym contests (default is False).

        Returns
        -------
        list[codeforcespy.abc.objects.Contest]
            A list of contest objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_list(gym=of_gym)
        result = await self._execute_request(
            "contest.list",
            endpoint_url,
            codeforcespy.abc.interactions.ContestListResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Contest]", result)

    async def get_contest_rating_changes(
        self, contest_id: int
    ) -> list[codeforcespy.abc.objects.RatingChange]:
        """
        Asynchronously retrieve rating changes for a specific contest.

        Parameters
        ----------
        contest_id : int
            The contest ID.

        Returns
        -------
        list[codeforcespy.abc.objects.RatingChange]
            A list of rating change objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_rating_changes(
            contest_id=contest_id
        )
        result = await self._execute_request(
            "contest.ratingChanges",
            endpoint_url,
            codeforcespy.abc.interactions.ContestRatingChangeResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RatingChange]", result)

    async def get_contest_standings(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        from_index: int = 1,
        count: int = 5,
        show_unofficial: bool | None = True,
    ) -> list[codeforcespy.abc.cobjects.Standings]:
        """
        Asynchronously retrieve contest standings.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve standings as a contest manager (default is False).
        from_index : int, optional
            The starting index for standings (default is 1).
        count : int, optional
            The number of standings rows to retrieve (default is 5).
        show_unofficial : bool | None, optional
            Whether to show unofficial standings (default is True).

        Returns
        -------
        list[codeforcespy.abc.cobjects.Standings]
            A list of standings objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_standings(
            contest_id=contest_id,
            as_manager=as_manager,
            from_index=from_index,
            count=count,
            show_unofficial=show_unofficial,
        )
        result = await self._execute_request(
            "contest.standings",
            endpoint_url,
            codeforcespy.abc.interactions.ContestStandingResponse,
        )
        return typing.cast("list[codeforcespy.abc.cobjects.Standings]", result)

    async def get_contest_status(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        handle: str | None = None,
        from_index: int = 1,
        count: int = 10,
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Asynchronously retrieve contest submission status.

        Parameters
        ----------
        contest_id : int
            The contest ID.
        as_manager : bool | None, optional
            Whether to retrieve status as a contest manager (default is False).
        handle : str | None, optional
            The user handle to filter submissions (default is None).
        from_index : int, optional
            The starting index for submissions (default is 1).
        count : int, optional
            The number of submissions to retrieve (default is 10).

        Returns
        -------
        list[codeforcespy.abc.objects.Submission]
            A list of submission objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.contest_status(
            contest_id=contest_id,
            as_manager=as_manager,
            handle=handle,
            from_index=from_index,
            count=count,
        )
        result = await self._execute_request(
            "contest.status",
            endpoint_url,
            codeforcespy.abc.interactions.ContestStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)
