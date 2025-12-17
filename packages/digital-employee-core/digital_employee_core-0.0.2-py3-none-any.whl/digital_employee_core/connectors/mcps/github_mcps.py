"""GitHub MCPs for Digital Employee Core.

This module provides pre-configured MCP instances for GitHub services
that can be easily imported and used in Digital Employee implementations.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from glaip_sdk import MCP

# GitHub MCP
github_mcp = MCP(
    name="digital_employee_github_mcp",
    description="MCP for GitHub Operation for DE",
    transport="http",
    config={"url": "https://default.com/github/mcp"},
)
