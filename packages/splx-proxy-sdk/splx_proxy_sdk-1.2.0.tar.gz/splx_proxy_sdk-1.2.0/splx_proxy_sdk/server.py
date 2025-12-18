"""
Server definition that the user should extend.
"""

import os
from abc import ABC, abstractmethod
from typing import Generic, Mapping, TypeVar
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.exceptions import HTTPException

from splx_proxy_sdk.auth import _auth_func
from splx_proxy_sdk.error import _exception_handler
from splx_proxy_sdk.logging import LoggingConfig, RequestLoggingMiddleware
from splx_proxy_sdk.model import (
    CloseSessionRequest,
    CloseSessionResponse,
    OpenSessionRequest,
    OpenSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)

API_KEY_ENV_VAR = "SPLX_PROXY_API_KEY"
API_KEY_HEADER_NAME = "x-api-key"

# pylint: disable=unexpected-keyword-arg
ExtraArgsT = TypeVar("ExtraArgsT", default=None)


class Server(FastAPI, ABC, Generic[ExtraArgsT]):
    """
    The server that handles the proxy requests.
    This class should be extended to implement the actual server.
    It also supports all `FastAPI` features.

    **Example:**
    ```python
    from proxy import Server
    from proxy import (
            OpenSessionRequest,
            OpenSessionResponse,
            CloseSessionRequest,
            CloseSessionResponse,
            SendMessageRequest,
            SendMessageResponse
        )

    class MyServer(Server):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # some other initialization code

        async def open_session(
            self, request: OpenSessionRequest, raw: Request
        ) -> OpenSessionResponse:
            return OpenSessionResponse(session_id="my-session-id")
        async def close_session(
            self, request: CloseSessionRequest, raw: Request
        ) -> CloseSessionResponse:
            return CloseSessionResponse()
        async def send_message(
            self, request: SendMessageRequest, raw: Request
        ) -> SendMessageResponse:
            return SendMessageResponse(session_id="my-session-id", message="Hello, world!")
    ```
    You can find more examples in the
    [examples](https://github.com/splx-ai/proxy/tree/main/examples) directory.
    """

    def __init__(self, logging_config=None, **kwargs):
        """
        The init method of the server.
        It uses the `FastAPI` constructor and adds the routes for the proxy requests.
        Additionally, it adds the authentication middleware with the API key loaded
        from the `SPLX_PROXY_API_KEY` environment variable.

        Args:
            logging_config: The logging configuration or mapping.
            **kwargs: Additional keyword arguments for the FastAPI constructor.
        """

        if logging_config is None:
            logging_config = LoggingConfig.from_env()
        elif isinstance(logging_config, Mapping):
            logging_config = LoggingConfig(**logging_config)
        elif not isinstance(logging_config, LoggingConfig):
            raise TypeError("logging_config must be a LoggingConfig or mapping")

        api_key = os.getenv(API_KEY_ENV_VAR)
        if not api_key:
            raise RuntimeError(
                (
                    "SPLX_PROXY_API_KEY environment variable ",
                    "must be set before starting the proxy server.",
                )
            )

        super().__init__(**kwargs)
        if logging_config.enabled:
            self.add_middleware(RequestLoggingMiddleware, config=logging_config)

        security = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=True)
        dependencies = [Depends(_auth_func(api_key, security))]

        router = APIRouter(dependencies=dependencies)

        router.add_api_route(
            "/open-session",
            self.open_session,
            methods=["POST"],
        )
        router.add_api_route(
            "/close-session",
            self.close_session,
            methods=["POST"],
        )
        router.add_api_route(
            "/send-message",
            self.send_message,
            methods=["POST"],
        )

        self.include_router(router)
        self.exception_handler(HTTPException)(_exception_handler)

    @abstractmethod
    async def open_session(
        self, request: OpenSessionRequest[ExtraArgsT], raw: Request
    ) -> OpenSessionResponse:
        """
        The method that handles the `/open-session` request.
        It should return an `OpenSessionResponse` object with the session ID.

        Args:
            request: The request object.
            raw: The raw request object so you can access the headers, query parameters, etc.
        """
        session_id = request.session_id if request.session_id else str(uuid4())
        return OpenSessionResponse(session_id=session_id)

    @abstractmethod
    async def close_session(
        self, request: CloseSessionRequest[ExtraArgsT], raw: Request
    ) -> CloseSessionResponse:
        """
        The method that handles the `/close-session` request.
        It should return a `CloseSessionResponse` object.

        Args:
            request: The request object.
            raw: The raw request object so you can access the headers, query parameters, etc.
        """
        return CloseSessionResponse()

    @abstractmethod
    async def send_message(
        self, request: SendMessageRequest[ExtraArgsT], raw: Request
    ) -> SendMessageResponse:
        """
        The method that handles the `/send-message` request.
        It should return a `SendMessageResponse` object with the session ID and the message.

        Args:
            request: The request object.
            raw: The raw request object so you can access the headers, query parameters, etc.
        """
        raise NotImplementedError()
