"""Digital employee Core package.

This package provides the core functionality for building and managing
digital employees with support for tools, MCPs, and configurations.
"""

from digital_employee_core.config_templates import ConfigTemplateLoader
from digital_employee_core.configuration import DigitalEmployeeConfiguration
from digital_employee_core.digital_employee import DigitalEmployee
from digital_employee_core.identity import (
    DigitalEmployeeIdentity,
    DigitalEmployeeJob,
    DigitalEmployeeSupervisor,
)

__all__ = [
    # Core classes
    "ConfigTemplateLoader",
    "DigitalEmployee",
    # Identity classes
    "DigitalEmployeeIdentity",
    "DigitalEmployeeJob",
    "DigitalEmployeeSupervisor",
    # Configuration classes
    "DigitalEmployeeConfiguration",
]
