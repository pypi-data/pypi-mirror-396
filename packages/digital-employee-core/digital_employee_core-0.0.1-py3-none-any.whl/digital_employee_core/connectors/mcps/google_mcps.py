"""Google MCPs for Digital Employee Core.

This module provides pre-configured MCP instances for Google services
that can be easily imported and used in Digital Employee implementations.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from glaip_sdk import MCP

# Google Calendar MCP
google_calendar_mcp = MCP(
    name="digital_employee_google_calendar_mcp",
    description="MCP for Google Calendar Operation for DE",
    transport="http",
    config={"url": "https://default.com/google_calendar/mcp"},
)

# Google Docs MCP
google_docs_mcp = MCP(
    name="digital_employee_google_docs_mcp",
    description="MCP for Google Docs Operation for DE",
    transport="http",
    config={"url": "https://default.com/google_docs/mcp"},
)

# Google Drive MCP
google_drive_mcp = MCP(
    name="digital_employee_google_drive_mcp",
    description="MCP for Google Drive Operation for DE",
    transport="http",
    config={"url": "https://default.com/google_drive/mcp"},
)

# Google Mail MCP
google_mail_mcp = MCP(
    name="digital_employee_google_mail_mcp",
    description="MCP for Google Mail Operation for DE",
    transport="http",
    config={"url": "https://default.com/google_mail/mcp"},
)

# Google Sheets MCP
google_sheets_mcp = MCP(
    name="digital_employee_google_sheets_mcp",
    description="MCP for Google Sheets Operation for DE",
    transport="http",
    config={"url": "https://default.com/google_sheets/mcp"},
)

# Convenience list of all Google MCPs
ALL_GOOGLE_MCPS = [
    google_calendar_mcp,
    google_docs_mcp,
    google_drive_mcp,
    google_mail_mcp,
    google_sheets_mcp,
]
