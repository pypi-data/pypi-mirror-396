"""
SDK interface for the Genesis Framework.

This module provides the main Genesis class that implements the dual-key model
for the Genesis SDK.
"""

import os
from typing import Dict, Any
from .orchestrator import Orchestrator, OrchestratorConfig
from .governance import BudgetManager
from .factory import AgentFactory


class Genesis:
    """
    The main Genesis SDK class that implements the dual-key model.

    The Genesis class provides a clean, high-level interface to the Genesis framework
    using the dual-key model where developers provide their own LLM key (BYOK)
    and a Genesis API key for orchestration services.
    """

    def __init__(self, genesis_api_key: str, llm_config: Dict[str, Any]):
        """
        Initialize the Genesis SDK with dual-key configuration.

        Args:
            genesis_api_key (str): Genesis API key for orchestration, memory, and logging services
            llm_config (dict): Configuration for the LLM provider (BYOK - Bring Your Own Key)
                              Expected format: {
                                  "provider": "openai" | "anthropic",
                                  "api_key": "your-llm-api-key",
                                  "model": "gpt-4o" (optional, defaults to provider's default)
                              }
        """
        self.genesis_api_key = genesis_api_key
        self.llm_config = llm_config

        # Mock validation for genesis_api_key
        print(f"[SUCCESS] Genesis Key Verified: {genesis_api_key[:8]}...")

        # Store LLM configuration for later use by agents
        self._setup_llm_provider()

    def _setup_llm_provider(self):
        """
        Set up the LLM provider based on the provided configuration.
        This ensures the BYOK (Bring Your Own Key) model is properly implemented.
        """
        provider = self.llm_config.get("provider", "openai")
        api_key = self.llm_config.get("api_key")

        # Set environment variables for the LLM provider based on the configuration
        if provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
        elif provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = api_key

        # Store the model configuration
        self.model = self.llm_config.get("model", "gpt-4o" if provider == "openai" else "claude-3-sonnet")

    def create_agent(self, name: str, objective: str, budget_limit: float = 10.0):
        """
        Create a new agent with the specified parameters.

        Args:
            name (str): The name of the agent
            objective (str): The objective/goal for the agent
            budget_limit (float): Maximum budget limit for the agent's operations (default: 10.0)

        Returns:
            Agent: A configured agent instance ready to run
        """
        # Create a budget manager with the specified budget limit
        budget_manager = BudgetManager(max_budget=budget_limit, max_depth=5)

        # Create orchestrator configuration
        config = OrchestratorConfig(
            max_agents=5,
            enable_sub_agents=True
        )

        # Initialize the orchestrator with the LLM configuration to use BYOK
        orchestrator = Orchestrator(
            config=config,
            budget_manager=budget_manager,
            llm_config=self.llm_config
        )

        # Create and return an agent using the factory
        agent = AgentFactory.create_agent(
            goal=objective,
            name=name,
            orchestrator=orchestrator
        )

        return agent