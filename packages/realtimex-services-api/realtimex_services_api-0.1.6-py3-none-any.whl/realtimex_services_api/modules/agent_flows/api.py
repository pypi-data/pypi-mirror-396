"""
Agent Flows API Router

FastAPI router providing Agent Flows testing, validation, and streaming endpoints.
Focuses on request/response handling while delegating business logic to service layer.
"""

import logging
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.routing import APIRoute

from .dependencies import AuthContext, get_auth_context
from .exceptions import agent_flows_http_exception, extract_error_payload
from .schemas import (
    ExecuteFlowRequest,
    FlowTestRequest,
    FlowValidationRequest,
    StreamChatRequest,
)
from .service import AgentFlowsService

logger = logging.getLogger(__name__)

# Initialize router with tags for OpenAPI documentation


class AgentFlowsRoute(APIRoute):
    """Custom route with consistent error handling for Agent Flows endpoints."""

    def get_route_handler(self) -> Callable[[Request], Any]:
        original_handler = super().get_route_handler()

        async def route_handler(request: Request) -> Any:
            try:
                return await original_handler(request)
            except HTTPException as exc:
                code, message, details = extract_error_payload(exc)
                content: dict[str, Any] = {
                    "success": False,
                    "error": {
                        "code": code,
                        "message": message,
                    },
                }
                if details:
                    content["error"]["details"] = details
                return JSONResponse(status_code=exc.status_code, content=content)
            except Exception:  # pragma: no cover - defensive guard
                logger.exception("Unhandled Agent Flows exception")
                content = {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred while processing the request.",
                    },
                }
                return JSONResponse(status_code=500, content=content)

        return route_handler


agent_flows_router = APIRouter(tags=["agent-flows"], route_class=AgentFlowsRoute)


@agent_flows_router.post("/action/test")
async def execute_flow_test(
    request: FlowTestRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    """
    Execute flow in test mode with optional pinned results.

    Validates user authentication, creates flow configuration, and executes
    the flow using the AgentFlows executor in test mode.
    """
    return await AgentFlowsService.execute_flow_test(
        request_data=request.model_dump(),
        kc_user_id=auth["kc_user_id"],
        api_key=auth["token"],
    )


@agent_flows_router.post("/action/validate")
async def validate_flow(
    request: FlowValidationRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    """
    Validate flow configuration without execution.

    Performs validation checks on the flow definition to ensure it's
    properly structured and contains valid configuration.
    """
    return await AgentFlowsService.validate_flow(
        request_data=request.model_dump(),
        kc_user_id=auth["kc_user_id"],
        api_key=auth["token"],
    )


@agent_flows_router.post("/action/execute")
async def execute_flow(
    flow_request: ExecuteFlowRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    """
    Execute a flow by flow ID.

    Validates user authentication, loads the flow by UUID, and executes
    it with optional initial variables using the AgentFlows executor.
    """
    return await AgentFlowsService.execute_flow(
        flow_request.model_dump(),
        kc_user_id=auth["kc_user_id"],
        api_key=auth["token"],
    )


@agent_flows_router.get("/chat/thread/{thread_id}")
async def get_thread_state(thread_id: str) -> dict[str, Any]:
    """Get the entire state for a given thread."""
    try:
        return await AgentFlowsService.get_thread_state(thread_id)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        raise agent_flows_http_exception(
            status_code=500, message="Failed to retrieve thread state"
        ) from exc


@agent_flows_router.post("/chat/stream")
async def stream_chat(request: StreamChatRequest):
    """
    Stream chat responses from the Agent Flows Builder

    This endpoint uses Server-Sent Events (SSE) to deliver a stream of
    structured JSON messages. Each message is an event object containing
    a specific payload.

    **Response Format:**
    Server-Sent Events with structured JSON data containing:
    - **event**: 'message_chunk' | 'tool_start' | 'tool_result' | 'flow_update' | 'stream_complete' | 'error'
    - **data**: Structured response data based on event type
    - **timestamp**: ISO timestamp
    - **node**: LangGraph node name (if applicable)

    **Event Types:**
    - `message_chunk`: LLM token streaming with content
    - `tool_start`: Tool invocation with arguments
    - `tool_result`: Tool completion with structured state updates
    - `flow_update`: Real-time flow configuration updates from AI agent
    - `stream_complete`: End of response stream
    """
    if not request.messages:
        raise agent_flows_http_exception(
            status_code=400, message="Messages cannot be empty"
        )

    messages = [msg.model_dump() for msg in request.messages]

    return StreamingResponse(
        AgentFlowsService.stream_agent_response(
            messages, request.current_flow, request.thread_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


@agent_flows_router.options("/chat/stream")
async def options_handler():
    """Handle preflight CORS requests."""
    return {"status": "ok"}
