"""
Example usage of the Genesis Core framework.
"""

import asyncio
from genesis_core.orchestrator import Orchestrator, OrchestratorConfig
from genesis_core.governance import BudgetManager
from genesis_core.schemas import AgentProfile


async def main():
    """
    Example demonstrating the Genesis Core functionality.
    """
    print("Genesis Core Example")
    print("=" * 50)

    # Create a budget manager with constraints
    budget_manager = BudgetManager(max_budget=5.0, max_depth=5)

    # Create orchestrator configuration
    config = OrchestratorConfig(
        max_agents=5,
        enable_sub_agents=True
    )

    # Initialize the orchestrator
    orchestrator = Orchestrator(config=config, budget_manager=budget_manager)

    # Example 1: Simple task
    print("\nExample 1: Simple task")
    print("-" * 25)
    result1 = await orchestrator.run(
        goal="Summarize the benefits of renewable energy",
        initial_budget=1.0
    )
    print(f"Result: {result1}")

    # Example 2: Complex task that might require sub-agents
    print("\nExample 2: Complex task (might create sub-agents)")
    print("-" * 50)
    result2 = await orchestrator.run(
        goal="Analyze renewable energy options, compare costs, and write a report",
        initial_budget=3.0
    )
    print(f"Result: {result2}")

    # Example 3: Creating specialized agents directly
    print("\nExample 3: Creating specialized agents")
    print("-" * 40)
    from genesis_core.factory import AgentFactory

    research_agent = AgentFactory.create_research_agent(
        goal="Research solar panel efficiency improvements",
        parent_id="main_task_1"
    )
    print(f"Created research agent: {research_agent['agent_id'] if research_agent else 'Failed'}")

    writing_agent = AgentFactory.create_writing_agent(
        goal="Write a summary of solar panel research",
        parent_id="main_task_1"
    )
    print(f"Created writing agent: {writing_agent['agent_id'] if writing_agent else 'Failed'}")

    print("\nGenesis Core example completed!")


if __name__ == "__main__":
    asyncio.run(main())