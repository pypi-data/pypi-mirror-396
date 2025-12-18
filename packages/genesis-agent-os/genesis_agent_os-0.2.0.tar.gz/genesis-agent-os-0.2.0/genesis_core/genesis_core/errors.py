"""
Custom error classes for the Genesis Core framework.
"""

class BudgetExceededError(Exception):
    """Raised when the budget limit is exceeded during agent execution."""

    def __init__(self, message: str = "Budget limit exceeded", remaining_budget: float = 0.0):
        self.remaining_budget = remaining_budget
        super().__init__(message)


class DepthLimitExceededError(Exception):
    """Raised when the recursion depth limit is exceeded."""

    def __init__(self, message: str = "Recursion depth limit exceeded", max_depth: int = 0):
        self.max_depth = max_depth
        super().__init__(message)


class AgentCreationError(Exception):
    """Raised when there's an error creating a new agent."""
    pass


class AgentExecutionError(Exception):
    """Raised when there's an error during agent execution."""
    pass


class MemoryOperationError(Exception):
    """Raised when there's an error with memory operations."""
    pass