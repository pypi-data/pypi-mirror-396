"""Core digital employee orchestrator.

This module provides the base DigitalEmployee class that manages agents,
tools, and MCPs. It implements the ConfigBuilder interface to
provide configuration building capabilities.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from typing import Any

from glaip_sdk import MCP, Agent, Tool

from digital_employee_core.config_templates.loader import ConfigTemplateLoader
from digital_employee_core.configuration.configuration import (
    DigitalEmployeeConfiguration,
)
from digital_employee_core.constants import DEFAULT_MODEL_NAME
from digital_employee_core.identity.identity import DigitalEmployeeIdentity


class DigitalEmployee:
    """Core digital employee orchestrator.

    This class manages the lifecycle of a digital employee, including
    initialization, deployment, and execution of agents with tools and MCPs.
    Provides methods for building tool and MCP configurations from YAML templates.

    Attributes:
        identity (DigitalEmployeeIdentity): The digital employee's identity.
        tools (list[Tool]): List of tools the digital employee can use.
        sub_agents (list[Agent]): List of sub-agents (for future use).
        mcps (list[MCP]): List of MCPs the digital employee can use.
        configurations (list[DigitalEmployeeConfiguration]): List of configuration objects for tools and MCPs.
        model (str): Model identifier to use for the agent.
        agent (Agent | None): The main agent instance.
        config_loader (ConfigTemplateLoader): The configuration template loader instance.
    """

    def __init__(  # noqa: PLR0913
        self,
        identity: DigitalEmployeeIdentity,
        tools: list[Tool] | None = None,
        sub_agents: list[Agent] | None = None,
        mcps: list[MCP] | None = None,
        configurations: list[DigitalEmployeeConfiguration] | None = None,
        model: str = DEFAULT_MODEL_NAME,
    ):
        """Initialize the digital employee.

        Args:
            identity (DigitalEmployeeIdentity): The digital employee's identity.
            tools (list[Tool] | None, optional): List of tools the digital employee can use. Defaults to None.
            sub_agents (list[Agent] | None, optional): List of sub-agents (for future use). Defaults to None.
            mcps (list[MCP] | None, optional): List of MCPs the digital employee can use. Defaults to None.
            configurations (list[DigitalEmployeeConfiguration] | None, optional): List of configuration objects
                for tools and MCPs. Defaults to None.
            model (str, optional): Model identifier to use for the agent. Defaults to DEFAULT_MODEL_NAME.
        """
        self.identity = identity
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.mcps = mcps or []
        self.configurations = configurations or []
        self.model = model
        self.agent: Agent | None = None
        self.config_loader = ConfigTemplateLoader()

    def add_tools(self, tools: list[Tool]) -> None:
        """Add tools to the digital employee.

        Args:
            tools (list[Tool]): List of tools to add.
        """
        self.tools.extend(tools)

    def remove_tools(self, tools: list[Tool]) -> None:
        """Remove tools from the digital employee.

        Args:
            tools (list[Tool]): List of tools to remove.
        """
        tools_to_remove = set(tools)
        self.tools = [tool for tool in self.tools if tool not in tools_to_remove]

    def add_mcps(self, mcps: list[MCP]) -> None:
        """Add MCPs to the digital employee.

        Args:
            mcps (list[MCP]): List of MCPs to add.
        """
        self.mcps.extend(mcps)

    def remove_mcps(self, mcps: list[MCP]) -> None:
        """Remove MCPs from the digital employee.

        Args:
            mcps (list[MCP]): List of MCPs to remove.
        """
        mcps_to_remove = set(mcps)
        self.mcps = [mcp for mcp in self.mcps if mcp not in mcps_to_remove]

    def add_sub_agents(self, sub_agents: list[Agent]) -> None:
        """Add sub-agents to the digital employee.

        Args:
            sub_agents (list[Agent]): List of sub-agents to add.
        """
        self.sub_agents.extend(sub_agents)

    def remove_sub_agents(self, sub_agents: list[Agent]) -> None:
        """Remove sub-agents from the digital employee by name.

        Args:
            sub_agents (list[Agent]): List of sub-agents to remove.
        """
        agent_names_to_remove = {agent.name for agent in sub_agents if agent.name}
        self.sub_agents = [agent for agent in self.sub_agents if agent.name not in agent_names_to_remove]

    def build_prompt(self) -> str:
        """Build the prompt for the agent.

        This method can be overridden by subclasses to provide custom
        prompts based on the digital employee's identity and job.
        Always includes the digital employee's name, email, and language preferences
        in the prompt to ensure identity awareness.

        Returns:
            str: The prompt string for the agent.
        """
        # Build identity information with language
        language_names = [lang.value for lang in self.identity.languages]

        if len(language_names) > 1:
            language_list = ", ".join(language_names[:-1]) + f" and {language_names[-1]}"
            language_instruction = (
                f"You must respond only in the following languages: {language_list}. "
                f"Choose the most appropriate language based on the user's input or context."
            )
        else:
            language_instruction = f"You must respond only in {language_names[0]} language."

        identity_prefix = (
            f"You are {self.identity.name} ({self.identity.email}), {self.identity.job.title}. "
            f"{language_instruction}"
        )

        return f"{identity_prefix}\n\n{self.identity.job.instruction}"

    def deploy(self) -> None:
        """Deploy the digital employee.

        This method initializes the agent with tools and MCPs,
        applies configurations to MCPs and tools, and deploys it to the AI platform.
        """
        if self.configurations:
            tool_configs = self.build_tool_config(self.configurations)
            mcp_configs = self.build_mcp_config(self.configurations)
            configured_mcps = self._apply_mcp_configs(self.mcps, mcp_configs)
            configured_tools = self._apply_tool_configs(self.tools, tool_configs)
        else:
            configured_mcps = self.mcps
            configured_tools = self.tools

        self.agent = Agent(
            name=self.identity.name,
            description=self.identity.job.description,
            instruction=self.build_prompt(),
            tools=configured_tools,
            agents=self.sub_agents,
            mcps=configured_mcps,
            model=self.model,
        )

        self.agent.deploy()

    def run(
        self,
        message: str,
        configurations: list[DigitalEmployeeConfiguration] | None = None,
    ) -> str:
        """Run the digital employee with a message.

        Args:
            message (str): The message/prompt to send to the digital employee.
            configurations (list[DigitalEmployeeConfiguration] | None, optional): List of configuration objects.
                Defaults to None.

        Returns:
            str: The agent's response as a string.

        Raises:
            RuntimeError: If the agent has not been deployed.
        """
        if self.agent is None:
            raise RuntimeError("Agent has not been deployed. Call deploy() before run().")

        configurations = configurations or []
        runtime_config = self._build_runtime_configs(configurations)

        return self.agent.run(message=message, runtime_config=runtime_config)

    def build_tool_config(self, configurations: list[DigitalEmployeeConfiguration]) -> dict[str, dict[str, Any]]:
        """Build tool configuration based on identity and configurations.

        This method loads tool configuration templates from YAML and replaces
        placeholders with values from DigitalEmployeeConfiguration objects. Subclasses can
        override this to provide custom logic and merge with parent configs.

        Example for subclasses:
            def build_tool_config(self, configurations):
                # Get base configs from parent
                base_configs = super().build_tool_config(configurations)

                # Load additional configs for this subclass
                additional = self.config_loader.load_tool_configs(configurations)

                # Merge them
                return self.config_loader.merge_configs(base_configs, additional)

        Args:
            configurations: List of configuration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping tool names to their configuration dictionaries.
        """
        return self.config_loader.load_tool_configs(configurations)

    def build_mcp_config(self, configurations: list[DigitalEmployeeConfiguration]) -> dict[str, dict[str, Any]]:
        """Build MCP configuration based on identity and configurations.

        This method loads MCP configuration templates from YAML and replaces
        placeholders with values from DigitalEmployeeConfiguration objects. Subclasses can
        override this to provide custom logic and merge with parent configs.

        Example for subclasses:
            def build_mcp_config(self, configurations):
                # Get base configs from parent
                base_configs = super().build_mcp_config(configurations)

                # Load additional configs for this subclass
                additional = self.config_loader.load_mcp_configs(configurations)

                # Merge them
                return self.config_loader.merge_configs(base_configs, additional)

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of configuration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping MCP names to their configuration dictionaries.
        """
        return self.config_loader.load_mcp_configs(configurations)

    def _apply_mcp_configs(
        self,
        mcps: list[MCP],
        mcp_configs: dict[str, dict[str, Any]],
    ) -> list[MCP]:
        """Apply configurations to MCPs.

        This method updates the config and authentication attributes of MCPs
        based on the provided configuration dictionary. Only updates MCPs
        that have matching configurations.

        Args:
            mcps (list[MCP]): List of MCP instances.
            mcp_configs (dict[str, dict[str, Any]]): Dictionary mapping MCP names to their configurations.

        Returns:
            list[MCP]: List of MCPs with configurations applied.
        """
        return [self._apply_single_mcp_config(mcp, mcp_configs) for mcp in mcps]

    def _apply_single_mcp_config(self, mcp: MCP, mcp_configs: dict[str, dict[str, Any]]) -> MCP:
        """Apply configuration to a single MCP.

        Args:
            mcp (MCP): MCP instance to configure.
            mcp_configs (dict[str, dict[str, Any]]): Dictionary mapping MCP names to their configurations.

        Returns:
            MCP: MCP with configuration applied.
        """
        if not (mcp.name and mcp.name in mcp_configs):
            return mcp

        config_data = mcp_configs[mcp.name]

        if config_data.get("config"):
            if mcp.config is None:
                mcp.config = {}
            mcp.config.update(config_data["config"])

        if config_data.get("authentication"):
            if mcp.authentication is None:
                mcp.authentication = {}
            mcp.authentication.update(config_data["authentication"])

        return mcp

    def _apply_tool_configs(
        self,
        tools: list[Tool],
        tool_configs: dict[str, dict[str, Any]],
    ) -> list[Tool]:
        """Apply configurations to tools.

        This method updates tool configurations based on the provided
        configuration dictionary. Only updates tools that have matching
        configurations and a config attribute.

        Args:
            tools (list[Tool]): List of tool names (strings) or Tool objects.
            tool_configs (dict[str, dict[str, Any]]): Dictionary mapping tool names to their configurations.

        Returns:
            list[Tool]: List of tools with configurations applied.
        """
        configured_tools = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "config"):
                if tool.name and tool.name in tool_configs:
                    config_data = tool_configs[tool.name]
                    if tool.config is None:
                        tool.config = {}
                    tool.config.update(config_data)

            configured_tools.append(tool)

        return configured_tools

    def _filter_tool_configs(
        self,
        all_tool_configs: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Filter tool configs to only include tools used by the agent.

        Args:
            all_tool_configs (dict[str, dict[str, Any]]): All available tool configurations.

        Returns:
            dict[str, dict[str, Any]]: Filtered tool configurations for tools used by the agent.
        """
        return {
            name: config
            for name, config in all_tool_configs.items()
            if any(
                (hasattr(tool, "name") and tool.name == name) or (isinstance(tool, str) and tool == name)
                for tool in self.agent.tools
            )
        }

    def _filter_mcp_configs(
        self,
        all_mcp_configs: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Filter MCP configs to only include MCPs used by the agent.

        Args:
            all_mcp_configs (dict[str, dict[str, Any]]): All available MCP configurations.

        Returns:
            dict[str, dict[str, Any]]: Filtered MCP configurations for MCPs used by the agent.
        """
        return {
            name: config
            for name, config in all_mcp_configs.items()
            if any(
                (hasattr(mcp, "name") and mcp.name == name) or (isinstance(mcp, str) and mcp == name)
                for mcp in self.agent.mcps
            )
        }

    def _build_runtime_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """Build runtime configurations for tools and MCPs.

        This method builds all configurations and filters them to only include
        tools and MCPs that are actually used by the agent.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of configuration objects.

        Returns:
            dict[str, dict[str, dict[str, Any]]]: Dictionary with 'tool_configs' and 'mcp_configs' keys.
        """
        all_tool_configs = self.build_tool_config(configurations)
        all_mcp_configs = self.build_mcp_config(configurations)

        return {
            "tool_configs": self._filter_tool_configs(all_tool_configs),
            "mcp_configs": self._filter_mcp_configs(all_mcp_configs),
        }
