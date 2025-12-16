"""
Agent Flows Flow Processing Utilities

Utilities for manipulating and processing flow definitions including
simplification for agent context and UI state management.
"""

import copy

# A set of keys to remove from any step object. These are purely for UI state.
UI_KEYS_TO_STRIP = {"isExpanded", "_connections", "ui"}


def _clean_steps_recursively(steps: list[dict]) -> list[dict]:
    """
    Recursively iterates through a list of steps, stripping UI-specific keys
    and cleaning nested step structures.
    """
    if not isinstance(steps, list):
        return []

    cleaned_steps = []
    for step in steps:
        # Create a new step dictionary containing only non-UI keys from the top level.
        cleaned_step = {
            key: value for key, value in step.items() if key not in UI_KEYS_TO_STRIP
        }

        config = cleaned_step.get("config")
        if not isinstance(config, dict):
            cleaned_steps.append(cleaned_step)
            continue

        # Clean the 'ui' key from within the config object itself.
        if "ui" in config:
            del config["ui"]

        # --- Recursively clean nested step arrays within composite nodes ---

        # Conditional: truePath, falsePath
        if "truePath" in config:
            config["truePath"] = _clean_steps_recursively(config.get("truePath", []))
        if "falsePath" in config:
            config["falsePath"] = _clean_steps_recursively(config.get("falsePath", []))

        # Switch: cases[].blocks and defaultBlocks
        if "cases" in config:
            for case in config.get("cases", []):
                if "blocks" in case:
                    case["blocks"] = _clean_steps_recursively(case.get("blocks", []))
        if "defaultBlocks" in config:
            config["defaultBlocks"] = _clean_steps_recursively(
                config.get("defaultBlocks", [])
            )

        # Loop: loopBlocks
        if "loopBlocks" in config:
            config["loopBlocks"] = _clean_steps_recursively(
                config.get("loopBlocks", [])
            )

        cleaned_steps.append(cleaned_step)

    return cleaned_steps


def prepare_flow_for_agent(flow: dict) -> dict:
    """
    Strips frontend-only fields from a flow configuration to reduce token usage
    and focus the agent's context on functional properties.

    This function recursively removes UI-related keys from the main step list,
    from within each step's config, and from all nested step structures.

    Args:
        flow: The complete flow definition, potentially including UI state.

    Returns:
        A deep copy of the flow with only functional fields, optimized for the agent.
    """
    if not flow or not isinstance(flow.get("steps"), list):
        return flow

    flow_for_agent = copy.deepcopy(flow)
    flow_for_agent["steps"] = _clean_steps_recursively(flow_for_agent["steps"])

    return flow_for_agent
