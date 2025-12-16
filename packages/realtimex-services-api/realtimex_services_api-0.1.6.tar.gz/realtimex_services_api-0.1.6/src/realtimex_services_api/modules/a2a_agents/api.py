"""A2A Agents API Router."""

import traceback
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse
from openinference.instrumentation import using_metadata
from realtimex_agent_a2a_agent import RealTimeXAgent

# Initialize router with tags for OpenAPI documentation
a2a_agents_router = APIRouter(tags=["a2a-agents"])


def _create_error_response(
    status_code: int, error_code: str, message: str, details: dict = None
) -> JSONResponse:
    """Create standardized error response."""
    content = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


@a2a_agents_router.post("/sessions")
async def create_a2a_session(request: Request, body: Any = Body(None)) -> JSONResponse:
    """
    Create A2A session
    """
    try:
        payload = body["payload"]
        a2a_port = body["a2a_port"]
        execution_id = body["execution_id"]

        system_prompt = None
        agent_framework = None
        agent_description = None
        default_model = None
        provider_name = None
        llm_setting = None

        execution_id = payload["session_id"]
        agent_id = payload["agent_id"]
        agent_data = payload["agent_data"]
        user_id = payload["user_id"]
        workspace_slug = payload["workspace_slug"]
        thread_id = payload["thread_id"]
        knowledges = payload["knowledges"]
        memory_id = payload["memory_id"]
        memory_path = payload["memory_path"]
        message = payload["query"]
        messages = payload["messages"]
        aci_linked_account_owner_id = payload["aci_linked_account_owner_id"]
        aci_agent_first_api_key = payload["aci_api_key"]
        realtimex_access_token = payload["realtimex_access_token"]

        if "agent_description" in payload:
            agent_description = payload["agent_description"]
        if "agent_framework" in payload:
            agent_framework = payload["agent_framework"]
        if "system_prompt" in payload:
            system_prompt = payload["system_prompt"]
        if "llm_setting" in payload:
            llm_setting = payload["llm_setting"]

        default_openai_base_url = payload["litellm_api_base"]
        default_openai_api_key = payload["litellm_api_key"]

        trace_metadata = {
            "realtimex_user_id": user_id,
            "workspace_slug": workspace_slug,
            "thread_id": thread_id,
            "session_id": execution_id,
        }

        with using_metadata(trace_metadata):

            # Load MCP tools
            
            # Create agent
            agent = RealTimeXAgent(current_session_id=execution_id)

            await agent.load_default_agent(agent_id, agent_data, payload)
            
            server_url = await agent.serve_as_a2a(a2a_serving_config={"port":a2a_port,"stream_tool_usage":True})
        

        return {"server_url": server_url}

    except HTTPException as e:
        if e.status_code == 400:
            return _create_error_response(400, "INVALID_INPUT", e.detail)
        elif e.status_code == 404:
            return _create_error_response(404, "USER_NOT_FOUND", e.detail)
        else:
            return _create_error_response(e.status_code, "REQUEST_ERROR", e.detail)
    except Exception as e:
        print(traceback.format_exc())
        return _create_error_response(500, "INTERNAL_ERROR", str(e))

