"""
Shared utilities for RealTimeX Services API

Provides reusable functions for configuration management, user fetching,
and other common operations across the application.
"""

import os
from typing import Any, Dict

import requests
from dotenv import dotenv_values

# Global configuration variables
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_API_KEY = ""


def get_user_dir() -> str:
    """Get the user directory for realtimex.ai configuration."""
    return os.path.join(os.path.expanduser("~"), ".realtimex.ai")


def get_cache_dir():
    return os.path.join(os.path.expanduser("~"),".cache")

def get_env_file_path() -> str:
    """Get the path to the environment development file."""
    return os.path.join(get_user_dir(), "Resources", "server", ".env.development")


def get_workspace_path(workspace_name: str) -> str:
    """Return the absolute path to a named workspace, creating the directory if needed.

    Workspaces are stored under ~/.realtimex.ai/Resources/server/storage and can be
    reused by any feature that needs a persistent sandbox.
    """
    workspace_dir = os.path.join(
        get_user_dir(), "Resources", "server", "storage", workspace_name
    )
    os.makedirs(workspace_dir, exist_ok=True)
    return workspace_dir


def get_uv_executable():
    import platform
    os_type = platform.system()
    if os_type == "Windows":
        return os.path.join(get_user_dir(),"Resources","envs","Scripts","uv.exe")

    return os.path.join(get_user_dir(),"Resources","envs","bin","uv")

def load_env_configs():
    from dotenv import dotenv_values

    env_file_path = get_env_file_path()
    if os.path.exists(env_file_path):
        env_configs = dotenv_values(env_file_path)
        return env_configs
    return None

def reload_env_configs() -> None:
    """
    Reload environment configurations and update global OpenAI settings.

    Reads from ~/.realtimex.ai/Resources/server/.env.development and updates
    global configuration variables based on LLM_PROVIDER setting.
    """
    global DEFAULT_OPENAI_BASE_URL, DEFAULT_OPENAI_API_KEY

    env_configs = load_env_configs()

    if not env_configs:
        return

    llm_provider = env_configs.get("LLM_PROVIDER")

    if llm_provider == "openai":
        DEFAULT_OPENAI_API_KEY = env_configs.get("OPEN_AI_KEY", "")
        DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
    elif llm_provider == "realtimexai":
        DEFAULT_OPENAI_BASE_URL = env_configs.get("REALTIMEX_AI_BASE_PATH", "")
        DEFAULT_OPENAI_API_KEY = env_configs.get("REALTIMEX_AI_API_KEY", "")
    elif llm_provider == "ollama":
        DEFAULT_OPENAI_BASE_URL = env_configs.get("OLLAMA_BASE_PATH", "")
        DEFAULT_OPENAI_API_KEY = ""


def get_realtimex_ai_config() -> tuple[str, str]:
    """
    Get RealTimeX AI configuration from environment file.

    Returns:
        Tuple of (api_key, base_path)

    Raises:
        ValueError: If required configuration is missing
    """
    env_file_path = get_env_file_path()

    if not os.path.exists(env_file_path):
        raise ValueError(f"Environment file not found: {env_file_path}")

    env_configs = dotenv_values(env_file_path)
    api_key = env_configs.get("REALTIMEX_AI_API_KEY", "").strip()
    base_path = env_configs.get("REALTIMEX_AI_BASE_PATH", "").strip()

    if not api_key:
        raise ValueError(
            "REALTIMEX_AI_API_KEY is required but not found in environment configuration"
        )
    if not base_path:
        raise ValueError(
            "REALTIMEX_AI_BASE_PATH is required but not found in environment configuration"
        )

    return api_key, base_path


def get_mcp_proxy_config() -> tuple[str, str]:
    """
    Get MCP proxy configuration from environment file.

    Returns:
        Tuple of (api_key, linked_account_owner_id)

    Raises:
        ValueError: If required configuration is missing
    """
    env_file_path = get_env_file_path()

    if not os.path.exists(env_file_path):
        raise ValueError(f"Environment file not found: {env_file_path}")

    env_configs = dotenv_values(env_file_path)
    api_key = env_configs.get("MCP_PROXY_API_KEY", "").strip()
    linked_account_owner_id = env_configs.get(
        "MCP_PROXY_LINKED_ACCOUNT_OWNER_ID", ""
    ).strip()

    if not api_key:
        raise ValueError(
            "MCP_PROXY_API_KEY is required but not found in environment configuration"
        )
    if not linked_account_owner_id:
        raise ValueError(
            "MCP_PROXY_LINKED_ACCOUNT_OWNER_ID is required but not found in environment configuration"
        )

    return api_key, linked_account_owner_id


def get_realtimex_user(kc_user_id: str) -> Dict[str, Any] | None:
    """
    Fetch RealTimeX user data by Keycloak user ID.

    Args:
        kc_user_id: Keycloak user identifier

    Returns:
        User data dictionary or None if not found/error occurred
    """
    try:
        url = f"http://127.0.0.1:8002/users/{kc_user_id}"
        response = requests.get(url, headers={}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching user {kc_user_id}: {e}")
        return None


# Initialize configurations on module import
reload_env_configs()
