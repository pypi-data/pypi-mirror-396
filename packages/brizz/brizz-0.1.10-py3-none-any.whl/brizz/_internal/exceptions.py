class BrizzError(Exception):
    """Base exception for Brizz SDK errors."""

    pass


class NotInitializedError(BrizzError):
    """Raised when SDK is used before initialization."""

    pass


class InitializationError(BrizzError):
    """Raised when SDK initialization fails."""

    pass


class ArgumentNotProvidedError(BrizzError):
    """Raised when required argument is not provided."""

    pass


class PromptNotFoundError(BrizzError):
    """Raised when prompt is not found."""

    pass
