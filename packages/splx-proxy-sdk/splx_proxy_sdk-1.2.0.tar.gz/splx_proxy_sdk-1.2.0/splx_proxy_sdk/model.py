"""
Model definitions.
"""

from enum import Enum
from typing import Dict, Generic, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel

from .error import BadRequestException

# pylint: disable=unexpected-keyword-arg
ExtraArgsT = TypeVar("ExtraArgsT", default=None)

# Base64 encoded image or audio
MultiModalImage = str
MultiModalAudio = str
MultiModalDocument = str

MultiModalContent = Union[MultiModalImage, MultiModalAudio, MultiModalDocument]


class MultiModalType(str, Enum):
    """
    The type of multimodal content.

    Supported types:
        - `image`
        - `audio`
        - `document`

    """

    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"


class MultiModal(BaseModel):
    """
    A multimodal content value.

    Args:
        type: the type of multimodal content
        content: the multimodal content, sent as a base64-encoded Data URI.
        To parse its parts, use `MultiModal.parse_content()`.
    """

    type: MultiModalType
    content: MultiModalContent

    @staticmethod
    def parse_content(content: MultiModalContent) -> Tuple[str, str]:
        """
        Parser method for the base64-encoded Data URI.

        Args:
            `content`: the multimodal content, sent as a base64-encoded Data URI.

        Returns:
            `Tuple[str, str]`: the first value is the media type (e.g. image/webp), and
            the second one is the base64-encoded file.
        """
        if content[:5] != "data:":
            raise BadRequestException(
                "The provided multimodal content is not a base64-encoded Data URI."
            )

        split_content = content[5:].split(",")

        mime_type = split_content[0].rstrip(";base64")
        base64_file = split_content[1]

        return mime_type, base64_file


class OpenSessionRequest(BaseModel, Generic[ExtraArgsT]):
    """
    The request to open a new session.

    Args:
        session_id: the session id to use.
            If not provided, a new session should be generated from the server.
        extra_args: any extra static attributes or data you want to
            include in the request. Default is None.
    """

    session_id: Optional[str] = None

    extra_args: Optional[ExtraArgsT] = None


class OpenSessionResponse(BaseModel):
    """
    The response of opening a new session.

    Args:
        session_id: the session id that should be used for the session
    """

    session_id: str


class SendMessageRequest(BaseModel, Generic[ExtraArgsT]):
    """
    The request to send a message to the session.

    Args:
        session_id: the session id to use
        message: the message to send
        multimodal: the multimodal content to send.
            The key of the dictionary is the name of the multimodal content,
            and the value is the `MultiModal` message.
        extra_args: any extra static attributes or data you want to
            include in the request. Default is None.
    """

    session_id: str
    message: str
    multimodal: Optional[Dict[str, MultiModal]] = None

    extra_args: Optional[ExtraArgsT] = None


class SendMessageResponse(BaseModel):
    """
    The response of sending a message to the session.

    Args:
        session_id: the session id that is used for the session
        message: the message received
        multimodal: the multimodal content received.
            The key of the dictionary is the name of the multimodal content,
            and the value is the `MultiModal` message.
    """

    session_id: str
    message: str
    multimodal: Optional[Dict[str, MultiModal]] = None


class CloseSessionRequest(BaseModel, Generic[ExtraArgsT]):
    """
    The request to close a session.

    Args:
        session_id: the session id to close
        extra_args: any extra static attributes or data you want to
            include in the request. Default is None.
    """

    session_id: str

    extra_args: Optional[ExtraArgsT] = None


class CloseSessionResponse(BaseModel):
    """
    The response of closing a session.
    """
