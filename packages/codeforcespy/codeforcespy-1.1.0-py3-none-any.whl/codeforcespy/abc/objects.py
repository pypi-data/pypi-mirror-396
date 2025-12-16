"""
📦 **Data Models (msgspec Structs)**.
====================================

msgspec definitions representing Codeforces API response objects.

✨ **Features**
--------------
- 🛡️ **Validation**: Strict runtime type checking and validation.
- 🏗️ **Structure**: Clear object definitions for Users, Contests, Problems, etc.

📦 **Classes**
--------------
- `User`: Represents a Codeforces user.
- `Member`: Represents a member of a party.
- `BlogEntry`: Represents a Codeforces blog entry.
- `Comment`: Represents a comment.
- `RecentAction`: Represents a recent action.
- `RatingChange`: Represents a user's rating change after a contest.
- `Contest`: Represents a contest.
- `Party`: Represents a party participating in a contest.
- `Problem`: Represents a problem.
- `ProblemStatistics`: Represents statistics data for a problem.
- `Submission`: Represents a submission.
- `Hack`: Represents a hack attempt during a contest.
- `ProblemResult`: Represents a party's result for a specific problem.
- `RankListRow`: Represents a row in the contest ranklist.

📝 **Compliance**
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""

import msgspec


class User(msgspec.Struct):
    """
    Represents a Codeforces user.

    Attributes
    ----------
    handle : str | None
        Codeforces user handle.
    vkId : str | None
        User ID for the VK social network (if shared).
    openId : str | None
        OpenID identifier (if shared).
    firstName : str | None
        Localized first name of the user.
    lastName : str | None
        Localized last name of the user.
    country : str | None
        Localized country of the user.
    city : str | None
        Localized city of the user.
    organization : str | None
        Localized organization of the user.
    contribution : int | None
        User's contribution to the Codeforces community.
    rank : str | None
        Localized rank of the user.
    rating : int | None
        User's rating in the Codeforces community.
    maxRank : str | None
        Localized maximum rank achieved by the user.
    maxRating : int | None
        Maximum rating achieved by the user.
    lastOnlineTimeSeconds : int | None
        Unix timestamp indicating when the user was last online.
    registrationTimeSeconds : int | None
        Unix timestamp of the user's registration.
    friendOfCount : int | None
        Number of users who have this user in their friends list.
    avatar : str | None
        URL of the user's avatar.
    titlePhoto : str | None
        URL of the user's title photo.
    email : str | None
        Email address (shared if permitted).
    """

    handle: str | None = None
    vkId: str | None = None
    openId: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    country: str | None = None
    city: str | None = None
    organization: str | None = None
    contribution: int | None = None
    rank: str | None = None
    rating: int | None = None
    maxRank: str | None = None
    maxRating: int | None = None
    lastOnlineTimeSeconds: int | None = None
    registrationTimeSeconds: int | None = None
    friendOfCount: int | None = None
    avatar: str | None = None
    titlePhoto: str | None = None
    email: str | None = None


class Member(msgspec.Struct):
    """
    Represents a member of a party.

    Attributes
    ----------
    handle : str
        Codeforces user handle.
    name : str | None
        User's name (if available).
    """

    handle: str
    name: str | None = None


class BlogEntry(msgspec.Struct):
    """
    Represents a Codeforces blog entry.

    Attributes
    ----------
    id : int | None
        Unique identifier for the blog entry.
    originalLocale : str | None
        Original locale of the blog entry.
    creationTimeSeconds : int | None
        Unix timestamp when the blog entry was created.
    authorHandle : str | None
        User handle of the blog entry author.
    title : str | None
        Localized title of the blog entry.
    content : str | None
        Localized content of the blog entry (omitted in the short version).
    locale : str | None
        Locale of the blog entry.
    modificationTimeSeconds : int | None
        Unix timestamp when the blog entry was last modified.
    allowViewHistory : bool | None
        Indicates if viewing the history of the blog entry is permitted.
    tags : list[str] | None
        List of tags associated with the blog entry.
    rating : int | None
        Rating of the blog entry.
    """

    id: int | None = None
    originalLocale: str | None = None
    creationTimeSeconds: int | None = None
    authorHandle: str | None = None
    title: str | None = None
    content: str | None = None
    locale: str | None = None
    modificationTimeSeconds: int | None = None
    allowViewHistory: bool | None = None
    tags: list[str] | None = None
    rating: int | None = None


class Comment(msgspec.Struct):
    """
    Represents a comment on Codeforces.

    Attributes
    ----------
    id : int | None
        Unique identifier for the comment.
    creationTimeSeconds : int | None
        Unix timestamp when the comment was created.
    commentatorHandle : str | None
        Handle of the user who posted the comment.
    locale : str | None
        Locale of the comment.
    text : str | None
        Text content of the comment.
    parentCommentId : int | None
        Identifier of the parent comment (if any).
    rating : int | None
        Rating of the comment.
    """

    id: int | None = None
    creationTimeSeconds: int | None = None
    commentatorHandle: str | None = None
    locale: str | None = None
    text: str | None = None
    parentCommentId: int | None = None
    rating: int | None = None


class RecentAction(msgspec.Struct):
    """
    Represents a recent action on Codeforces.

    Attributes
    ----------
    timeSeconds : int | None
        Unix timestamp of the action.
    blogEntry : BlogEntry | None
        Associated blog entry (short version), if applicable.
    comment : Comment | None
        Associated comment, if applicable.
    """

    timeSeconds: int | None = None
    blogEntry: BlogEntry | None = None
    comment: Comment | None = None


class RatingChange(msgspec.Struct):
    """
    Represents a user's rating change after participating in a contest.

    Attributes
    ----------
    contestId : int | None
        Identifier of the contest.
    contestName : str | None
        Localized name of the contest.
    handle : str | None
        Codeforces user handle.
    rank : int | None
        User's rank during the contest.
    ratingUpdateTimeSeconds : int | None
        Unix timestamp when the rating was updated.
    oldRating : int | None
        User's rating before the contest.
    newRating : int | None
        User's rating after the contest.
    """

    contestId: int | None = None
    contestName: str | None = None
    handle: str | None = None
    rank: int | None = None
    ratingUpdateTimeSeconds: int | None = None
    oldRating: int | None = None
    newRating: int | None = None


class Contest(msgspec.Struct):
    """
    Represents a contest on Codeforces.

    Attributes
    ----------
    id : int | None
        Contest identifier.
    name : str | None
        Localized name of the contest.
    type : str | None
        Contest type (e.g., 'CF', 'IOI', 'ICPC').
    phase : str | None
        Current contest phase (e.g., 'BEFORE', 'CODING', 'FINISHED').
    frozen : bool | None
        Indicates if the contest ranklist is frozen.
    durationSeconds : int | None
        Contest duration in seconds.
    startTimeSeconds : int | None
        Unix timestamp of the contest start.
    relativeTimeSeconds : int | None
        Seconds elapsed since the contest start (may be negative).
    preparedBy : str | None
        Handle of the contest creator.
    websiteUrl : str | None
        URL of the contest-related website.
    description : str | None
        Localized description of the contest.
    difficulty : int | None
        Difficulty rating (scale from 1 to 5).
    kind : str | None
        Localized, human-readable contest type.
    icpcRegion : str | None
        Localized region name for official ICPC contests.
    country : str | None
        Localized country name.
    city : str | None
        Localized city name.
    season : str | None
        Contest season.
    """

    id: int | None = None
    name: str | None = None
    type: str | None = None
    phase: str | None = None
    frozen: bool | None = None
    durationSeconds: int | None = None
    startTimeSeconds: int | None = None
    relativeTimeSeconds: int | None = None
    preparedBy: str | None = None
    websiteUrl: str | None = None
    description: str | None = None
    difficulty: int | None = None
    kind: str | None = None
    icpcRegion: str | None = None
    country: str | None = None
    city: str | None = None
    season: str | None = None


class Party(msgspec.Struct):
    """
    Represents a party participating in a contest.

    Attributes
    ----------
    contestId : int | None
        Identifier of the contest (if applicable).
    members : list[Member] | None
        List of party members.
    participantType : str | None
        Participant type (e.g., 'CONTESTANT', 'PRACTICE', 'VIRTUAL').
    teamId : int | None
        Unique team identifier (if the party is a team).
    teamName : str | None
        Localized team name (if the party is a team or ghost).
    ghost : bool | None
        Indicates if the party is a ghost (participated off Codeforces).
    room : int | None
        Room number (if assigned).
    startTimeSeconds : int | None
        Unix timestamp when the party started the contest.
    """

    contestId: int | None = None
    members: list[Member] | None = None
    participantType: str | None = None
    teamId: int | None = None
    teamName: str | None = None
    ghost: bool | None = None
    room: int | None = None
    startTimeSeconds: int | None = None


class Problem(msgspec.Struct):
    """
    Represents a problem on Codeforces.

    Attributes
    ----------
    contestId : int | None
        Identifier of the contest containing the problem.
    problemsetName : str | None
        Short name of the problemset to which the problem belongs.
    index : str | None
        Problem index (typically a letter or letter-number combination).
    name : str | None
        Localized name of the problem.
    type : str | None
        Problem type (e.g., 'PROGRAMMING', 'QUESTION').
    points : float | None
        Maximum points achievable for the problem.
    rating : int | None
        Difficulty rating of the problem.
    tags : list[str] | None
        List of tags associated with the problem.
    """

    contestId: int | None = None
    problemsetName: str | None = None
    index: str | None = None
    name: str | None = None
    type: str | None = None
    points: float | None = None
    rating: int | None = None
    tags: list[str] | None = None


class ProblemStatistics(msgspec.Struct):
    """
    Represents statistical data for a problem.

    Attributes
    ----------
    contestId : int | None
        Identifier of the contest containing the problem.
    index : str | None
        Problem index (typically a letter or letter-number combination).
    solvedCount : int | None
        Number of users who solved the problem.
    """

    contestId: int | None = None
    index: str | None = None
    solvedCount: int | None = None


class Submission(msgspec.Struct):
    """
    Represents a submission made on Codeforces.

    Attributes
    ----------
    id : int
        Unique identifier for the submission.
    contestId : int | None
        Identifier of the contest (if applicable).
    creationTimeSeconds : int | None
        Unix timestamp when the submission was created.
    relativeTimeSeconds : int | None
        Seconds elapsed from contest start to the submission.
    problem : Problem | None
        Problem associated with the submission.
    author : Party | None
        Party that made the submission.
    programmingLanguage : str | None
        Programming language used for the submission.
    verdict : str | None
        Verdict of the submission (e.g., 'OK', 'WRONG_ANSWER').
    testset : str | None
        Testset used for judging (e.g., 'SAMPLES', 'PRETESTS').
    passedTestCount : int | None
        Number of tests passed.
    timeConsumedMillis : int | None
        Time consumed (in milliseconds) for one test.
    memoryConsumedBytes : int | None
        Memory consumed (in bytes) for one test.
    points : float | None
        Points scored (for IOI-like contests).
    """

    id: int
    contestId: int | None = None
    creationTimeSeconds: int | None = None
    relativeTimeSeconds: int | None = None
    problem: Problem | None = None
    author: Party | None = None
    programmingLanguage: str | None = None
    verdict: str | None = None
    testset: str | None = None
    passedTestCount: int | None = None
    timeConsumedMillis: int | None = None
    memoryConsumedBytes: int | None = None
    points: float | None = None


class Hack(msgspec.Struct):
    """
    Represents a hack attempt during a Codeforces contest.

    Attributes
    ----------
    id : int
        Unique identifier for the hack.
    creationTimeSeconds : int
        Unix timestamp when the hack was created.
    hacker : Party | None
        Party that initiated the hack.
    defender : Party | None
        Party that was defended against.
    verdict : str | None
        Hack verdict (e.g., 'HACK_SUCCESSFUL', 'HACK_UNSUCCESSFUL').
    problem : Problem | None
        Problem that was hacked.
    test : str | None
        Test case details (if available).
    judgeProtocol : dict[str, str] | None
        Judge protocol details including keys such as 'manual', 'protocol', and 'verdict'.
    """

    id: int
    creationTimeSeconds: int
    hacker: Party | None = None
    defender: Party | None = None
    verdict: str | None = None
    problem: Problem | None = None
    test: str | None = None
    judgeProtocol: dict[str, str] | None = None


class ProblemResult(msgspec.Struct):
    """
    Represents a party's result for a specific problem.

    Attributes
    ----------
    points : float | None
        Points scored for the problem.
    penalty : int | None
        Penalty incurred (in ICPC style) for the problem.
    rejectedAttemptCount : int | None
        Number of incorrect submission attempts.
    type : str | None
        Result type (e.g., 'PRELIMINARY', 'FINAL').
    bestSubmissionTimeSeconds : int | None
        Seconds elapsed from contest start for the best submission.
    """

    points: float | None = None
    penalty: int | None = None
    rejectedAttemptCount: int | None = None
    type: str | None = None
    bestSubmissionTimeSeconds: int | None = None


class RankListRow(msgspec.Struct):
    """
    Represents a row in the contest ranklist.

    Attributes
    ----------
    party : Party | None
        Party corresponding to this ranklist row.
    rank : int | None
        Rank position of the party.
    points : float | None
        Total points scored by the party.
    penalty : int | None
        Total penalty incurred by the party.
    successfulHackCount : int | None
        Number of successful hacks performed by the party.
    unsuccessfulHackCount : int | None
        Number of unsuccessful hacks performed by the party.
    problemResults : list[ProblemResult] | None
        List of results for each problem (order corresponds to the problems list).
    lastSubmissionTimeSeconds : int | None
        Unix timestamp of the last submission contributing to the score (for IOI contests).
    """

    party: Party | None = None
    rank: int | None = None
    points: float | None = None
    penalty: int | None = None
    successfulHackCount: int | None = None
    unsuccessfulHackCount: int | None = None
    problemResults: list[ProblemResult] | None = None
    lastSubmissionTimeSeconds: int | None = None
