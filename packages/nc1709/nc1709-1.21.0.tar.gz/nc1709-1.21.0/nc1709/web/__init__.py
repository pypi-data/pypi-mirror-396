"""
NC1709 Web Dashboard
Local web interface for NC1709 AI assistant
"""

from .server import create_app, run_server

__all__ = ["create_app", "run_server"]
