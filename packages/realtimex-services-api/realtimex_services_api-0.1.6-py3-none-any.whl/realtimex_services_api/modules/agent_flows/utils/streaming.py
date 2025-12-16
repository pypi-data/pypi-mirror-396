"""
Agent Flows Streaming Utilities

Provides utilities for agent flows streaming functionality including agent management,
message filtering, and configuration for chat streaming endpoints.
"""

import traceback
from typing import Any

from agent_flows_builder import create_flow_builder_agent, create_sqlite_checkpointer
from langchain_core.messages import ToolMessage

from ....utils import get_mcp_proxy_config, get_realtimex_ai_config, get_workspace_path

# Agent lifecycle management
_flow_builder_agent = None
_agent_checkpointer = None


async def get_flow_builder_agent(workspace_name: str = "agent-flows-assistant"):
    """Get or create the flow builder agent instance with SQLite persistence."""
    global _flow_builder_agent, _agent_checkpointer

    if _flow_builder_agent is None:
        try:
            # Get RealTimeX AI configuration from environment file
            realtimex_ai_api_key, realtimex_ai_base_path = get_realtimex_ai_config()

            # Get MCP proxy configuration from environment file
            mcp_aci_api_key, mcp_aci_linked_account_owner_id = get_mcp_proxy_config()

            # Get workspace path for agent storage
            workspace_path = get_workspace_path(workspace_name)

            _agent_checkpointer = create_sqlite_checkpointer(workspace=workspace_path)
            checkpointer = await _agent_checkpointer.__aenter__()
            _flow_builder_agent = create_flow_builder_agent(
                checkpointer=checkpointer,
                realtimex_ai_api_key=realtimex_ai_api_key,
                realtimex_ai_base_path=realtimex_ai_base_path,
                mcp_aci_api_key=mcp_aci_api_key,
                mcp_aci_linked_account_owner_id=mcp_aci_linked_account_owner_id,
                workspace=workspace_path,
            )
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Failed to initialize agent: {e}")

    return _flow_builder_agent


async def cleanup_flow_builder_agent():
    """Cleanup agent resources on module cleanup."""
    global _agent_checkpointer
    if _agent_checkpointer:
        try:
            await _agent_checkpointer.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors


def should_filter_message(message) -> bool:
    """Check if a message should be filtered from stream."""
    return isinstance(message, ToolMessage)


def should_filter_tool_event(tool_name: str) -> bool:
    """Check if a tool event should be filtered from stream."""
    internal_tools = {"task"}  # Internal subagent calls
    return tool_name in internal_tools


def build_agent_config(
    thread_id: str | None = None, workspace_name: str = "agent-flows-assistant"
) -> dict[str, Any]:
    """Build agent configuration with optional thread ID for persistence and workspace state."""
    config = {"configurable": {"workspace": workspace_name}}
    if thread_id:
        config["configurable"]["thread_id"] = thread_id
    return config


def extract_text_from_content(content: Any) -> str:
    """Extracts text from a content structure that may be a list of dictionaries."""
    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    if isinstance(content, str):
        return content
    return ""
