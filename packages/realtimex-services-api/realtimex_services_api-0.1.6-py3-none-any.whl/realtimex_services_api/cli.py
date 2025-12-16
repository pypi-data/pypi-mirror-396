"""
CLI entry point for RealTimeX Services API

Provides command-line interface for running the FastAPI application
using uvicorn server with production-ready configuration.
"""

import uvicorn

from .main import app


def main() -> None:
    """Main entry point for the CLI application."""
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=False, workers=1)
