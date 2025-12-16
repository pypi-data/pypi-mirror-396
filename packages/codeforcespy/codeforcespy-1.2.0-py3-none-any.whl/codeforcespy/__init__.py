"""
📦 codeforcespy.
==================

A high-performance, type-safe, and asynchronous wrapper for the Codeforces API.
Designed for competitive programmers and developers who demand reliability.

✨ Highlights
-----------------
- 🚀 Sync & Async: First-class support for both synchronous and asynchronous usage.
- 🔒 Type Safe: 100% type annotations with strict `basedpyright` compliance.
- 🛡️ Robust: Comprehensive error handling and response validation.

📝 License
--------------
MIT License. Copyright (c) 2024 Xsyncio.
"""

import codeforcespy.abc.cobjects
import codeforcespy.abc.endpoints
import codeforcespy.abc.interactions
import codeforcespy.abc.objects
import codeforcespy.clients
import codeforcespy.errors

__version__ = "1.2.0"

# Re-export public API using proper namespace access
ProblemSetProblems = codeforcespy.abc.cobjects.ProblemSetProblems
Standings = codeforcespy.abc.cobjects.Standings
CodeForcesAPI = codeforcespy.abc.endpoints.CodeForcesAPI
BlogEntryCommentResponse = codeforcespy.abc.interactions.BlogEntryCommentResponse
BlogEntryViewResponse = codeforcespy.abc.interactions.BlogEntryViewResponse
ContestHacksResponse = codeforcespy.abc.interactions.ContestHacksResponse
ContestListResponse = codeforcespy.abc.interactions.ContestListResponse
ContestRatingChangeResponse = codeforcespy.abc.interactions.ContestRatingChangeResponse
ContestStandingResponse = codeforcespy.abc.interactions.ContestStandingResponse
ContestStatusResponse = codeforcespy.abc.interactions.ContestStatusResponse
ProblemSetProblemsResponse = codeforcespy.abc.interactions.ProblemSetProblemsResponse
ProblemSetRecentStatusResponse = (
    codeforcespy.abc.interactions.ProblemSetRecentStatusResponse
)
RecentActionsResponse = codeforcespy.abc.interactions.RecentActionsResponse
UserBlogEntryResponse = codeforcespy.abc.interactions.UserBlogEntryResponse
UserFriendResponse = codeforcespy.abc.interactions.UserFriendResponse
UserInteractionResponse = codeforcespy.abc.interactions.UserInteractionResponse
UserRatedListResponse = codeforcespy.abc.interactions.UserRatedListResponse
UserRatingResponse = codeforcespy.abc.interactions.UserRatingResponse
UserStatusResponse = codeforcespy.abc.interactions.UserStatusResponse
BlogEntry = codeforcespy.abc.objects.BlogEntry
Comment = codeforcespy.abc.objects.Comment
Contest = codeforcespy.abc.objects.Contest
Hack = codeforcespy.abc.objects.Hack
Problem = codeforcespy.abc.objects.Problem
ProblemResult = codeforcespy.abc.objects.ProblemResult
RatingChange = codeforcespy.abc.objects.RatingChange
RecentAction = codeforcespy.abc.objects.RecentAction
Submission = codeforcespy.abc.objects.Submission
User = codeforcespy.abc.objects.User
AsyncClient = codeforcespy.clients.AsyncClient
SyncClient = codeforcespy.clients.SyncClient
CodeforcesPyError = codeforcespy.errors.CodeforcesPyError
APIError = codeforcespy.errors.APIError

__all__ = [
    "APIError",
    "AsyncClient",
    "BlogEntry",
    "BlogEntryCommentResponse",
    "BlogEntryViewResponse",
    "CodeForcesAPI",
    "CodeforcesPyError",
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
