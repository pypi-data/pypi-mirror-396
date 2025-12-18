"""Error definitions and error handling."""

import math
from dataclasses import dataclass, replace
from datetime import timedelta
from enum import Enum

from fastapi import Request
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

SESSION_STATUS_HEADER = "X-Splx-Session-Status"
SESSION_STATUS_OPEN = "open"
SESSION_STATUS_CLOSED = "closed"


@dataclass(slots=True)
class ProxyExceptionConfig:
    """Structured exception config used when building proxy exceptions."""

    session_closed: bool | None = None
    retry_after: timedelta | None = None
    headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.headers is not None:
            # Copy to avoid mutating caller-provided dictionaries.
            self.headers = dict(self.headers)

    def to_headers(self) -> dict[str, str]:
        """Build the headers that should accompany the error response."""
        headers: dict[str, str] = dict(self.headers or {})

        if self.session_closed is not None:
            headers[SESSION_STATUS_HEADER] = (
                SESSION_STATUS_CLOSED if self.session_closed else SESSION_STATUS_OPEN
            )

        if self.retry_after is not None:
            headers["Retry-After"] = str(math.ceil(self.retry_after.total_seconds()))

        return headers


class ProxyHTTPStatusCode(int, Enum):
    """
    HTTP status codes used in the proxy.
    """

    SESSION_CLOSED = 452


class ExceptionCode(str, Enum):
    """
    Exception codes that can be generated from the proxy.
    These are used so the SplxAI Platform can do error handling for some
    common use cases.
    """

    UNKNOWN = "UNKNOWN"

    BAD_REQUEST = "BAD_REQUEST"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    UNAUTHORIZED = "UNAUTHORIZED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SESSION_CLOSED = "SESSION_CLOSED"


class ProxyException(HTTPException):
    """
    A custom exception implementation that includes the `ExceptionCode`.
    """

    def __init__(
        self,
        status_code: int,
        details: str,
        code: ExceptionCode,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        """
        Args:
            status_code: the status code that should be returned in the result
            details: details about the exception
            code: the `ExceptionCode` of the error
            response: metadata describing proxy-specific response headers
        """
        super().__init__(status_code, details)
        self.code = code
        self._config = config or ProxyExceptionConfig()

    def get_headers(self) -> dict[str, str] | None:
        """
        Function returning Probe supported headers formatted as dictionary
        """
        headers = self._config.to_headers()
        return headers or None


class BadRequestException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Bad Request`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.BAD_REQUEST,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        super().__init__(
            400,
            details,
            code,
            config=config,
        )


class UnauthorizedException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Unauthorized`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.UNAUTHORIZED,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        super().__init__(
            401,
            details,
            code,
            config=config,
        )


class ForbiddenException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Forbidden`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.FORBIDDEN,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        super().__init__(
            403,
            details,
            code,
            config=config,
        )


class NotFoundException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Not Found`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.NOT_FOUND,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        super().__init__(
            404,
            details,
            code,
            config=config,
        )


class SessionClosedException(ProxyException):
    """
    Specialized instance of the `ProxyException` that informs the Probe that the session is closed.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.SESSION_CLOSED,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        config = (
            replace(config, session_closed=True)
            if config
            else ProxyExceptionConfig(session_closed=True)
        )
        super().__init__(
            ProxyHTTPStatusCode.SESSION_CLOSED,
            details,
            code,
            config=config,
        )


class TooManyRequestsException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Too Many Requests`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.TOO_MANY_REQUESTS,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        """
        Args:
            details: details about the exception
            code: the `ExceptionCode` of the error (default is TOO_MANY_REQUESTS)
            config: optional exception config controlling headers returned
        """
        super().__init__(
            429,
            details,
            code,
            config=config,
        )


class InternalServerErrorException(ProxyException):
    """
    Specialized instance of the `ProxyException` that returns `Internal Server Error`.
    """

    def __init__(
        self,
        details: str,
        code: ExceptionCode = ExceptionCode.INTERNAL_SERVER_ERROR,
        *,
        config: ProxyExceptionConfig | None = None,
    ):
        super().__init__(
            500,
            details,
            code,
            config=config,
        )


class ExceptionResult(BaseModel):
    """
    The resulting model for the exception response.

    Args:
        message: the message that should be returned in the result
        code: the `ExceptionCode` of the error
    """

    message: str
    code: ExceptionCode


def _exception_handler(_: Request, exc: HTTPException):
    code = ExceptionCode.UNKNOWN
    headers = exc.headers
    if isinstance(exc, ProxyException):
        code = exc.code
        headers = exc.get_headers()

    return JSONResponse(
        status_code=exc.status_code,
        content=ExceptionResult(message=exc.detail, code=code).model_dump(),
        headers=headers,
    )
