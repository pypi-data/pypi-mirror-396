"""OJIN Speech-To-Video message definitions and handlers.

This module contains message classes and utilities for handling communication
with the OJIN STV service, including audio input messages, cancellation
messages, and video response messages.
"""

import time
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ojin.entities.interaction_messages import (
    CancelInteractionInput,
    EndInteraction,
    EndInteractionMessage,
    InteractionInput,
    InteractionInputMessage,
    InteractionResponseMessage,
)


class FrameType(IntEnum):
    """Frame type for IMAGE payloads.

    Frame type is determined by interaction_id:
    - interaction_id == nil UUID (00000000-0000-0000-0000-000000000000): IDLE frames (from source video)
    - interaction_id != nil UUID: SPEECH frames (speech-generated)
    """

    IDLE = 0  # Idle frames from source video
    SPEECH = 1  # Speech-generated frames


class OjinSTVMessage(BaseModel):
    """Base class for all Ojin STV messages.

    All messages exchanged with the Ojin Inference backend inherit from this class.
    """

    def to_proxy_message(self) -> BaseModel:
        """Convert the message to a proxy message format.

        This method must be implemented by subclasses to define how the specific
        message type should be converted to its corresponding proxy message format.

        Returns:
        BaseModel: The proxy message representation of this message.

        Raises:
        NotImplementedError: Always raised as this method must be implemented
                          by concrete subclasses.

        """
        raise NotImplementedError


class OjinSTVSessionReadyMessage(OjinSTVMessage):
    """Message to start a new interaction with an Ojin Persona.

    Contains the ID of the persona to interact with.
    """

    parameters: Dict[str, Any] | None


class OjinSTVSessionReadyPing(OjinSTVMessage):
    """Ping message used to check session readiness with the Ojin backend."""


class OjinSTVInteractionResponseMessage(OjinSTVMessage):
    """Response message containing video data from the persona.

    Contains the interaction ID, persona ID, video data as bytes, and frame type.
    Frame type is determined by interaction_id: 'idle' = IDLE frames, other = SPEECH frames.
    """

    interaction_id: str
    video_frame_bytes: bytes
    audio_frame_bytes: bytes
    is_final_response: bool = False
    index: int
    frame_type: FrameType = FrameType.SPEECH

    @classmethod
    def from_proxy_message(cls, proxy_message: InteractionResponseMessage):
        """Create an instance from a proxy message response.

        Extracts video frame data and metadata from an InteractionResponseMessage
        to construct a new instance of this class.

        Args:
        proxy_message (InteractionResponseMessage): The proxy message containing
                                                  interaction response data with
                                                  video payload and metadata.

        Returns:
        cls: A new instance created from the proxy message data, containing
            the interaction ID, video frame bytes, and final response flag.

        """
        video_frame_bytes = b""
        audio_frame_bytes = b""

        for entry in proxy_message.payload.payloads:
            if entry.payload_type == "image":
                video_frame_bytes = entry.data
            elif entry.payload_type == "audio":
                audio_frame_bytes = entry.data

        # Determine frame type from interaction_id
        # Idle frames use the nil UUID (00000000-0000-0000-0000-000000000000)
        interaction_id = proxy_message.payload.interaction_id
        frame_type = FrameType.IDLE if interaction_id == "00000000-0000-0000-0000-000000000000" else FrameType.SPEECH

        return cls(
            interaction_id=interaction_id,
            video_frame_bytes=video_frame_bytes,
            audio_frame_bytes=audio_frame_bytes,
            is_final_response=proxy_message.payload.is_final_response,
            index=proxy_message.payload.index,
            frame_type=frame_type,
        )


class OjinSTVCancelInteractionMessage(OjinSTVMessage):
    """Message to cancel an interaction."""

    def to_proxy_message(self) -> CancelInteractionInput:
        """Convert the cancel message to a proxy message format.

        Creates a CancelInteractionInput message with the interaction ID and
        current timestamp to request cancellation of an ongoing interaction.

        Returns:
            CancelInteractionInput: A cancellation message containing the
                                   interaction ID and timestamp for the proxy
                                   service to process the cancellation request.

        """
        return CancelInteractionInput(
            timestamp=int(time.monotonic() * 1000),
        )


class OjinSTVEndInteractionMessage(OjinSTVMessage):
    """Message to cancel an interaction."""

    def to_proxy_message(self) -> EndInteractionMessage:
        """Convert the cancel message to a proxy message format.

        Creates a CancelInteractionInput message with the interaction ID and
        current timestamp to request cancellation of an ongoing interaction.

        Returns:
            CancelInteractionInput: A cancellation message containing the
                                   interaction ID and timestamp for the proxy
                                   service to process the cancellation request.

        """
        return EndInteractionMessage(
            payload=EndInteraction(
                timestamp=int(time.monotonic() * 1000),
            )
        )


class OjinSTVInteractionInputMessage(OjinSTVMessage):
    """Message containing audio input for the persona.

    Contains the audio data as bytes and a flag indicating if this is the last input.
    """

    audio_int16_bytes: bytes
    params: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional. Additional parameters for the interaction",
    )

    def to_proxy_message(self) -> BaseModel:
        """Convert the audio message to a proxy message format.

        Creates an InteractionInputMessage containing audio data encoded as base64,
        along with metadata such as interaction ID, timing information, and optional
        frame parameters.

        Returns:
        BaseModel: An InteractionInputMessage instance containing the encoded
                 audio data and associated metadata for transmission to the
                 proxy service.

        """
        payload = InteractionInput(
            payload_type="audio",
            payload=self.audio_int16_bytes,
            timestamp=int(time.monotonic() * 1000),
            params=self.params,
        )
        return InteractionInputMessage(
            payload=payload,
        )


class IOjinSTVClient(ABC):
    """Interface for Ojin STV client communication.

    Defines the contract for sending and receiving messages to/from the Ojin STV
    client.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Connect the client to the proxy."""

    @abstractmethod
    async def send_message(self, message: BaseModel) -> None:
        """Send a message to the server.

        Args:
           message: The message to send.

        """

    @abstractmethod
    async def start_interaction(self):
        """Create a UUID for server interactions.

        Returns:
            The UUID.

        """

    @abstractmethod
    async def receive_message(self) -> BaseModel | None:
        """Receive a message from the server.

        Returns:
            The received message.

        """

    @abstractmethod
    async def close(self) -> None:
        """Close the client."""
