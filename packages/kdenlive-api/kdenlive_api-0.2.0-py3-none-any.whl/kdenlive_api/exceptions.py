"""Exception classes for Kdenlive API."""


class KdenliveError(Exception):
    """Base exception for Kdenlive API errors."""

    code: int = -32603  # Internal error by default

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ValidationError(KdenliveError):
    """Input validation failed.

    Raised when input parameters fail Pydantic validation or semantic checks.
    This error is caught before sending to the WebSocket server.
    """

    code = -32602  # JSON-RPC InvalidParams

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message, self.code)
        self.field = field


class ConnectionError(KdenliveError):
    """Failed to connect to Kdenlive WebSocket server."""

    code = -32000


class ProjectNotOpenError(KdenliveError):
    """No project is currently open."""

    code = -32001


class ClipNotFoundError(KdenliveError):
    """Referenced clip does not exist."""

    code = -32002


class TrackNotFoundError(KdenliveError):
    """Referenced track does not exist."""

    code = -32003


class EffectNotFoundError(KdenliveError):
    """Referenced effect does not exist."""

    code = -32004


class RenderInProgressError(KdenliveError):
    """A render job is already running."""

    code = -32005


class InvalidClipTypeError(KdenliveError):
    """Clip type not supported for operation."""

    code = -32006


class FileNotFoundError(KdenliveError):
    """Referenced file does not exist."""

    code = -32007


class PermissionDeniedError(KdenliveError):
    """Operation not permitted."""

    code = -32008


# Mapping from error codes to exception classes
ERROR_CODE_MAP: dict[int, type[KdenliveError]] = {
    -32602: ValidationError,
    -32001: ProjectNotOpenError,
    -32002: ClipNotFoundError,
    -32003: TrackNotFoundError,
    -32004: EffectNotFoundError,
    -32005: RenderInProgressError,
    -32006: InvalidClipTypeError,
    -32007: FileNotFoundError,
    -32008: PermissionDeniedError,
}


def raise_for_error(code: int, message: str) -> None:
    """Raise appropriate exception for error code."""
    exc_class = ERROR_CODE_MAP.get(code, KdenliveError)
    raise exc_class(message, code)
