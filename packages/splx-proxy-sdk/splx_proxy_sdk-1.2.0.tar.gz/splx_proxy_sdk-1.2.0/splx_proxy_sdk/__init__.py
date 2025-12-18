"""
A SDK for building proxy servers for integration between user applications and SplxAI Platform.
"""

from splx_proxy_sdk.error import (
    BadRequestException,
    ExceptionCode,
    ForbiddenException,
    InternalServerErrorException,
    NotFoundException,
    ProxyException,
    ProxyExceptionConfig,
    SessionClosedException,
    TooManyRequestsException,
    UnauthorizedException,
)
from splx_proxy_sdk.logging import LoggingConfig
from splx_proxy_sdk.model import (
    CloseSessionRequest,
    CloseSessionResponse,
    MultiModal,
    MultiModalAudio,
    MultiModalContent,
    MultiModalDocument,
    MultiModalImage,
    MultiModalType,
    OpenSessionRequest,
    OpenSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from splx_proxy_sdk.server import Server
from splx_proxy_sdk.version import VERSION

__version__ = VERSION

__all__ = [
    "ExceptionCode",
    "ProxyException",
    "UnauthorizedException",
    "BadRequestException",
    "NotFoundException",
    "ForbiddenException",
    "TooManyRequestsException",
    "InternalServerErrorException",
    "SessionClosedException",
    "ProxyExceptionConfig",
    "MultiModalType",
    "MultiModal",
    "MultiModalAudio",
    "MultiModalContent",
    "MultiModalDocument",
    "MultiModalImage",
    "SendMessageRequest",
    "SendMessageResponse",
    "OpenSessionRequest",
    "OpenSessionResponse",
    "CloseSessionRequest",
    "CloseSessionResponse",
    "Server",
    "LoggingConfig",
]
