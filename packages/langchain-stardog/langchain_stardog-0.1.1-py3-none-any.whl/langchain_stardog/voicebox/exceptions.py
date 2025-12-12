class VoiceboxException(Exception):
    """Base exception for all Voicebox-related errors."""

    def __init__(self, message: str, exception: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong
            exception: The original exception that was caught (if any)
        """
        self.message = message
        self.original_exception = exception
        super().__init__(self.message)


class VoiceboxAuthenticationError(VoiceboxException):
    """Raised when authentication with Stardog Cloud fails."""

    pass


class VoiceboxAPIError(VoiceboxException):
    """Raised when the Stardog Cloud API returns an error."""

    pass


class VoiceboxValidationError(VoiceboxException):
    """Raised when input validation fails."""

    pass
