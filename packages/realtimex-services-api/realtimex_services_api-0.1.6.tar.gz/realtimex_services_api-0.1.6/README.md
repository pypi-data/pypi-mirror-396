# RealTimeX Services API

A production-ready FastAPI application providing commonly used services in a maintainable, modular structure. This project is built on a feature-based architecture to ensure scalability and clear separation of concerns.

## Features

- **Agent Flows**: A self-contained module providing testing, validation, and streaming endpoints for flow execution.
- **Feature-Based Modular Architecture**: Code is organized by business domain (e.g., "agent flows") for high cohesion and low coupling.
- **Production Ready**: Proper error handling, type hints, and dependency management.
- **Health Monitoring**: Built-in health check endpoints for observability.
- **API Versioning**: Endpoints are versioned (e.g., `/api/v1/...`) for long-term stability.
- **OpenAPI Documentation**: Auto-generated and interactive API documentation.

## Project Structure

The project follows a feature-based (vertical slice) architecture. All code related to a specific business domain is co-located within a "module".

```
src/realtimex_services_api/
├── __init__.py
├── main.py                 # FastAPI app initialization and router inclusion
├── cli.py                  # CLI entry point
├── core/                   # Shared application-wide logic (config, dependencies)
└── modules/                # Top-level directory for all feature modules
    ├── __init__.py
    └── agent_flows/        # A self-contained module for the "Agent Flows" feature
        ├── __init__.py
        ├── api.py          # FastAPI router and HTTP-related logic
        ├── service.py      # Core business logic, decoupled from the web framework
        ├── schemas.py      # Pydantic models and data contracts
        └── utils/          # Utility functions specific to this module
            ├── __init__.py
            └── ...
```

## Installation

```bash
# Install dependencies
uv sync

# Or using pip
pip install -e .
```

## Usage

### Running the Server

```bash
# Using the CLI command
realtimex-services-api

# Or directly with Python
python -m realtimex_services_api.cli

# Or with uvicorn directly
uvicorn realtimex_services_api.main:app --host 0.0.0.0 --port 8004
```

### API Endpoints

- **GET /** - Root endpoint with service information
- **GET /health** - Health check for monitoring
- **GET /docs** - OpenAPI documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation
- **POST /api/v1/agent-flows/action/test** - Execute flow in test mode
- **POST /api/v1/agent-flows/action/validate** - Validate flow configuration
- **POST /api/v1/agent-flows/chat/stream** - Stream chat responses

## Development

### Adding a New Feature Module

The architecture makes adding new, independent features straightforward.

1.  **Create the Module Directory**:
    Create a new folder inside `src/realtimex_services_api/modules/`.
    ```bash
    mkdir src/realtimex_services_api/modules/new_feature
    ```

2.  **Create Standard Files**:
    Inside the new directory, create the essential files: `__init__.py`, `api.py` (for the router), `service.py` (for business logic), and `schemas.py` (for Pydantic models).

3.  **Implement the Logic**:
    -   Define your FastAPI router in `api.py`.
    -   Write your business logic in `service.py`, keeping it decoupled from FastAPI.
    -   Define your request/response models in `schemas.py`.

4.  **Include the Router in `main.py`**:
    Import and include the new router from your module's `api.py` file.

    ```python
    # In main.py
    from .modules.new_feature.api import router as new_feature_router

    app.include_router(
        new_feature_router,
        prefix="/api/v1/new-feature",
        tags=["New Feature"]
    )
    ```

### Code Standards

- **Type Hints**: All functions should include proper type annotations.
- **Docstrings**: Public functions and modules should have clear docstrings.
- **Error Handling**: The service layer raises domain-specific exceptions; the API layer translates them into HTTP error responses.
- **Import Organization**: Follow PEP 8 import ordering.

## Configuration

The application reads configuration from `~/.realtimex.ai/Resources/server/.env.development`:

- `LLM_PROVIDER`: openai, realtimexai, or ollama
- `OPEN_AI_KEY`: OpenAI API key (when using openai provider)
- `REALTIMEX_AI_BASE_PATH`: Base URL for RealTimeX AI
- `REALTIMEX_AI_API_KEY`: API key for RealTimeX AI
- `OLLAMA_BASE_PATH`: Base URL for Ollama

## Architecture Decisions

### Why This Structure?

1.  **High Cohesion, Low Coupling**: All code for a single feature (API, logic, models) lives in one place, making it self-contained. Modules have minimal dependencies on each other.
2.  **Scalability**: The application grows by adding new, independent modules. This prevents the complexity of the project from growing exponentially.
3.  **Improved Developer Experience**: It's easy to find all code related to a feature. A developer can understand the scope of a feature by looking inside its module directory.
4.  **Clear Boundaries**: The separation between the HTTP layer (`api.py`) and the business logic layer (`service.py`) is strictly enforced, improving testability and reusability.
5.  **Easy to Refactor or Extract**: A self-contained feature module is much easier to modify, delete, or extract into its own microservice if needed.

## License

Internal RealTimeX project - All rights reserved.