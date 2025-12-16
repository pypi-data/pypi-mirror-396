"""
📰 Blog Features Mixins.
===========================

Domain-specific logic for blog-related API endpoints.

✨ Capabilities
-------------------
- 📝 Entries: Retrieve blog entries and content.
- 💬 Comments: Access comments associated with blog entries.
- 🔍 View: Get specific blog entry details.

📦 Classes
--------------
- `SyncBlog`: Synchronous mixin for blog operations.
- `AsyncBlog`: Asynchronous mixin for blog operations.

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


class SyncBlog(codeforcespy.features.mixin_base.SyncFeatureMixin, abc.ABC):
    """Mixin for synchronous blog-related operations."""

    def get_blog_entry_comments(
        self, blog_entry_id: int
    ) -> list[codeforcespy.abc.objects.Comment]:
        """
        Retrieve comments for a specific blog entry.

        Parameters
        ----------
        blog_entry_id : int
            The blog entry ID.

        Returns
        -------
        list[codeforcespy.abc.objects.Comment]
            A list of comment objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.blog_entry_comments(
            blog_entry_id=blog_entry_id
        )
        result = self._execute_request(
            "blogEntry.comments",
            endpoint_url,
            codeforcespy.abc.interactions.BlogEntryCommentResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Comment]", result)

    def get_blog_entry_view(
        self, blog_entry_id: int
    ) -> list[codeforcespy.abc.objects.BlogEntry]:
        """
        Retrieve a blog entry view.

        Parameters
        ----------
        blog_entry_id : int
            The blog entry ID.

        Returns
        -------
        list[codeforcespy.abc.objects.BlogEntry]
            A list of blog entry objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.blog_entry_view(
            blog_entry_id=blog_entry_id
        )
        result = self._execute_request(
            "blogEntry.view",
            endpoint_url,
            codeforcespy.abc.interactions.BlogEntryViewResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.BlogEntry]", result)


class AsyncBlog(codeforcespy.features.mixin_base.AsyncFeatureMixin, abc.ABC):
    """Mixin for asynchronous blog-related operations."""

    async def get_blog_entry_comments(
        self, blog_entry_id: int
    ) -> list[codeforcespy.abc.objects.Comment]:
        """
        Asynchronously retrieve comments for a specific blog entry.

        Parameters
        ----------
        blog_entry_id : int
            The blog entry ID.

        Returns
        -------
        list[codeforcespy.abc.objects.Comment]
            A list of comment objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.blog_entry_comments(
            blog_entry_id=blog_entry_id
        )
        result = await self._execute_request(
            "blogEntry.comments",
            endpoint_url,
            codeforcespy.abc.interactions.BlogEntryCommentResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.Comment]", result)

    async def get_blog_entry_view(
        self, blog_entry_id: int
    ) -> list[codeforcespy.abc.objects.BlogEntry]:
        """
        Asynchronously retrieve a blog entry view.

        Parameters
        ----------
        blog_entry_id : int
            The blog entry ID.

        Returns
        -------
        list[codeforcespy.abc.objects.BlogEntry]
            A list of blog entry objects.

        Raises
        ------
        codeforcespy.errors.APIError
            If the API response indicates a failure.
        """
        endpoint_url: str = self._url_generator.blog_entry_view(
            blog_entry_id=blog_entry_id
        )
        result = await self._execute_request(
            "blogEntry.view",
            endpoint_url,
            codeforcespy.abc.interactions.BlogEntryViewResponse,
        )
        return typing.cast("list[codeforcespy.abc.objects.BlogEntry]", result)
