"""Configuration template loader and processor.

This module provides utilities for loading and processing configuration templates
from YAML files, replacing placeholders with values from DigitalEmployeeConfiguration objects.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

import re
from pathlib import Path
from typing import Any

import yaml

from digital_employee_core.configuration.configuration import DigitalEmployeeConfiguration

# Configuration template filenames
MCP_CONFIGS_TEMPLATE = "mcp_configs.yaml"
TOOL_CONFIGS_TEMPLATE = "tool_configs.yaml"


class ConfigTemplateLoader:
    """Loads and processes configuration templates from YAML files.

    This class handles loading YAML configuration templates and replacing
    placeholders with actual values from DigitalEmployeeConfiguration objects.

    Attributes:
        template_dir (Path): Path to the directory containing template files.
    """

    def __init__(self, template_dir: str | Path | None = None):
        """Initialize the ConfigTemplateLoader.

        Args:
            template_dir (str | Path | None, optional): Path to template directory. Defaults to config_templates
                in the package directory.
        """
        if template_dir is None:
            # Default to config_templates directory in the package
            package_dir = Path(__file__).parent.parent
            template_dir = package_dir / "config_templates"

        self.template_dir = Path(template_dir)

    def load_template(self, filename: str) -> dict[str, Any]:
        """Load a YAML template file.

        Args:
            filename (str): Name of the template file (e.g., 'mcp_configs.yaml').

        Returns:
            dict[str, Any]: Dictionary containing the template configuration.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        template_path = self.template_dir / filename
        return self.load_template_from_path(template_path)

    def load_template_from_path(self, filepath: str | Path) -> dict[str, Any]:
        """Load a YAML template file from an absolute path.

        Args:
            filepath (str | Path): Absolute path to the template file.

        Returns:
            dict[str, Any]: Dictionary containing the template configuration.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        template_path = Path(filepath)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def merge_configs(
        base_config: dict[str, dict[str, Any]],
        additional_config: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Merge two configuration dictionaries.

        The additional_config will override values in base_config for matching keys.
        New keys in additional_config will be added to the result.
        Performs recursive deep merge for nested dictionaries.

        Args:
            base_config (dict[str, dict[str, Any]]): Base configuration dictionary.
            additional_config (dict[str, dict[str, Any]]): Additional configuration to merge.

        Returns:
            dict[str, dict[str, Any]]: Merged configuration dictionary.
        """

        def _deep_merge(base: dict[str, Any], additional: dict[str, Any]) -> dict[str, Any]:
            """Recursively merge two dictionaries."""
            result = base.copy()
            for key, value in additional.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = _deep_merge(result[key], value)
                else:
                    # Override or add new key
                    result[key] = value
            return result

        return _deep_merge(base_config, additional_config)

    def _replace_placeholders(
        self,
        template: dict[str, Any],
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, Any]:
        """Replace placeholders in template with configuration values.

        Placeholders are in format <PLACEHOLDER_KEY> and are replaced with
        values from DigitalEmployeeConfiguration objects matching the key.

        Args:
            template (dict[str, Any]): Template dictionary with placeholders.
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, Any]: Dictionary with placeholders replaced by actual values.
        """
        # Create a mapping of keys to values from configurations
        config_map: dict[str, str] = {}
        for config in configurations:
            config_map[config.key] = config.value

        def replace_value(value: Any) -> Any:
            """Recursively replace placeholders in values."""
            if isinstance(value, str):
                # Find all placeholders in format <KEY>
                placeholders = re.findall(r"<([^>]+)>", value)
                result = value
                for placeholder in placeholders:
                    if placeholder in config_map:
                        # Replace the placeholder with the actual value
                        result = result.replace(f"<{placeholder}>", config_map[placeholder])
                return result
            elif isinstance(value, dict):
                return {k: replace_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_value(item) for item in value]
            else:
                return value

        return replace_value(template)

    def load_mcp_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, Any]]:
        """Load MCP configuration template and replace placeholders.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping MCP names to their configurations.
        """
        template = self.load_template(MCP_CONFIGS_TEMPLATE)
        return self._replace_placeholders(template, configurations)

    def load_tool_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, Any]]:
        """Load tool configuration template and replace placeholders.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping tool names to their configurations.
        """
        template = self.load_template(TOOL_CONFIGS_TEMPLATE)
        return self._replace_placeholders(template, configurations)
