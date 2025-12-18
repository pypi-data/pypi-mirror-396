"""
Authentication middleware and configuration.
"""

from dataclasses import dataclass
from typing import Callable

from fastapi import Security

from splx_proxy_sdk.error import ExceptionCode, UnauthorizedException


@dataclass
class Config:
    """Configuration for the authentication middleware."""

    secret: str
    """
    The secret with which the value should be compared with.
    """
    security: Callable
    """
    The security function to use for extracting the secret from the request.
    More details are in the [FastAPI docs](https://fastapi.tiangolo.com/tutorial/security/).
    """


def _auth_func(api_key: str, base: Callable):
    async def _f(key: str = Security(base)):
        if key != api_key:
            raise UnauthorizedException("Invalid API key", ExceptionCode.UNAUTHORIZED)
        return None

    return _f
