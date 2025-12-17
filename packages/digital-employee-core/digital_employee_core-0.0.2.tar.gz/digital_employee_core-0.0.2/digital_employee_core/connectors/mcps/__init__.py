"""MCPs package for Digital Employee Core.

This package provides pre-configured MCP instances for various services.
"""

from digital_employee_core.connectors.mcps.github_mcps import github_mcp
from digital_employee_core.connectors.mcps.google_mcps import (
    ALL_GOOGLE_MCPS,
    google_calendar_mcp,
    google_docs_mcp,
    google_drive_mcp,
    google_mail_mcp,
    google_sheets_mcp,
)
from digital_employee_core.connectors.mcps.sql_mcps import sql_tool_mcp

__all__ = [
    "google_calendar_mcp",
    "google_docs_mcp",
    "google_drive_mcp",
    "google_mail_mcp",
    "google_sheets_mcp",
    "ALL_GOOGLE_MCPS",
    "github_mcp",
    "sql_tool_mcp",
]
