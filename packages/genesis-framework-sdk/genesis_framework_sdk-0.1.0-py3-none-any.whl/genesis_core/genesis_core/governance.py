"""
Governance layer for the Genesis Core framework.

This module implements the Budget Governance Layer that prevents infinite loops
and cost overruns with Max Budget/Depth constraints.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .schemas import BudgetState, SpendingEvent
from .errors import BudgetExceededError, DepthLimitExceededError


class BudgetManager:
    """
    Manages budget constraints and tracks spending across agent operations.
    """

    def __init__(self, max_budget: float = 10.0, max_depth: int = 10):
        """
        Initialize the BudgetManager with constraints.

        Args:
            max_budget: Maximum budget allowed for operations (in USD)
            max_depth: Maximum recursion depth allowed
        """
        self.budget_state = BudgetState(
            total_budget=max_budget,
            remaining_budget=max_budget,
            max_depth=max_depth,
            current_depth=0,
            spending_log=[]
        )

    def check_budget(self, cost: float) -> bool:
        """
        Check if the requested cost exceeds the remaining budget.

        Args:
            cost: The cost to check against remaining budget

        Returns:
            True if budget is sufficient, False otherwise
        """
        return self.budget_state.remaining_budget >= cost

    def check_depth(self, new_depth: Optional[int] = None) -> bool:
        """
        Check if the requested depth exceeds the maximum allowed depth.

        Args:
            new_depth: The new depth to check (if None, checks current depth + 1)

        Returns:
            True if depth is within limits, False otherwise
        """
        depth_to_check = new_depth if new_depth is not None else self.budget_state.current_depth + 1
        return depth_to_check <= self.budget_state.max_depth

    def track_spending(self, agent_id: str, operation: str, cost: float, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Track spending for an agent operation and raise exception if budget is exceeded.

        Args:
            agent_id: ID of the agent incurring the cost
            operation: Type of operation that incurred the cost
            cost: Amount of cost incurred
            details: Additional details about the cost

        Raises:
            BudgetExceededError: If the operation would exceed the budget limit
        """
        if details is None:
            details = {}

        # Check if this operation would exceed the budget
        if not self.check_budget(cost):
            raise BudgetExceededError(
                f"Operation '{operation}' would exceed budget. "
                f"Remaining budget: ${self.budget_state.remaining_budget:.2f}, "
                f"Cost: ${cost:.2f}",
                remaining_budget=self.budget_state.remaining_budget
            )

        # Create a spending event
        spending_event = SpendingEvent(
            agent_id=agent_id,
            operation=operation,
            cost=cost,
            details=details
        )

        # Update budget state
        self.budget_state.spending_log.append(spending_event.dict())
        self.budget_state.remaining_budget -= cost
        self.budget_state.total_budget -= (self.budget_state.total_budget - self.budget_state.remaining_budget)

    def increment_depth(self) -> None:
        """
        Increment the current recursion depth and check limits.

        Raises:
            DepthLimitExceededError: If the depth limit is exceeded
        """
        new_depth = self.budget_state.current_depth + 1
        if not self.check_depth(new_depth):
            raise DepthLimitExceededError(
                f"Recursion depth would exceed limit of {self.budget_state.max_depth}. "
                f"Current depth: {self.budget_state.current_depth}",
                max_depth=self.budget_state.max_depth
            )

        self.budget_state.current_depth = new_depth

    def decrement_depth(self) -> None:
        """
        Decrement the current recursion depth.
        """
        if self.budget_state.current_depth > 0:
            self.budget_state.current_depth -= 1

    def get_current_budget_state(self) -> BudgetState:
        """
        Get the current budget state.

        Returns:
            Current budget state information
        """
        return self.budget_state

    def reset(self) -> None:
        """
        Reset the budget state to initial values.
        """
        initial_remaining = self.budget_state.total_budget
        self.budget_state = BudgetState(
            total_budget=self.budget_state.total_budget,
            remaining_budget=initial_remaining,
            max_depth=self.budget_state.max_depth,
            current_depth=0,
            spending_log=[]
        )