"""
👤 User Features Mixins.
===========================

Domain-specific logic for user-related API endpoints.

✨ Capabilities
-------------------
- 📋 User Info: Retrieve detailed user profiles and rankings.
- 📉 Ratings: Access user rating changes and history.
- 🚦 Status: Get user submissions and status updates.

📦 Classes
--------------
- `SyncUser`: Synchronous mixin for user operations.
- `AsyncUser`: Asynchronous mixin for user operations.

📝 Compliance
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import abc
import typing

import codeforcespy.abc.interactions
import codeforcespy.abc.objects
import codeforcespy.features.mixin_base


class SyncUser(codeforcespy.features.mixin_base.SyncFeatureMixin, abc.ABC):
    """Mixin for synchronous user-related operations."""

    def get_user(
        self, handles: str, check_historic_handles: bool | None = True
    ) -> list[codeforcespy.abc.objects.User]:
        """
        Retrieve user information for given handles.

        Parameters
        ----------
        handles : str
            Semicolon-separated list of user handles.
        check_historic_handles : bool | None, optional
            Whether to check historic handles (default is True).

        Returns
        -------
        list[codeforcespy.abc.objects.User]
            A list of user objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_info(
            handles=handles, check_historic_handles=check_historic_handles
        )
        result = self._execute_request(
            "user.info",
            endpoint_url,
            codeforcespy.abc.interactions.UserInteractionResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.User]", result)

    def get_user_blog_entries(
        self, handle: str
    ) -> list[codeforcespy.abc.objects.BlogEntry]:
        """
        Retrieve blog entries for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.

        Returns
        -------
        list[codeforcespy.abc.objects.BlogEntry]
            A list of blog entry objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_blog_entries(handle=handle)
        result = self._execute_request(
            "user.blogEntries",
            endpoint_url,
            codeforcespy.abc.interactions.UserBlogEntryResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.BlogEntry]", result)

    def get_user_friends(self, only_online: bool = True) -> list[str]:
        """
        Retrieve the friends list for the authenticated user.

        Parameters
        ----------
        only_online : bool, optional
            Whether to retrieve only online friends (default is True).

        Returns
        -------
        list[str]
            A list of friend handles.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_friends(only_online=only_online)
        result = self._execute_request(
            "user.friends",
            endpoint_url,
            codeforcespy.abc.interactions.UserFriendResponse,
        )
        return typing.cast("list[str]", result)

    def get_user_rated_list(
        self,
        active_only: bool | None = True,
        include_retired: bool | None = False,
        contest_id: int | None = None,
    ) -> list[codeforcespy.abc.objects.User]:
        """
        Retrieve the rated list of users.

        Parameters
        ----------
        active_only : bool | None, optional
            Whether to include only active users (default is True).
        include_retired : bool | None, optional
            Whether to include retired users (default is False).
        contest_id : int | None, optional
            Contest ID to filter the rated list (default is None).

        Returns
        -------
        list[codeforcespy.abc.objects.User]
            A list of user objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_rated_list(
            active_only=active_only,
            include_retired=include_retired,
            contest_id=contest_id,
        )
        result = self._execute_request(
            "user.ratedList",
            endpoint_url,
            codeforcespy.abc.interactions.UserRatedListResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.User]", result)

    def get_user_rating(
        self, handle: str
    ) -> list[codeforcespy.abc.objects.RatingChange]:
        """
        Retrieve the rating history for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.

        Returns
        -------
        list[codeforcespy.abc.objects.RatingChange]
            A list of rating change objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_rating(handle=handle)
        result = self._execute_request(
            "user.rating",
            endpoint_url,
            codeforcespy.abc.interactions.UserRatingResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RatingChange]", result)

    def get_user_status(
        self, handle: str, from_index: int = 1, count: int = 10
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Retrieve submission status for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.
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
        endpoint_url: str = self._url_generator.user_status(
            handle=handle, from_index=from_index, count=count
        )
        result = self._execute_request(
            "user.status",
            endpoint_url,
            codeforcespy.abc.interactions.UserStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)


class AsyncUser(codeforcespy.features.mixin_base.AsyncFeatureMixin, abc.ABC):
    """Mixin for asynchronous user-related operations."""

    async def get_user(
        self, handles: str, check_historic_handles: bool | None = True
    ) -> list[codeforcespy.abc.objects.User]:
        """
        Asynchronously retrieve user information for given handles.

        Parameters
        ----------
        handles : str
            Semicolon-separated list of user handles.
        check_historic_handles : bool | None, optional
            Whether to check historic handles (default is True).

        Returns
        -------
        list[codeforcespy.abc.objects.User]
            A list of user objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_info(
            handles=handles, check_historic_handles=check_historic_handles
        )
        result = await self._execute_request(
            "user.info",
            endpoint_url,
            codeforcespy.abc.interactions.UserInteractionResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.User]", result)

    async def get_user_blog_entries(
        self, handle: str
    ) -> list[codeforcespy.abc.objects.BlogEntry]:
        """
        Asynchronously retrieve blog entries for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.

        Returns
        -------
        list[codeforcespy.abc.objects.BlogEntry]
            A list of blog entry objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_blog_entries(handle=handle)
        result = await self._execute_request(
            "user.blogEntries",
            endpoint_url,
            codeforcespy.abc.interactions.UserBlogEntryResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.BlogEntry]", result)

    async def get_user_friends(self, only_online: bool = True) -> list[str]:
        """
        Asynchronously retrieve the friends list for the authenticated user.

        Parameters
        ----------
        only_online : bool, optional
            Whether to retrieve only online friends (default is True).

        Returns
        -------
        list[str]
            A list of friend handles.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_friends(only_online=only_online)
        result = await self._execute_request(
            "user.friends",
            endpoint_url,
            codeforcespy.abc.interactions.UserFriendResponse,
        )
        return typing.cast("list[str]", result)

    async def get_user_rated_list(
        self,
        active_only: bool | None = True,
        include_retired: bool | None = False,
        contest_id: int | None = None,
    ) -> list[codeforcespy.abc.objects.User]:
        """
        Asynchronously retrieve the rated list of users.

        Parameters
        ----------
        active_only : bool | None, optional
            Whether to include only active users (default is True).
        include_retired : bool | None, optional
            Whether to include retired users (default is False).
        contest_id : int | None, optional
            Contest ID to filter the rated list (default is None).

        Returns
        -------
        list[codeforcespy.abc.objects.User]
            A list of user objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_rated_list(
            active_only=active_only,
            include_retired=include_retired,
            contest_id=contest_id,
        )
        result = await self._execute_request(
            "user.ratedList",
            endpoint_url,
            codeforcespy.abc.interactions.UserRatedListResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.User]", result)

    async def get_user_rating(
        self, handle: str
    ) -> list[codeforcespy.abc.objects.RatingChange]:
        """
        Asynchronously retrieve the rating history for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.

        Returns
        -------
        list[codeforcespy.abc.objects.RatingChange]
            A list of rating change objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.user_rating(handle=handle)
        result = await self._execute_request(
            "user.rating",
            endpoint_url,
            codeforcespy.abc.interactions.UserRatingResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.RatingChange]", result)

    async def get_user_status(
        self, handle: str, from_index: int = 1, count: int = 10
    ) -> list[codeforcespy.abc.objects.Submission]:
        """
        Asynchronously retrieve submission status for a specific user.

        Parameters
        ----------
        handle : str
            The Codeforces user handle.
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
        endpoint_url: str = self._url_generator.user_status(
            handle=handle, from_index=from_index, count=count
        )
        result = await self._execute_request(
            "user.status",
            endpoint_url,
            codeforcespy.abc.interactions.UserStatusResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Submission]", result)
