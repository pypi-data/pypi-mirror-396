"""Interaction messages."""

import json
import struct
import uuid
from contextlib import suppress
from enum import IntEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ojin.entities.session_messages import MessageType

# Format: Byte: payload type, uint64 timestamp, uint32 params size
INTERACTION_INPUT_FORMAT = "!BQI"
INTERACTION_INPUT_MESSAGE_HEADER_SIZE = struct.calcsize(INTERACTION_INPUT_FORMAT)

# Format: Byte: is final flag, 16b UUID, uint64 timestamp, uint32 usage, uint32 index, uint32 number of payload entries
INTERACTION_RESPONSE_FORMAT = "!B16sQIII"
INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE = struct.calcsize(INTERACTION_RESPONSE_FORMAT)


class PayloadType(IntEnum):
    """Payload type constants for binary serialization."""

    TEXT = 0
    AUDIO = 1
    IMAGE = 2
    VIDEO = 3


def payload_type_from_str(payload_type_str: str):
    payload_type_map = {
        "text": PayloadType.TEXT,
        "audio": PayloadType.AUDIO,
        "image": PayloadType.IMAGE,
        "video": PayloadType.VIDEO,
    }
    return payload_type_map.get(payload_type_str.lower(), PayloadType.TEXT)


def payload_type_to_str(payload_type: PayloadType):
    payload_type_map = {
        PayloadType.TEXT: "text",
        PayloadType.AUDIO: "audio",
        PayloadType.IMAGE: "image",
        PayloadType.VIDEO: "video",
    }
    return payload_type_map.get(payload_type, "text")


class InteractionInput(BaseModel):
    """Interaction input."""

    payload_type: str = Field(
        ...,
        description="Type of the data in the payload",
    )
    payload: bytes = Field(
        ...,
        description="The actual data.",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by client",
    )
    params: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional. Additional parameters for the interaction",
    )


class EndInteraction(BaseModel):
    """End interaction."""

    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by client",
    )


class EndInteractionMessage(BaseModel):
    """Interaction input message sent from client to proxy."""

    type: MessageType = MessageType.END_INTERACTION
    payload: EndInteraction


class CancelInteractionInput(BaseModel):
    timestamp: Optional[int] = Field(
        None,
        description="Timestamp in milliseconds when the message was sent by the proxy",
    )


class CancelInteractionMessage(BaseModel):
    """Interaction cancel message sent from client to proxy."""

    type: MessageType = MessageType.CANCEL_INTERACTION

    payload: CancelInteractionInput


class InteractionResponsePayload(BaseModel):
    payload_type: str = Field(
        ...,
        description="Type of the data in the payload",
    )
    data: bytes = Field(
        ...,
        description="The actual output data.",
    )


class InteractionResponse(BaseModel):
    """Interaction response."""

    interaction_id: str = Field(
        ...,
        description="ID linking this response to the corresponding client interaction",
    )
    payloads: List[InteractionResponsePayload] = Field(
        ...,
        description="List of the actual output data.",
    )
    is_final_response: bool = Field(
        ...,
        description="True if this is the final output chunk for this interaction_id",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by proxy",
    )
    usage: int = Field(
        ...,
        description="Usage metric for this response (unsigned 4-byte integer)",
    )
    index: int = Field(
        ...,
        description="The index of the infered payload (e.g frame index in case of persona)",
    )


class ErrorResponse(BaseModel):
    """Error response."""

    interaction_id: Optional[str] = Field(
        None,
        description="Optional. The interaction_id related to the error, if applicable",
    )
    code: str = Field(
        ...,
        description="Short error code (e.g., AUTH_FAILED, INVALID_MODEL_ID, TIMEOUT)",
    )
    message: str = Field(
        ...,
        description="A human-readable description of the error",
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional. Additional structured details about the error",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by proxy",
    )


class InteractionInputMessage(BaseModel):
    """Interaction input message sent from client to proxy.

    Binary format:
    - Byte - payload type:
        0 - text
        1 - audio
        2 - image
        3 - video
    - 8 bytes - timestamp (uint64, milliseconds since Unix epoch)
    - 4 byte: Encoded parameters size (uint32)
    - Remaining bytes - params data and payload data
    """

    type: MessageType = MessageType.INTERACTION_INPUT
    payload: InteractionInput

    def to_bytes(self) -> bytes:
        """Convert the message to bytes."""
        # Get payload type as int
        payload_type = payload_type_from_str(self.payload.payload_type)

        # Use current timestamp if not provided
        timestamp = self.payload.timestamp

        # Serialize params if present
        params_bytes = b""
        if self.payload.params:
            try:
                params_bytes = json.dumps(self.payload.params).encode("utf-8")
            except (TypeError, UnicodeEncodeError):
                pass

        # Pack the fixed-size header
        header = struct.pack(
            INTERACTION_INPUT_FORMAT, int(payload_type), timestamp, len(params_bytes)
        )

        # Combine header, params, and payload
        return header + params_bytes + self.payload.payload

    @staticmethod
    def from_bytes(data: bytes) -> "InteractionInputMessage":
        """Convert bytes to an InteractionInputMessage."""
        # Ensure we have at least the header
        if len(data) < INTERACTION_INPUT_MESSAGE_HEADER_SIZE:
            raise ValueError("Invalid data: message too short")

        # Extract header fields
        (payload_type_int, timestamp, params_size) = struct.unpack(
            INTERACTION_INPUT_FORMAT, data[:INTERACTION_INPUT_MESSAGE_HEADER_SIZE]
        )

        current_pos = INTERACTION_INPUT_MESSAGE_HEADER_SIZE

        # Extract params if present
        params = None

        if params_size > 0:
            params_bytes = data[current_pos : current_pos + params_size]
            with suppress(json.JSONDecodeError, UnicodeDecodeError):
                params = json.loads(params_bytes.decode("utf-8"))
            current_pos += params_size

        # The rest is payload
        payload_bytes = data[current_pos:]

        # Convert payload type int to string
        payload_type = payload_type_to_str(payload_type_int)

        # Create the interaction input
        interaction_input = InteractionInput(
            payload_type=payload_type,
            payload=payload_bytes,
            timestamp=timestamp,
            params=params,
        )

        # Return the message
        return InteractionInputMessage(payload=interaction_input)


class InteractionResponseMessage(BaseModel):
    """Interaction response message sent from proxy to client.

    Binary format:
    - Byte - flag indicating if this is the final response
        - 1: True
        - 0: False
    - 16 bytes - interaction_id (UUID)
    - 8 bytes - timestamp (uint64, milliseconds since Unix epoch)
    - 4 bytes - usage (uint32)
    - 4 bytes - message index (uint32)
    - Bytes - number of payloads in the response
    - The remaing bytes contains encoded payloads:
        - Each payload entry contains:
            - 4 bytes: size of payload data in bytes (uint32)
            - Byte - payload type:
                0 - text
                1 - audio
                2 - image
                3 - video
            - Remaining bytes in entry - payload data
    """

    type: MessageType = MessageType.INTERACTION_RESPONSE
    payload: InteractionResponse

    def to_bytes(self) -> bytes:
        """Convert the message to bytes."""
        # Convert UUID string to bytes (16 bytes)
        interaction_id_bytes = uuid.UUID(self.payload.interaction_id).bytes

        # Get message type as int
        is_final_flag = int(self.payload.is_final_response)

        timestamp = self.payload.timestamp
        usage = self.payload.usage
        index = self.payload.index

        # Pack the fixed-size header
        header = struct.pack(
            INTERACTION_RESPONSE_FORMAT,
            is_final_flag,
            interaction_id_bytes,
            timestamp,
            usage,
            index,
            len(self.payload.payloads),
        )

        result = header
        for entry in self.payload.payloads:
            # Get payload type as int
            payload_type = payload_type_from_str(entry.payload_type)
            encoded_entry_header = struct.pack(
                "!IB",  # Format: uint32 payload data size in bytes, Byte
                len(entry.data),
                payload_type,
            )
            result += encoded_entry_header + entry.data

        # Combine header and payload
        return result

    @staticmethod
    def get_usage_from_bytes(data: bytes) -> int:
        """Get the usage from the bytes."""
        if len(data) < INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE:
            raise ValueError("Invalid data: message too short")

        _, _, _, usage, _, _ = struct.unpack(
            INTERACTION_RESPONSE_FORMAT, data[:INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE]
        )
        return usage

    @staticmethod
    def from_bytes(data: bytes) -> "InteractionResponseMessage":
        """Convert bytes to an InteractionResponseMessage."""
        # Ensure we have at least the header
        if len(data) < INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE:
            raise ValueError("Invalid data: message too short")

        # Extract header fields
        (
            is_final_flag,
            interaction_id_bytes,
            timestamp,
            usage,
            index,
            payload_entries_count,
        ) = struct.unpack(
            INTERACTION_RESPONSE_FORMAT, data[:INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE]
        )

        data = data[INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE:]
        payloads: List[InteractionResponsePayload] = []
        for _ in range(payload_entries_count):
            if len(data) < 5:
                raise ValueError("Invalid data: truncated payload entry header")
            data_size, payload_type_int = struct.unpack(
                "!IB",  # Format: uint32 payload data size in bytes, Byte
                data[:5],
            )
            payload_type = payload_type_to_str(payload_type_int)
            data = data[5:]
            if len(data) < data_size:
                raise ValueError("Invalid data: truncated payload entry body")
            payload_data = data[:data_size]
            data = data[data_size:]
            payloads.append(
                InteractionResponsePayload(payload_type=payload_type, data=payload_data)
            )
        # Convert bytes to UUID string
        interaction_id = str(uuid.UUID(bytes=interaction_id_bytes))

        # Determine if this is a final message
        is_final_response = bool(is_final_flag)

        # Create the interaction response
        interaction_response = InteractionResponse(
            interaction_id=interaction_id,
            is_final_response=is_final_response,
            timestamp=timestamp,
            usage=usage,
            index=index,
            payloads=payloads,
        )

        # Return the message
        return InteractionResponseMessage(payload=interaction_response)


class ErrorResponseMessage(BaseModel):
    """Error response message sent from proxy to client."""

    type: MessageType = MessageType.ERROR_RESPONSE
    payload: ErrorResponse
