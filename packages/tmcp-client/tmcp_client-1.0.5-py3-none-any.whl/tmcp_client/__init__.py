"""TMCP Client - Lightweight MCP client for TowardsAGI MCP servers.

A minimal, efficient client for connecting to TowardsAGI MCP servers via HTTP API.
Designed for use with Claude, Cursor, and other MCP-compatible applications.

Copyright (c) 2024 TowardsAGI.AI UK Ltd
"""

from .bridge import TMCPBridge

__version__ = "1.0.5"
__author__ = "TowardsAGI.AI UK Ltd"
__email__ = "support@towardsagi.ai"
__description__ = "Lightweight MCP client for TowardsAGI MCP servers"

__all__ = [
    "TMCPBridge",
]
