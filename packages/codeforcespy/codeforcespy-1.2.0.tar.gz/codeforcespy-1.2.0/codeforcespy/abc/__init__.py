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

import codeforcespy.abc.cobjects
import codeforcespy.abc.endpoints
import codeforcespy.abc.interactions
import codeforcespy.abc.objects

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
RatingChange = codeforcespy.abc.objects.RatingChange
RecentAction = codeforcespy.abc.objects.RecentAction
Submission = codeforcespy.abc.objects.Submission
User = codeforcespy.abc.objects.User

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
