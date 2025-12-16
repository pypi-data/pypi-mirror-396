"""Configuration and credentials management for digital employee.

This module provides classes for managing configuration credentials.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from dataclasses import dataclass


@dataclass
class DigitalEmployeeConfiguration:
    """Represents a single configuration for digital employee.

    This class combines both configuration and credential information.

    Attributes:
        key (str): The configuration key identifier (e.g., "GOOGLE_MCP_X_API_KEY", "SPREADSHEET_ID").
        value (str): The configuration value or credential.
    """

    key: str
    value: str
