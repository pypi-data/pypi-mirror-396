# SPLX AI Proxy

The SPLX AI Proxy is a lightweight and easy-to-use interface for creating and managing API proxies for integration with the SPLX Platform.

## Getting Started

1. **Install the SDK**

```bash
# poetry
poetry add splx-proxy-sdk

# pip
pip install splx-proxy-sdk
```

2. **Implement your proxy server**

```python
from fastapi import Request
from pydantic import BaseModel

from splx_proxy_sdk import (
    CloseSessionRequest,
    CloseSessionResponse,
    OpenSessionRequest,
    OpenSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
    Server,
)


class ExtraArgs(BaseModel):
    tone: str
    token_count: int


class SimpleServer(Server):
    async def open_session(
        self, request: OpenSessionRequest, raw: Request
    ) -> OpenSessionResponse:
        raise NotImplementedError("Implement the open_session method")

    async def close_session(
        self, request: CloseSessionRequest, raw: Request
    ) -> CloseSessionResponse:
        raise NotImplementedError("Implement the close_session method")

    async def send_message(
        self, request: SendMessageRequest[ExtraArgs], raw: Request
    ) -> SendMessageResponse:
        if request.extra_args:
            print("Response tone:", request.extra_args.tone)
            print("Response token count:", request.extra_args.token_count)

        return SendMessageResponse(
            session_id="test", message="Hello, how may I help you?"
        )


# Ensure SPLX_PROXY_API_KEY env. variable is set before instantiating the server
app = SimpleServer()
```

3. **Run the service**

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

The SPLX Platform must be able to reach the host and port you expose.

See [examples/simple_server](examples/simple_server/main.py) for a sample project, including `.env` placeholders for SPLX credentials.

## Features

### Authentication

Proxy SDK requires authentication using the `x-api-key` header. To set the secret, you need to set the `SPLX_PROXY_API_KEY` environment variable.

### Extra arguments

If you want to use some extra arguments in any of the endpoints, you can parametrize any of the Request classes (OpenSessionRequest, SendMessageRequest, CloseSessionRequest). To do that, define your own class and use it as in the [example](examples/simple_server/main.py) code. This approach provides simple customization together with type safety.

### Logging

By default, all requests and responses are logged in JSON format.

```json
{
  "text": "Request logged.",
  "record": {
    "elapsed": { "repr": "0:00:01.259405", "seconds": 1.259405 },
    "exception": null,
    "extra": {
      "payload": {
        "event": "request",
        "request_id": "1f8c1f39-e2c3-471e-b567-d69b2d58337f",
        "method": "POST",
        "url": "http://127.0.0.1:8000/send-message",
        "scheme": "http",
        "host": "127.0.0.1",
        "path": "/send-message",
        "query": null,
        "http_version": "1.1",
        "headers": {
          "host": "127.0.0.1:8000",
          "connection": "keep-alive",
          "content-length": "342",
          "sec-ch-ua-platform": "\"macOS\"",
          "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
          "accept": "application/json",
          "sec-ch-ua": "\"Chromium\";v=\"142\", \"Brave\";v=\"142\", \"Not_A Brand\";v=\"99\"",
          "content-type": "application/json",
          "x-api-key": "***REDACTED***",
          "sec-ch-ua-mobile": "?0",
          "sec-gpc": "1",
          "accept-language": "en-US,en;q=0.8",
          "origin": "http://127.0.0.1:8000",
          "sec-fetch-site": "same-origin",
          "sec-fetch-mode": "cors",
          "sec-fetch-dest": "empty",
          "referer": "http://127.0.0.1:8000/docs",
          "accept-encoding": "gzip, deflate, br, zstd"
        },
        "started_at": "2025-11-03T09:29:18.151146Z",
        "client": { "ip": "127.0.0.1", "port": 60711 },
        "content_length": 342,
        "body_length": 342,
        "body": {
          "session_id": "string",
          "message": "string",
          "multimodal": {
            "additionalProp1": { "type": "image", "content": "string" },
            "additionalProp2": { "type": "image", "content": "string" },
            "additionalProp3": { "type": "image", "content": "string" }
          },
          "extra_args": "string"
        }
      }
    },
    "file": {
      "name": "logging.py",
      "path": "/Users/ivanvlahov/Desktop/SPLX/splx-proxy-sdk/splx_proxy_sdk/logging.py"
    },
    "function": "dispatch",
    "level": { "icon": "ℹ️", "name": "INFO", "no": 20 },
    "line": 169,
    "message": "Request logged.",
    "module": "logging",
    "name": "splx_proxy_sdk.logging",
    "process": { "id": 49939, "name": "SpawnProcess-1" },
    "thread": { "id": 8591597888, "name": "MainThread" },
    "time": {
      "repr": "2025-11-03 10:29:18.151469+01:00",
      "timestamp": 1762162158.151469
    }
  }
}
INFO:     127.0.0.1:60711 - "POST /send-message HTTP/1.1" 200 OK
{
  "text": "Response logged.",
  "record": {
    "elapsed": { "repr": "0:00:01.262576", "seconds": 1.262576 },
    "exception": null,
    "extra": {
      "payload": {
        "event": "response",
        "request_id": "1f8c1f39-e2c3-471e-b567-d69b2d58337f",
        "method": "POST",
        "url": "http://127.0.0.1:8000/send-message",
        "path": "/send-message",
        "status_code": 200,
        "duration_ms": 3.394,
        "completed_at": "2025-11-03T09:29:18.154589Z",
        "headers": {
          "content-length": "65",
          "content-type": "application/json"
        },
        "client": { "ip": "127.0.0.1", "port": 60711 },
        "content_length": 65,
        "body_length": 65,
        "body": {
          "session_id": "test",
          "message": "Hello, world!",
          "multimodal": null
        }
      }
    },
    "file": {
      "name": "logging.py",
      "path": "/Users/ivanvlahov/Desktop/SPLX/splx-proxy-sdk/splx_proxy_sdk/logging.py"
    },
    "function": "dispatch",
    "level": { "icon": "ℹ️", "name": "INFO", "no": 20 },
    "line": 179,
    "message": "Response logged.",
    "module": "logging",
    "name": "splx_proxy_sdk.logging",
    "process": { "id": 49939, "name": "SpawnProcess-1" },
    "thread": { "id": 8591597888, "name": "MainThread" },
    "time": {
      "repr": "2025-11-03 10:29:18.154640+01:00",
      "timestamp": 1762162158.15464
    }
  }
}
```

You can use the `LoggingConfig` class to configure the logging in your server’s constructor. Alternatively, you can use environment variables:

- `SPLX_PROXY_LOG_ENABLED` - defaults to `True`
- `SPLX_PROXY_LOG_REQUEST_BODY` - defaults to `True`
- `SPLX_PROXY_LOG_RESPONSE_BODY` - defaults to `True`
- `SPLX_PROXY_LOG_MAX_BODY_LENGTH` - defaults to `4096`
- `SPLX_PROXY_LOG_REDACT_HEADERS` - defaults to `x-api-key`
- `SPLX_PROXY_LOG_REDACT_FIELDS` - defaults to `api_key`, `access_token`, `refresh_token`, `token`, `secret`, `password`, `authorization`

### Exception Catalogue

Proxy SDK exposes multiple exception classes:

- `BadRequestException`
- `UnauthorizedException`
- `ForbiddenException`
- `NotFoundException`
- `SessionClosedException` - error code 452
- `TooManyRequestsException`
- `InternalServerErrorException`

Each of these exceptions can be raised with the following parameters:

- `details: str` - details of the exception
- `code: ExceptionCode` - each exception has a default enum value
- `config: ProxyExceptionConfig | None = None` - an exception config object that sets the headers
  - `session_closed: bool | None = None` - tells Probe whether the session was closed as a result of this exception, uses a X-Splx-Session-Status header internally
  - `retry_after: timedelta | None = None` - tells Probe when to retry the request, if needed, uses a Retry-After header internally
  - `headers: dict[str, str]` - any additional headers you want to include in the exception

## Useful links

- TODO: Link to public documentation
- TODO: Link to package repository
