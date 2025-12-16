"""
🔗 **API Endpoints Definitions**.
================================

Defines the structure and generation logic for Codeforces API endpoints.

✨ **Capabilities**
-------------------
- 🛤️ **Route Generation**: Dynamically constructs API URLs.
- 🔧 **Parameter Handling**: Manages query parameters for endpoints.

📦 **Classes**
--------------
- `CodeForcesAPI`: Main endpoint generator.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""


class CodeForcesAPI:
    """
    A class to generate URL endpoints for the Codeforces API.

    Attributes
    ----------
    base_url : str
        The base URL for the Codeforces API.

    Examples
    --------
    >>> api = CodeForcesAPI()
    >>> api.blog_entry_comments(123)
    'https://codeforces.com/api/blogEntry.comments?blogEntryId=123'
    """

    def __init__(self) -> None:
        """Initialize the CodeForcesAPI instance with the base API URL."""
        self.base_url: str = "https://codeforces.com/api"

    def blog_entry_comments(self, blog_entry_id: int) -> str:
        """
        Generate URL endpoint to retrieve comments for a specific blog entry.

        Parameters
        ----------
        blog_entry_id : int
            The ID of the blog entry.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.blog_entry_comments(123)
        'https://codeforces.com/api/blogEntry.comments?blogEntryId=123'
        """
        return f"{self.base_url}/blogEntry.comments?blogEntryId={blog_entry_id}"

    def blog_entry_view(self, blog_entry_id: int) -> str:
        """
        Generate URL endpoint to retrieve a specific blog entry.

        Parameters
        ----------
        blog_entry_id : int
            The ID of the blog entry.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.blog_entry_view(123)
        'https://codeforces.com/api/blogEntry.view?blogEntryId=123'
        """
        return f"{self.base_url}/blogEntry.view?blogEntryId={blog_entry_id}"

    def contest_hacks(self, contest_id: int, as_manager: bool | None = False) -> str:
        """
        Generate URL endpoint to retrieve hacks for a specific contest.

        Parameters
        ----------
        contest_id : int
            The ID of the contest.
        as_manager : bool | None, default False
            Flag indicating if the request is made by a contest manager.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.contest_hacks(456, True)
        'https://codeforces.com/api/contest.hacks?contestId=456&asManager=True'
        """
        return f"{self.base_url}/contest.hacks?contestId={contest_id}&asManager={as_manager}"

    def contest_list(self, gym: bool | None = False) -> str:
        """
        Generate URL endpoint to retrieve information about all available contests.

        Parameters
        ----------
        gym : bool | None, default False
            Flag indicating if gym contests should be returned.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.contest_list(gym=True)
        'https://codeforces.com/api/contest.list?gym=True'
        """
        return f"{self.base_url}/contest.list?gym={gym}"

    def contest_rating_changes(self, contest_id: int) -> str:
        """
        Generate URL endpoint to retrieve rating changes after a contest.

        Parameters
        ----------
        contest_id : int
            The ID of the contest.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.contest_rating_changes(789)
        'https://codeforces.com/api/contest.ratingChanges?contestId=789'
        """
        return f"{self.base_url}/contest.ratingChanges?contestId={contest_id}"

    def contest_standings(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        from_index: int = 1,
        count: int = 5,
        show_unofficial: bool | None = True,
    ) -> str:
        """
        Generate URL endpoint to retrieve contest standings and details.

        Parameters
        ----------
        contest_id : int
            The ID of the contest.
        as_manager : bool | None, default False
            Flag indicating if the request is made by a contest manager.
        from_index : int, default 1
            1-based index of the standings row to start the ranklist.
        count : int, default 5
            Number of standing rows to return.
        show_unofficial : bool | None, default True
            Flag indicating if unofficial contestants should be shown.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.contest_standings(101, from_index=1, count=10)
        'https://codeforces.com/api/contest.standings?contestId=101&asManager=False&from=1&count=10&showUnofficial=True'
        """
        return (
            f"{self.base_url}/contest.standings?contestId={contest_id}&asManager={as_manager}"
            f"&from={from_index}&count={count}&showUnofficial={show_unofficial}"
        )

    def contest_status(
        self,
        contest_id: int,
        as_manager: bool | None = False,
        handle: str | None = None,
        from_index: int = 1,
        count: int = 10,
    ) -> str:
        """
        Generate URL endpoint to retrieve contest submissions.

        Parameters
        ----------
        contest_id : int
            The ID of the contest.
        as_manager : bool | None, default False
            Flag indicating if the request is made by a contest manager.
        handle : str | None, default None
            Codeforces user handle.
        from_index : int, default 1
            1-based index of the first submission to return.
        count : int, default 10
            Number of submissions to return.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.contest_status(202, handle="user123")
        'https://codeforces.com/api/contest.status?contestId=202&asManager=False&handle=user123&from=1&count=10'
        """
        if handle:
            return (
                f"{self.base_url}/contest.status?contestId={contest_id}&asManager={as_manager}"
                f"&handle={handle}&from={from_index}&count={count}"
            )
        else:
            return f"{self.base_url}/contest.status?contestId={contest_id}&asManager={as_manager}&from={from_index}&count={count}"

    def problemset_problems(
        self,
        tags: str | None = None,
        problemset_name: str | None = None,
    ) -> str:
        """
        Generate URL endpoint to retrieve problems from the problemset.

        Parameters
        ----------
        tags : str | None, default None
            Semicolon-separated list of tags.
        problemset_name : str | None, default None
            Custom problemset's short name.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.problemset_problems(tags="dp;graphs")
        'https://codeforces.com/api/problemset.problems?tags=dp;graphs'
        """
        if tags:
            return f"{self.base_url}/problemset.problems?tags={tags}"
        elif problemset_name:
            return (
                f"{self.base_url}/problemset.problems?problemsetName={problemset_name}"
            )
        else:
            return f"{self.base_url}/problemset.problems"

    def problemset_recent_status(
        self,
        count: int,
        problemset_name: str | None = None,
    ) -> str:
        """
        Generate URL endpoint to retrieve recent submissions from the problemset.

        Parameters
        ----------
        count : int
            Number of submissions to return.
        problemset_name : str | None, default None
            Custom problemset's short name.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.problemset_recent_status(5)
        'https://codeforces.com/api/problemset.recentStatus?count=5'
        """
        if problemset_name:
            return f"{self.base_url}/problemset.recentStatus?count={count}&problemsetName={problemset_name}"
        else:
            return f"{self.base_url}/problemset.recentStatus?count={count}"

    def recent_actions(self, max_count: int) -> str:
        """
        Generate URL endpoint to retrieve recent actions.

        Parameters
        ----------
        max_count : int
            Number of recent actions to return.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.recent_actions(20)
        'https://codeforces.com/api/recentActions?maxCount=20'
        """
        return f"{self.base_url}/recentActions?maxCount={max_count}"

    def user_blog_entries(self, handle: str) -> str:
        """
        Generate URL endpoint to retrieve a user's blog entries.

        Parameters
        ----------
        handle : str
            Codeforces user handle.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_blog_entries("user123")
        'https://codeforces.com/api/user.blogEntries?handle=user123'
        """
        return f"{self.base_url}/user.blogEntries?handle={handle}"

    def user_friends(self, only_online: bool | None = False) -> str:
        """
        Generate URL endpoint to retrieve the authorized user's friends list.

        Parameters
        ----------
        only_online : bool | None, default False
            Flag indicating if only online friends should be returned.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_friends(True)
        'https://codeforces.com/api/user.friends?onlyOnline=True'
        """
        return f"{self.base_url}/user.friends?onlyOnline={only_online}"

    def user_info(
        self,
        handles: str,
        check_historic_handles: bool | None = True,
    ) -> str:
        """
        Generate URL endpoint to retrieve information about one or several users.

        Parameters
        ----------
        handles : str
            Semicolon-separated list of user handles.
        check_historic_handles : bool | None, default True
            Flag indicating if historical handles should be checked.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_info("user1;user2")
        'https://codeforces.com/api/user.info?handles=user1;user2&checkHistoricHandles=True'
        """
        return f"{self.base_url}/user.info?handles={handles}&checkHistoricHandles={check_historic_handles}"

    def user_rated_list(
        self,
        active_only: bool | None = True,
        include_retired: bool | None = False,
        contest_id: int | None = None,
    ) -> str:
        """
        Generate URL endpoint to retrieve the list of rated users.

        Parameters
        ----------
        active_only : bool | None, default True
            Flag indicating if only active users should be returned.
        include_retired : bool | None, default False
            Flag indicating if retired users should be included.
        contest_id : int | None, default None
            Contest ID to filter the rated users.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_rated_list(active_only=False, contest_id=100)
        'https://codeforces.com/api/user.ratedList?activeOnly=False&includeRetired=False&contestId=100'
        """
        if contest_id is not None:
            return (
                f"{self.base_url}/user.ratedList?activeOnly={active_only}"
                f"&includeRetired={include_retired}&contestId={contest_id}"
            )
        else:
            return f"{self.base_url}/user.ratedList?activeOnly={active_only}&includeRetired={include_retired}"

    def user_rating(self, handle: str) -> str:
        """
        Generate URL endpoint to retrieve a user's rating history.

        Parameters
        ----------
        handle : str
            Codeforces user handle.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_rating("user123")
        'https://codeforces.com/api/user.rating?handle=user123'
        """
        return f"{self.base_url}/user.rating?handle={handle}"

    def user_status(self, handle: str, from_index: int = 1, count: int = 10) -> str:
        """
        Generate URL endpoint to retrieve submissions of a specified user.

        Parameters
        ----------
        handle : str
            Codeforces user handle.
        from_index : int, default 1
            1-based index of the first submission to return.
        count : int, default 10
            Number of submissions to return.

        Returns
        -------
        str
            The generated URL endpoint.

        Examples
        --------
        >>> api = CodeForcesAPI()
        >>> api.user_status("user123", from_index=1, count=15)
        'https://codeforces.com/api/user.status?handle=user123&from=1&count=15'
        """
        return f"{self.base_url}/user.status?handle={handle}&from={from_index}&count={count}"
