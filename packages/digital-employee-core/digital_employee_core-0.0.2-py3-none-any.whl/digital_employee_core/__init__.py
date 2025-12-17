"""Digital employee Core package.

This package provides the core functionality for building and managing
digital employees with support for tools, MCPs, and configurations.
"""

from digital_employee_core.config_templates import ConfigTemplateLoader
from digital_employee_core.configuration import DigitalEmployeeConfiguration
from digital_employee_core.constants import (
    GPT_4_1_MODEL_NAME,
    GPT_5_1_HIGH_MODEL_NAME,
    GPT_5_1_LOW_MODEL_NAME,
    GPT_5_1_MEDIUM_MODEL_NAME,
    GPT_5_1_MODEL_NAME,
    GPT_5_LOW_MODEL_NAME,
    GPT_5_MINI_MODEL_NAME,
    GPT_5_MINIMAL_MODEL_NAME,
    GPT_5_MODEL_NAME,
)
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
    # Model constants
    "GPT_4_1_MODEL_NAME",
    "GPT_5_MODEL_NAME",
    "GPT_5_MINIMAL_MODEL_NAME",
    "GPT_5_MINI_MODEL_NAME",
    "GPT_5_LOW_MODEL_NAME",
    "GPT_5_1_MODEL_NAME",
    "GPT_5_1_LOW_MODEL_NAME",
    "GPT_5_1_MEDIUM_MODEL_NAME",
    "GPT_5_1_HIGH_MODEL_NAME",
]
