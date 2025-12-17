"""
Factory for the Genesis Core framework.

This module implements the agent spawning logic that dynamically instantiates
new nodes in the graph based on the Orchestrator's decision.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from .schemas import AgentProfile, AgentState
from .governance import BudgetManager


def spawn_agent(
    goal: str,
    agent_profile: AgentProfile,
    parent_id: Optional[str] = None,
    budget_manager: Optional[BudgetManager] = None
) -> Optional[Dict[str, Any]]:
    """
    Dynamically instantiate a new agent node in the graph based on the Orchestrator's decision.

    Args:
        goal: The goal or task for the new agent
        agent_profile: Profile defining the agent's role and capabilities
        parent_id: ID of the parent agent (if any)
        budget_manager: Budget manager to enforce constraints

    Returns:
        Dictionary containing the new agent's information, or None if spawning failed
    """
    try:
        # Generate a unique ID for the new agent
        agent_id = f"agent_{str(uuid.uuid4()).replace('-', '')[:8]}"

        # Determine depth based on parent
        depth = 1 if parent_id is None else 2  # Simplified depth calculation

        # Create the agent state
        agent_state: AgentState = {
            "goal": goal,
            "current_task": goal,
            "conversation_history": [],
            "task_queue": [],
            "results": {},
            "budget_used": 0.0,
            "remaining_budget": budget_manager.get_current_budget_state().remaining_budget if budget_manager else 10.0,
            "depth": depth,
            "max_depth": budget_manager.get_current_budget_state().max_depth if budget_manager else 10,
            "agent_id": agent_id,
            "parent_id": parent_id,
            "children_ids": [],
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {
                "profile": agent_profile.dict()
            }
        }

        # If budget manager is provided, track the creation cost
        if budget_manager:
            try:
                budget_manager.track_spending(
                    agent_id=agent_id,
                    operation="spawn_agent",
                    cost=0.05,  # Estimated cost for spawning an agent
                    details={
                        "agent_type": agent_profile.role,
                        "parent_agent": parent_id
                    }
                )
            except Exception as e:
                print(f"Failed to track spending for agent {agent_id}: {e}")
                return None

        # Return the agent information
        return {
            "agent_id": agent_id,
            "profile": agent_profile,
            "state": agent_state,
            "parent_id": parent_id,
            "depth": depth
        }

    except Exception as e:
        print(f"Error spawning agent: {e}")
        return None


class AgentFactory:
    """
    A factory class for creating different types of specialized agents.
    """

    @staticmethod
    def create_research_agent(goal: str, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a research-focused agent.

        Args:
            goal: The research goal
            parent_id: ID of the parent agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        profile = AgentProfile(
            name="ResearchAgent",
            role="Research Specialist",
            tools=["web_search", "document_analysis", "data_extraction"],
            description="Specialized in research and information gathering",
            capabilities=["information_retrieval", "analysis", "synthesis"]
        )

        return spawn_agent(goal, profile, parent_id)

    @staticmethod
    def create_writing_agent(goal: str, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a writing-focused agent.

        Args:
            goal: The writing goal
            parent_id: ID of the parent agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        profile = AgentProfile(
            name="WriterAgent",
            role="Content Creator",
            tools=["content_generation", "editing", "proofreading"],
            description="Specialized in writing and content creation",
            capabilities=["drafting", "editing", "style_adaptation"]
        )

        return spawn_agent(goal, profile, parent_id)

    @staticmethod
    def create_code_agent(goal: str, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a coding-focused agent.

        Args:
            goal: The coding goal
            parent_id: ID of the parent agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        profile = AgentProfile(
            name="CodeAgent",
            role="Software Developer",
            tools=["code_generation", "debugging", "testing", "refactoring"],
            description="Specialized in software development",
            capabilities=["programming", "debugging", "testing"]
        )

        return spawn_agent(goal, profile, parent_id)

    @staticmethod
    def create_general_agent(goal: str, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a general-purpose agent.

        Args:
            goal: The general goal
            parent_id: ID of the parent agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        profile = AgentProfile(
            name="GeneralAgent",
            role="General Problem Solver",
            tools=["general_reasoning", "planning", "decision_making"],
            description="General purpose agent for various tasks",
            capabilities=["reasoning", "planning", "problem_solving"]
        )

        return spawn_agent(goal, profile, parent_id)

    @staticmethod
    def create_agent_by_role(
        role: str,
        goal: str,
        parent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an agent based on a specific role.

        Args:
            role: The role to create (research, writing, code, general)
            goal: The goal for the agent
            parent_id: ID of the parent agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        role_map = {
            "research": AgentFactory.create_research_agent,
            "writing": AgentFactory.create_writing_agent,
            "code": AgentFactory.create_code_agent,
            "general": AgentFactory.create_general_agent,
        }

        create_func = role_map.get(role.lower())
        if create_func:
            return create_func(goal, parent_id)

        # Default to general agent if role not found
        return AgentFactory.create_general_agent(goal, parent_id)

    @staticmethod
    def create_agent(
        goal: str,
        name: str,
        orchestrator: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new agent with the specified goal and name.

        Args:
            goal: The goal or task for the new agent
            name: The name of the agent
            orchestrator: The orchestrator instance to manage this agent

        Returns:
            Dictionary containing the new agent's information, or None if creation failed
        """
        profile = AgentProfile(
            name=name,
            role=f"{name} Agent",
            tools=["general_reasoning", "planning", "decision_making"],
            description=f"Specialized agent for: {goal}",
            capabilities=["reasoning", "planning", "problem_solving"]
        )

        # Extract parent_id and budget_manager from orchestrator if available
        parent_id = getattr(orchestrator, 'parent_id', None)
        budget_manager = getattr(orchestrator, 'budget_manager', None)

        return spawn_agent(goal, profile, parent_id, budget_manager)