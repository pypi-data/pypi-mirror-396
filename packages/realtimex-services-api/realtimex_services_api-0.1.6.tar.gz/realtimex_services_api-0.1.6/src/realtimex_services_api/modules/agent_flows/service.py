"""
Agent Flows Service Layer

Business logic for Agent Flows functionality including user validation,
system configuration, flow execution, and streaming responses.
"""

import json
from collections.abc import AsyncGenerator
from typing import Any, Dict

from agent_flows import (
    AgentFlowsConfig,
    FlowConfig,
    FlowExecutor,
    LiteLLMConfig,
    MCPConfig,
    FlowResult,
)
from agent_flows.models.config import LoggingConfig
from agent_flows_builder.telemetry import flow_builder_tracing_context

from ...utils import (
    DEFAULT_OPENAI_API_KEY,
    DEFAULT_OPENAI_BASE_URL,
    get_realtimex_user,
    reload_env_configs,
)
from .exceptions import agent_flows_http_exception
from .schemas import create_stream_response
from .utils.flow_processing import prepare_flow_for_agent
from .utils.streaming import (
    build_agent_config,
    extract_text_from_content,
    get_flow_builder_agent,
    should_filter_message,
    should_filter_tool_event,
)

_AGENT_FLOWS_PROJECT = "realtimex-agent-flows"


class AgentFlowsService:
    """Service class for Agent Flows business logic."""

    @staticmethod
    def get_user_data(kc_user_id: str) -> Dict[str, Any]:
        """
        Fetch user data by Keycloak user ID.

        Args:
            kc_user_id: Keycloak user identifier

        Returns:
            User data dictionary

        Raises:
            HTTPException: If user not found
        """
        if not kc_user_id or not kc_user_id.strip():
            raise agent_flows_http_exception(
                status_code=401,
                message="Keycloak user identifier is required",
            )

        user_data = get_realtimex_user(kc_user_id)
        if not user_data:
            raise agent_flows_http_exception(
                status_code=404, code="USER_NOT_FOUND", message="User not found"
            )
        return user_data

    @staticmethod
    def create_system_config(
        user_data: Dict[str, Any], api_key: str
    ) -> AgentFlowsConfig:
        """
        Create AgentFlowsConfig from user data and API key.

        Args:
            user_data: User information dictionary
            api_key: API key for Agent Flow execution

        Returns:
            Configured AgentFlowsConfig instance
        """
        return AgentFlowsConfig(
            api_key=api_key,
            base_url="https://marketplace-api.realtimex.ai",
            litellm=LiteLLMConfig(
                api_key=DEFAULT_OPENAI_API_KEY,
                api_base=DEFAULT_OPENAI_BASE_URL,
            ),
            mcp=MCPConfig(
                aci_api_key=user_data.get("aci_agent_first_api_key"),
                aci_linked_account_owner_id=user_data.get(
                    "aci_linked_account_owner_id"
                ),
            ),
            logging=LoggingConfig(
                level="DEBUG",
                json_format=False,
            ),
        )

    @staticmethod
    def validate_flow_definition(flow_definition: Any) -> Dict[str, Any]:
        """
        Validate flow definition structure.

        Args:
            flow_definition: Flow definition to validate

        Raises:
            HTTPException: If flow definition is invalid
        """
        if not isinstance(flow_definition, dict):
            raise agent_flows_http_exception(
                status_code=400,
                code="INVALID_FLOW_DEFINITION",
                message="Flow definition must be a JSON object",
            )

        steps = flow_definition.get("steps")
        if not isinstance(steps, list) or not steps:
            raise agent_flows_http_exception(
                status_code=400,
                code="INVALID_FLOW_DEFINITION",
                message="Flow definition must contain at least one step",
            )

        return flow_definition

    @classmethod
    async def execute_flow(
        cls,
        request_data: Dict[str, Any],
        kc_user_id: str,
        api_key: str,
    ) -> Dict[str, Any]:
        """
        Execute a flow by flow ID.

        Args:
            request_data: Request data containing flow ID and execution parameters
            kc_user_id: Keycloak user identifier obtained from the access token
            api_key: API key from Authorization header for Agent Flow execution

        Returns:
            Flow execution result dictionary
        """
        # Validate user and get data
        user_data = cls.get_user_data(kc_user_id)

        # Validate flow ID
        flow_id = request_data.get("flow_id")
        if not isinstance(flow_id, str) or not flow_id.strip():
            raise agent_flows_http_exception(
                status_code=400,
                code="FLOW_ID_MISSING",
                message="flow_id is required",
            )

        # Create system configuration and executor
        system_config = cls.create_system_config(user_data, api_key)
        executor = FlowExecutor(config=system_config)

        # Execute flow
        variables = request_data.get("variables")
        include_trace = request_data.get("include_trace", False)

        result = await executor.execute_flow(
            flow_source=flow_id,
            variables=variables,
            include_trace=include_trace,
        )

        return result.model_dump(mode="json")

    @classmethod
    async def execute_flow_test(
        cls,
        request_data: Dict[str, Any],
        kc_user_id: str,
        api_key: str,
    ) -> Dict[str, Any]:
        """
        Execute flow in test mode with optional pinned results.

        Args:
            request_data: Request data containing flow definition and test parameters
            kc_user_id: Keycloak user identifier obtained from the access token
            api_key: API key from Authorization header for Agent Flow execution

        Returns:
            Test result dictionary
        """
        reload_env_configs()

        # Validate user and get data
        user_data = cls.get_user_data(kc_user_id)

        # Validate flow definition
        flow_definition = cls.validate_flow_definition(
            request_data.get("flow_definition")
        )

        # Create system configuration and executor
        system_config = cls.create_system_config(user_data, api_key)
        flow_config = FlowConfig(**flow_definition)
        executor = FlowExecutor(config=system_config)

        # Execute flow test
        test_manifest = request_data.get("test_manifest")
        include_trace = request_data.get("include_trace", False)

        result: FlowResult = await executor.test(
            flow_source=flow_config,
            test_manifest=test_manifest,
            include_trace=include_trace,
        )

        return result.model_dump(mode="json")

    @classmethod
    async def validate_flow(
        cls,
        request_data: Dict[str, Any],
        kc_user_id: str,
        api_key: str,
    ) -> Dict[str, Any]:
        """
        Validate flow configuration without execution.

        Args:
            request_data: Request data containing flow definition
            kc_user_id: Keycloak user identifier obtained from the access token
            api_key: API key from Authorization header for Agent Flow execution

        Returns:
            Validation result dictionary
        """
        reload_env_configs()

        # Validate user and get data
        user_data = cls.get_user_data(kc_user_id)

        # Validate flow definition
        flow_definition = cls.validate_flow_definition(
            request_data.get("flow_definition")
        )

        # Create flow configuration and executor for validation
        flow_config = FlowConfig(**flow_definition)
        system_config = cls.create_system_config(user_data, api_key)
        executor = FlowExecutor(config=system_config)

        # Perform validation
        validation_result = await executor.validate_flow(flow_source=flow_config)

        # Check validation results
        if not validation_result.get("valid", False):
            raise agent_flows_http_exception(
                status_code=400,
                code="VALIDATION_FAILED",
                message="The provided flow definition contains errors.",
                details={
                    "overall_errors": validation_result.get("errors", []),
                    "step_validation_summary": validation_result.get(
                        "step_validation_summary", []
                    ),
                },
            )

        return {
            "success": True,
            "step_validation_summary": validation_result.get(
                "step_validation_summary", []
            ),
        }

    @staticmethod
    async def stream_agent_response(
        messages: list[dict[str, str]],
        current_flow: dict | None = None,
        thread_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream agent responses with comprehensive feedback.

        Args:
            messages: List of chat messages
            current_flow: Current flow definition for context
            thread_id: Thread ID for conversation persistence

        Yields:
            Formatted stream response strings
        """
        metadata = {
            "thread_id": thread_id,
            "request_type": "agent_flows_stream",
            "flow_uuid": (current_flow or {}).get("uuid"),
        }

        try:
            with flow_builder_tracing_context(
                project_name=_AGENT_FLOWS_PROJECT, metadata=metadata
            ):
                agent = await get_flow_builder_agent()
                formatted_messages = [
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ]

                # Seed agent state with simplified flow (State Seeding Architecture)
                files_state = {}
                if current_flow:
                    # Simplify flow to reduce token usage and focus agent context
                    simplified_flow = prepare_flow_for_agent(current_flow)
                    files_state["/flow.json"] = {
                        "content": json.dumps(simplified_flow, indent=2).splitlines()
                    }

                # Build config with thread_id for persistence
                config = build_agent_config(thread_id)

                # Prepare agent input with state seeding
                agent_input = {"messages": formatted_messages}
                if files_state:
                    agent_input["files"] = files_state

                async for stream_mode, chunk in agent.astream(
                    agent_input,
                    config=config,
                    stream_mode=["updates", "messages", "custom"],
                ):
                    if stream_mode == "messages":
                        message_chunk, metadata = chunk
                        if (
                            hasattr(message_chunk, "content")
                            and message_chunk.content
                            and not should_filter_message(message_chunk)
                        ):
                            text_content = extract_text_from_content(
                                message_chunk.content
                            )
                            if not text_content:
                                continue
                            yield create_stream_response(
                                event_type="message_chunk",
                                data={
                                    "content": text_content,
                                    "metadata": {
                                        "node": metadata.get("langgraph_node"),
                                        "tags": metadata.get("tags", []),
                                    },
                                },
                                node=metadata.get("langgraph_node"),
                                message_id=getattr(message_chunk, "id", None),
                            )

                    elif stream_mode == "updates":
                        allowed_nodes = {"model", "tools"}
                        for node_name, node_output in chunk.items():
                            if not node_output or node_name not in allowed_nodes:
                                continue

                            def _unwrap(val: Any) -> Any:
                                return val.value if hasattr(val, "value") else val

                            state_updates = {
                                k: _unwrap(v) for k, v in node_output.items() if k != "messages"
                            }

                            files_state = state_updates.get("files")
                            if isinstance(files_state, dict):
                                for key in ("/flow.json", "flow.json"):
                                    if key in files_state:
                                        try:
                                            raw_flow = _unwrap(files_state[key])
                                            if isinstance(raw_flow, dict) and "content" in raw_flow:
                                                raw_flow = raw_flow["content"]
                                            if isinstance(raw_flow, list):
                                                raw_flow = "\n".join(raw_flow)
                                            agent_updated_flow = json.loads(raw_flow)
                                            yield create_stream_response(
                                                event_type="flow_update",
                                                data={"updated_flow": agent_updated_flow},
                                                node=node_name,
                                            )
                                        except json.JSONDecodeError:
                                            yield create_stream_response(
                                                event_type="error",
                                                data={
                                                    "error": "Invalid JSON in flow.json update",
                                                    "error_type": "JSONDecodeError",
                                                },
                                                node=node_name,
                                            )

                            messages_output = _unwrap(node_output.get("messages"))
                            if isinstance(messages_output, list) and messages_output:
                                last_message = messages_output[-1]

                                if (
                                    hasattr(last_message, "content")
                                    and last_message.content
                                    and not should_filter_message(last_message)
                                ):
                                    text_content = extract_text_from_content(
                                        last_message.content
                                    )
                                    if text_content:
                                        yield create_stream_response(
                                            event_type="final_message",
                                            data={
                                                "node": node_name,
                                                "message": text_content,
                                                "message_type": getattr(
                                                    last_message, "type", "ai"
                                                ),
                                            },
                                            node=node_name,
                                            message_id=getattr(last_message, "id", None),
                                        )

                                if (
                                    hasattr(last_message, "tool_calls")
                                    and last_message.tool_calls
                                ):
                                    for tool_call in last_message.tool_calls:
                                        tool_name = tool_call.get("name", "unknown")
                                        if not should_filter_tool_event(tool_name):
                                            yield create_stream_response(
                                                event_type="tool_start",
                                                data={
                                                    "tool_name": tool_name,
                                                    "tool_id": tool_call.get("id", ""),
                                                    "arguments": tool_call.get(
                                                        "args", {}
                                                    ),
                                                },
                                                node=node_name,
                                                message_id=getattr(
                                                    last_message, "id", None
                                                ),
                                            )

                                if hasattr(last_message, "tool_call_id"):
                                    tool_name = getattr(last_message, "name", "unknown")
                                    if not should_filter_tool_event(tool_name):
                                        yield create_stream_response(
                                            event_type="tool_result",
                                            data={
                                                "tool_call_id": getattr(
                                                    last_message, "tool_call_id", ""
                                                ),
                                                "tool_name": tool_name,
                                                "state_updates": state_updates,
                                            },
                                            node=node_name,
                                            message_id=getattr(
                                                last_message, "id", None
                                            ),
                                        )

                yield create_stream_response(
                    event_type="stream_complete", data={"status": "finished"}
                )

        except Exception as e:
            yield create_stream_response(
                event_type="error",
                data={"error": str(e), "error_type": type(e).__name__},
            )

    @staticmethod
    async def get_thread_state(thread_id: str) -> Dict[str, Any]:
        """
        Get the entire state for a given thread.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread state dictionary
        """
        if not thread_id.strip():
            raise agent_flows_http_exception(
                status_code=400,
                code="INVALID_THREAD_ID",
                message="Thread ID cannot be empty",
            )

        try:
            agent = await get_flow_builder_agent()
            config = build_agent_config(thread_id)
            state = await agent.aget_state(config)

            return {
                "thread_id": thread_id,
                "states": getattr(state, "values", {}) if state else {},
            }

        except Exception as e:
            raise agent_flows_http_exception(
                status_code=500, message="Failed to retrieve thread state"
            ) from e
