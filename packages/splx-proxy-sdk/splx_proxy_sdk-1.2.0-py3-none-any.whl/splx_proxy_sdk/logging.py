"""
Logging utilities for the SplxAI proxy.
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterable, Mapping

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

DEFAULT_REDACTED = "***REDACTED***"


def _utc_now_iso() -> str:
    """
    Return the current UTC time in ISO-8601 format with a trailing Z for readability.
    """

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    value_lower = value.strip().lower()
    if value_lower in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if value_lower in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def _parse_csv(value: str | None, *, default: Iterable[str]) -> tuple[str, ...]:
    if not value:
        return tuple(default)
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass
class LoggingConfig:
    """
    Configuration options for the structured logging middleware.
    """

    enabled: bool = True
    log_request_body: bool = True
    log_response_body: bool = True
    max_body_length: int = 4096
    redact_headers: tuple[str, ...] = field(default_factory=lambda: ("x-api-key",))
    redact_fields: tuple[str, ...] = field(
        default_factory=lambda: (
            "api_key",
            "access_token",
            "refresh_token",
            "token",
            "secret",
            "password",
            "authorization",
        )
    )

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """
        Build a logging configuration instance from environment variables.
        """

        enabled = _parse_bool(os.getenv("SPLX_PROXY_LOG_ENABLED"), default=True)
        log_request_body = _parse_bool(
            os.getenv("SPLX_PROXY_LOG_REQUEST_BODY"), default=True
        )
        log_response_body = _parse_bool(
            os.getenv("SPLX_PROXY_LOG_RESPONSE_BODY"), default=True
        )

        max_body_length_raw = os.getenv("SPLX_PROXY_LOG_MAX_BODY_LENGTH")
        max_body_length = 4096
        if max_body_length_raw:
            try:
                max_body_length = max(0, int(max_body_length_raw))
            except ValueError:
                max_body_length = 4096

        redact_headers = _parse_csv(
            os.getenv("SPLX_PROXY_LOG_REDACT_HEADERS"),
            default=cls().redact_headers,
        )
        redact_fields = _parse_csv(
            os.getenv("SPLX_PROXY_LOG_REDACT_FIELDS"),
            default=cls().redact_fields,
        )

        return cls(
            enabled=enabled,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            max_body_length=max_body_length,
            redact_headers=tuple(header.lower() for header in redact_headers),
            redact_fields=tuple(field.lower() for field in redact_fields),
        )

    def __post_init__(self) -> None:
        self.redact_headers = tuple(header.lower() for header in self.redact_headers)
        self.redact_fields = tuple(field.lower() for field in self.redact_fields)


# pylint: disable=too-few-public-methods
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware emitting structured request/response logs via Loguru.
    """

    def __init__(self, app: ASGIApp, config: LoggingConfig):
        super().__init__(app)
        logger.remove()
        logger.add(
            sink=sys.stdout,
            serialize=True,
            backtrace=False,
            diagnose=False,
            enqueue=True,
        )

        self._context_logger = logger.opt(record=False, raw=True)

        self._config = config

    async def dispatch(self, request: Request, call_next):
        if not self._config.enabled:
            return await call_next(request)

        started_at_iso = _utc_now_iso()
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        client_host = request.client.host if request.client else None
        client_port = request.client.port if request.client else None

        client_info: dict[str, int | str] | None = None
        if client_host or client_port:
            client_info = {}
            if client_host:
                client_info["ip"] = client_host
            if client_port:
                client_info["port"] = client_port

        log_context: dict[str, Any] = {
            "request_id": request_id,
            "started_at": started_at_iso,
            "start_time": start_time,
            "client_info": client_info,
        }

        request_payload, _ = await self._create_request_payload(request, log_context)

        self._context_logger.info("Request logged.", payload=request_payload)

        response = await call_next(request)  # type: ignore

        response_payload, response_body_bytes = await self._create_response_payload(
            request,
            response,
            log_context,
        )

        self._context_logger.info("Response logged.", payload=response_payload)

        if response_body_bytes is not None:
            return Response(
                content=response_body_bytes,  # type: ignore[attr-defined]
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response

    async def _create_request_payload(
        self,
        request: Request,
        context: Mapping[str, Any],
    ) -> tuple[dict[str, Any], bytes | None]:
        request_id: str = context["request_id"]
        started_at_iso = context.get("started_at") or _utc_now_iso()
        client_info = context.get("client_info")
        sanitized_headers = self._sanitize_headers(request.headers)
        request_content_length: int | str | None = None
        request_content_length_raw = request.headers.get("content-length")
        if request_content_length_raw is not None:
            try:
                request_content_length = int(request_content_length_raw)
            except ValueError:
                request_content_length = request_content_length_raw

        request_body_bytes: bytes | None = None
        request_body = None
        request_body_length = None
        if self._config.log_request_body:
            request_body_bytes = await request.body()
            request_body_length = len(request_body_bytes)
            request_body = self._format_body(
                request_body_bytes, request.headers.get("content-type")
            )

        request_payload: dict[str, Any] = {
            "event": "request",
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "scheme": request.url.scheme,
            "host": request.url.hostname,
            "path": request.url.path,
            "query": request.url.query or None,
            "http_version": request.scope.get("http_version"),
            "headers": sanitized_headers,
            "started_at": started_at_iso,
        }
        if client_info:
            request_payload["client"] = client_info
        if request_content_length is not None:
            request_payload["content_length"] = request_content_length
        if request_body_length is not None:
            request_payload["body_length"] = request_body_length
        if request_body is not None:
            request_payload["body"] = request_body

        return request_payload, request_body_bytes

    async def _create_response_payload(
        self,
        request: Request,
        response: Response,
        context: Mapping[str, Any],
    ) -> tuple[dict[str, Any], bytes | None]:
        start_time = context.get("start_time", time.perf_counter())
        client_info = context.get("client_info")
        response_body = None
        response_body_bytes: bytes | None = None

        if self._config.log_response_body and hasattr(response, "body_iterator"):
            response_body_bytes = await self._read_bytes(response.body_iterator)  # type: ignore
            response_body = self._format_body(
                response_body_bytes, response.headers.get("content-type")
            )

        completed_at_iso = _utc_now_iso()
        duration_ms = (time.perf_counter() - start_time) * 1000
        response_body_length = len(response_body_bytes) if response_body_bytes else None
        response_content_length: int | str | None = None
        response_content_length_raw = response.headers.get("content-length")
        if response_content_length_raw is not None:
            try:
                response_content_length = int(response_content_length_raw)
            except ValueError:
                response_content_length = response_content_length_raw
        response_headers = self._sanitize_headers(response.headers)

        response_payload: dict[str, Any] = {
            "event": "response",
            "request_id": context["request_id"],
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 3),
            "completed_at": completed_at_iso,
            "headers": response_headers,
        }
        if client_info:
            response_payload["client"] = client_info
        if response_content_length is not None:
            response_payload["content_length"] = response_content_length
        if response_body_length is not None:
            response_payload["body_length"] = response_body_length
        if response_body is not None:
            response_payload["body"] = response_body

        return response_payload, response_body_bytes

    def _sanitize_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        sanitized: dict[str, str] = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower in self._config.redact_headers:
                sanitized[key] = DEFAULT_REDACTED
            else:
                sanitized[key] = value
        return sanitized

    def _format_body(self, body: bytes, content_type: str | None) -> Any:
        if not body:
            return None

        length = len(body)
        if self._config.max_body_length and length > self._config.max_body_length:
            return {"length": length, "truncated": True}

        if content_type and "json" in content_type.lower():
            try:
                parsed = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            else:
                return self._sanitize_data(parsed)

        decoded = body.decode("utf-8", errors="replace")
        if self._config.max_body_length and len(decoded) > self._config.max_body_length:
            return {
                "length": len(decoded),
                "truncated": True,
            }
        return decoded

    def _sanitize_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key: (
                    DEFAULT_REDACTED
                    if key.lower() in self._config.redact_fields
                    else self._sanitize_data(value)
                )
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [self._sanitize_data(value) for value in data]
        if isinstance(data, tuple):
            return tuple(self._sanitize_data(value) for value in data)
        return data

    async def _read_bytes(self, generator: AsyncIterator[bytes]) -> bytes:
        body = b""
        async for data in generator:
            body += data
        return body
