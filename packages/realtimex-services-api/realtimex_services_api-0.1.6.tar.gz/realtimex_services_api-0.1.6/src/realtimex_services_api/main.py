"""
RealTimeX Services API - Main FastAPI Application

Production-ready FastAPI application providing commonly used services
in a maintainable, modular structure.
"""
import sys

from fastapi import FastAPI

from .modules.a2a_agents import a2a_agents_router
from .modules.agent_flows import agent_flows_router
from .modules.python_interpreter import python_interpreter_router
from .telemetry import initialize_tracing


# Configure Phoenix tracing once for the application process
initialize_tracing()

# Initialize FastAPI application
app = FastAPI(
    title="RealTimeX Services API",
    description="Production-ready API providing commonly used services",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers with appropriate prefixes
app.include_router(agent_flows_router, prefix="/agent-flows")
app.include_router(a2a_agents_router, prefix="/a2a-agents")
app.include_router(python_interpreter_router, prefix="/python-interpreter")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "realtimex-services-api"}


@app.get("/")
async def root():
    """Root endpoint with basic service information."""
    return {
        "service": "RealTimeX Services API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
