"""
Agent Flows Schemas

Pydantic models for Agent Flows API requests, responses, and data structures.
Provides structured validation for chat streaming and flow processing.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Individual chat message in conversation."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class StreamChatRequest(BaseModel):
    """Request model for streaming chat endpoint."""

    messages: list[ChatMessage] = Field(..., description="Chat conversation history")
    stream: bool = Field(True, description="Enable streaming response")
    thread_id: str | None = Field(
        None, description="Thread ID for conversation persistence"
    )
    current_flow: dict | None = Field(
        None, description="Current flow definition for flow-aware agent context"
    )


class ExecuteFlowRequest(BaseModel):
    """Request model for flow execution endpoint."""

    flow_id: str = Field(..., description="UUID of the flow to execute")
    variables: dict[str, Any] | None = Field(
        None, description="Initial variables for the flow execution"
    )
    include_trace: bool = Field(
        False, description="Whether to include step-by-step execution trace"
    )


class FlowValidationRequest(BaseModel):
    """Base request model for flow validation operations."""

    model_config = ConfigDict(extra="allow")

    flow_definition: dict[str, Any] = Field(
        ..., description="Full flow definition to validate"
    )


class FlowTestRequest(FlowValidationRequest):
    """Request model for flow test execution."""

    test_manifest: dict[str, Any] | None = Field(
        None, description="Optional test manifest configuration"
    )
    include_trace: bool = Field(
        False, description="Whether to include step-by-step execution trace"
    )


class StreamResponse(BaseModel):
    """Structured response model for streaming events."""

    event: str = Field(
        ...,
        description="Event type: 'message_chunk' | 'final_message' | 'tool_start' | 'tool_result' | 'flow_update' | 'stream_complete' | 'error'",
    )
    data: dict[str, Any] = Field(..., description="Event-specific data payload")
    timestamp: str = Field(..., description="ISO timestamp with timezone")
    node: str | None = Field(
        None, description="LangGraph node name where event originated"
    )
    message_id: str | None = Field(
        None, description="Message ID for grouping related chunks"
    )


def create_stream_response(
    event_type: str,
    data: dict[str, Any],
    node: str | None = None,
    message_id: str | None = None,
) -> str:
    """Create a formatted Server-Sent Events response."""
    response = StreamResponse(
        event=event_type,
        data=data,
        timestamp=datetime.now(UTC).isoformat(),
        node=node,
        message_id=message_id,
    )
    return f"data: {response.model_dump_json()}\n\n"
