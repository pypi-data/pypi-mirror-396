"""
🧩 ABC Package Initialization.
=================================

Exports abstract base classes and interaction models for easy access.

✨ Purpose
--------------
- 📥 Centralized Access: Unified import point for all core types and models.
- 🧹 Clean Namespace: Organized re-exports to avoid clutter.

📦 Exports
--------------
- `CodeForcesAPI`: Endpoint logic.
- `User`, `Contest`, `Problem`, etc.: API Data models.
- `SyncProtocol`, `AsyncProtocol`: Interaction protocols.

📝 Compliance
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

from . import cobjects
from . import endpoints
from . import interactions
from . import objects

# Re-export public API using proper namespace access
ProblemSetProblems = cobjects.ProblemSetProblems
Standings = cobjects.Standings
CodeForcesAPI = endpoints.CodeForcesAPI
BlogEntryCommentResponse = interactions.BlogEntryCommentResponse
BlogEntryViewResponse = interactions.BlogEntryViewResponse
ContestHacksResponse = interactions.ContestHacksResponse
ContestListResponse = interactions.ContestListResponse
ContestRatingChangeResponse = interactions.ContestRatingChangeResponse
ContestStandingResponse = interactions.ContestStandingResponse
ContestStatusResponse = interactions.ContestStatusResponse
ProblemSetProblemsResponse = interactions.ProblemSetProblemsResponse
ProblemSetRecentStatusResponse = interactions.ProblemSetRecentStatusResponse
RecentActionsResponse = interactions.RecentActionsResponse
UserBlogEntryResponse = interactions.UserBlogEntryResponse
UserFriendResponse = interactions.UserFriendResponse
UserInteractionResponse = interactions.UserInteractionResponse
UserRatedListResponse = interactions.UserRatedListResponse
UserRatingResponse = interactions.UserRatingResponse
UserStatusResponse = interactions.UserStatusResponse
BlogEntry = objects.BlogEntry
Comment = objects.Comment
Contest = objects.Contest
Hack = objects.Hack
RatingChange = objects.RatingChange
RecentAction = objects.RecentAction
Submission = objects.Submission
User = objects.User

__all__ = [
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
    "ProblemSetProblems",
    "ProblemSetProblemsResponse",
    "ProblemSetRecentStatusResponse",
    "RatingChange",
    "RecentAction",
    "RecentActionsResponse",
    "Standings",
    "Submission",
    "User",
    "UserBlogEntryResponse",
    "UserFriendResponse",
    "UserInteractionResponse",
    "UserRatedListResponse",
    "UserRatingResponse",
    "UserStatusResponse",
]
