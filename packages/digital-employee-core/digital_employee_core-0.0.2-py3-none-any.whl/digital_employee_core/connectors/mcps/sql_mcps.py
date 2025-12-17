"""SQL MCPs for Digital Employee Core.

This module provides pre-configured MCP instances for SQL database services
that can be easily imported and used in Digital Employee implementations.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from glaip_sdk import MCP

# SQL Tool MCP
sql_tool_mcp = MCP(
    name="digital_employee_sql_tool_mcp",
    description="MCP for SQL Tool Operation for DE",
    transport="http",
    config={"url": "https://default.com/sql_tool/mcp"},
)
