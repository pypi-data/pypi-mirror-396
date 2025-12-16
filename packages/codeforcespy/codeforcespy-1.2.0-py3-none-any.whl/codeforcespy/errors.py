"""
⚠️ Custom Error Hierarchy.
==============================

Defines structured exception types for the Codeforces API wrapper.

✨ Purpose
--------------
- 🛡️ Type Safety: Explicit, typed exception hierarchy.
- 🔍 Debuggability: Clear error messages with structured context.
- 🏗️ Extensibility: Base class for all library exceptions.

📦 Classes
--------------
- `CodeforcesPyError`: Base exception for all library errors.
- `APIError`: Raised when the Codeforces API returns a failure response.

📝 Compliance
-----------------
Adheres to FinTech industry best practices, NumPy-style docstrings, and
strict PEP 8/257 standards.
"""


class CodeforcesPyError(Exception):
    """
    Base exception for all codeforcespy errors.

    All exceptions raised by this library inherit from this class,
    allowing users to catch all library-specific errors with a single handler.

    Attributes
    ----------
    message : str
        Human-readable error message.
    """

    __slots__: tuple[str, ...] = ("message",)

    def __init__(self, message: str) -> None:
        """
        Initialize the base error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        """
        super().__init__(message)
        self.message: str = message


class APIError(CodeforcesPyError):
    """
    Raised when the Codeforces API returns a failure response.

    This exception is raised when the API response has status "FAILED"
    and includes the error comment from the API.

    Attributes
    ----------
    message : str
        Human-readable error message (inherited from CodeforcesPyError).
    comment : str | None
        The error comment returned by the Codeforces API.
    """

    __slots__: tuple[str, ...] = ("comment",)

    def __init__(self, comment: str | None) -> None:
        """
        Initialize the API error.

        Parameters
        ----------
        comment : str | None
            The error comment from the Codeforces API response.
        """
        error_message: str = comment if comment else "Unknown API error"
        super().__init__(error_message)
        self.comment: str | None = comment
