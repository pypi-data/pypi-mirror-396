"""
📦 **codeforcespy**.
==================

A high-performance, type-safe, and asynchronous wrapper for the Codeforces API.
Designed for competitive programmers and developers who demand reliability.

✨ **Highlights**
-----------------
- 🚀 **Sync & Async**: First-class support for both synchronous and asynchronous usage.
- 🔒 **Type Safe**: 100% type annotations with strict `basedpyright` compliance.
- 🛡️ **Robust**: Comprehensive error handling and response validation.

📝 **License**
--------------
MIT License. Copyright (c) 2024 Xsyncio.
"""

from codeforcespy.abc.cobjects import ProblemSetProblems
from codeforcespy.abc.cobjects import Standings
from codeforcespy.abc.endpoints import CodeForcesAPI
from codeforcespy.abc.interactions import BlogEntryCommentResponse
from codeforcespy.abc.interactions import BlogEntryViewResponse
from codeforcespy.abc.interactions import ContestHacksResponse
from codeforcespy.abc.interactions import ContestListResponse
from codeforcespy.abc.interactions import ContestRatingChangeResponse
from codeforcespy.abc.interactions import ContestStandingResponse
from codeforcespy.abc.interactions import ContestStatusResponse
from codeforcespy.abc.interactions import ProblemSetProblemsResponse
from codeforcespy.abc.interactions import ProblemSetRecentStatusResponse
from codeforcespy.abc.interactions import RecentActionsResponse
from codeforcespy.abc.interactions import UserBlogEntryResponse
from codeforcespy.abc.interactions import UserFriendResponse
from codeforcespy.abc.interactions import UserInteractionResponse
from codeforcespy.abc.interactions import UserRatedListResponse
from codeforcespy.abc.interactions import UserRatingResponse
from codeforcespy.abc.interactions import UserStatusResponse
from codeforcespy.abc.objects import BlogEntry
from codeforcespy.abc.objects import Comment
from codeforcespy.abc.objects import Contest
from codeforcespy.abc.objects import Hack
from codeforcespy.abc.objects import Problem
from codeforcespy.abc.objects import ProblemResult
from codeforcespy.abc.objects import RatingChange
from codeforcespy.abc.objects import RecentAction
from codeforcespy.abc.objects import Submission
from codeforcespy.abc.objects import User
from codeforcespy.clients import AsyncClient
from codeforcespy.clients import SyncClient

__version__ = "1.1.0"

__all__ = [
    "AsyncClient",
    "BlogEntry",
    "BlogEntryCommentResponse",
    "BlogEntryViewResponse",
    "CodeForcesAPI",
    "Comment",
    "Contest",
    "ContestHacksResponse",
    "ContestListResponse",
    "ContestRatingChangeResponse",
    "ContestStandingResponse",
    "ContestStatusResponse",
    "Hack",
    "Problem",
    "ProblemResult",
    "ProblemSetProblems",
    "ProblemSetProblemsResponse",
    "ProblemSetRecentStatusResponse",
    "RatingChange",
    "RecentAction",
    "RecentActionsResponse",
    "Standings",
    "Submission",
    "SyncClient",
    "User",
    "UserBlogEntryResponse",
    "UserFriendResponse",
    "UserInteractionResponse",
    "UserRatedListResponse",
    "UserRatingResponse",
    "UserStatusResponse",
]
