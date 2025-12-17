"""
Orchestrator for the Genesis Core framework.

This module implements the LangGraph State Graph that analyzes user prompts
and decides if sub-agents are needed for recursive agent orchestration.
"""

import asyncio
from typing import Dict, Any, List, Optional, Literal
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from .schemas import AgentState, AgentProfile
from .governance import BudgetManager
from .factory import spawn_agent


class OrchestratorConfig(BaseModel):
    """
    Configuration for the orchestrator.
    """
    max_agents: int = 10
    enable_sub_agents: bool = True
    default_agent_profile: Optional[AgentProfile] = None


class Orchestrator:
    """
    Main orchestrator class that manages the creation and execution of agents using LangGraph.
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None, budget_manager: Optional[BudgetManager] = None, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator.

        Args:
            config: Configuration for the orchestrator
            budget_manager: Budget manager to enforce constraints
            llm_config: Configuration for the LLM provider (BYOK - Bring Your Own Key)
        """
        self.config = config or OrchestratorConfig()
        self.budget_manager = budget_manager or BudgetManager()
        self.llm_config = llm_config or {}
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph with nodes and edges.

        Returns:
            Configured StateGraph
        """
        # Define the state graph
        graph = StateGraph(AgentState)

        # Add nodes to the graph
        graph.add_node("analyze", self._analyze_task)
        graph.add_node("create_sub_agents", self._create_sub_agents)
        graph.add_node("execute_agent", self._execute_agent)
        graph.add_node("aggregate_results", self._aggregate_results)

        # Set the entry point
        graph.set_entry_point("analyze")

        # Add conditional edges
        graph.add_conditional_edges(
            "analyze",
            self._should_create_sub_agents,
            {
                "sub_agents": "create_sub_agents",
                "execute": "execute_agent",
                "end": END
            }
        )

        graph.add_edge("create_sub_agents", "execute_agent")
        graph.add_edge("execute_agent", "aggregate_results")
        graph.add_conditional_edges(
            "aggregate_results",
            self._should_continue,
            {
                "continue": "analyze",
                "end": END
            }
        )

        return graph

    def _should_create_sub_agents(self, state: AgentState) -> Literal["sub_agents", "execute", "end"]:
        """
        Determine if sub-agents should be created based on the current state.

        Args:
            state: Current agent state

        Returns:
            Decision on next step in the workflow
        """
        # Analyze the goal and determine if it requires sub-agents
        goal = state["goal"].lower()

        # Keywords that suggest the need for sub-agents
        sub_agent_keywords = [
            "analyze", "research", "compare", "multiple", "several",
            "different", "various", "complex", "break down", "decompose"
        ]

        # Check if the goal contains keywords that suggest sub-agents are needed
        has_sub_agent_keywords = any(keyword in goal for keyword in sub_agent_keywords)

        # Check if we're within budget and depth constraints
        within_budget = self.budget_manager.check_budget(0.1)  # Minimal cost check
        within_depth = self.budget_manager.check_depth(state["depth"] + 1)

        # Check if we haven't exceeded the max agent limit
        agent_count = len(state["children_ids"]) + 1

        if (has_sub_agent_keywords and
            within_budget and
            within_depth and
            agent_count < self.config.max_agents and
            self.config.enable_sub_agents):
            return "sub_agents"
        elif within_budget and within_depth:
            return "execute"
        else:
            return "end"

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if the orchestration should continue.

        Args:
            state: Current agent state

        Returns:
            Decision to continue or end
        """
        # Check if there are more tasks in the queue
        if state["task_queue"]:
            # Check budget and depth constraints
            within_budget = self.budget_manager.check_budget(0.1)  # Minimal cost check
            within_depth = self.budget_manager.check_depth(state["depth"])

            if within_budget and within_depth:
                return "continue"

        return "end"

    def _analyze_task(self, state: AgentState) -> Dict[str, Any]:
        """
        Analyze the current task and prepare for execution.

        Args:
            state: Current agent state

        Returns:
            Updated state with analysis results
        """
        # Update the state timestamp
        state["updated_at"] = state.get("updated_at", state["created_at"])

        # Log the analysis
        print(f"Analyzing task: {state['goal']}")

        # Return the updated state
        return {"current_task": f"Analyzed: {state['goal']}"}

    def _create_sub_agents(self, state: AgentState) -> Dict[str, Any]:
        """
        Create sub-agents based on the current task analysis.

        Args:
            state: Current agent state

        Returns:
            Updated state with new sub-agents
        """
        # Check depth constraints before creating sub-agents
        try:
            self.budget_manager.increment_depth()
        except Exception:
            # If we can't increment depth, we can't create sub-agents
            return {"status": "failed_depth_limit"}

        # Determine what types of sub-agents to create based on the goal
        goal = state["goal"].lower()
        sub_agents = []

        # Create specialized agents based on the goal
        if "research" in goal or "analyze" in goal:
            sub_agents.append(AgentProfile(
                name="ResearchAgent",
                role="Research Specialist",
                tools=["web_search", "document_analysis"],
                description="Specialized in research and information gathering"
            ))

        if "write" in goal or "draft" in goal or "create" in goal:
            sub_agents.append(AgentProfile(
                name="WriterAgent",
                role="Content Creator",
                tools=["content_generation", "editing"],
                description="Specialized in writing and content creation"
            ))

        if "code" in goal or "program" in goal or "develop" in goal:
            sub_agents.append(AgentProfile(
                name="CodeAgent",
                role="Software Developer",
                tools=["code_generation", "debugging", "testing"],
                description="Specialized in software development"
            ))

        # If no specific agents were identified, create a general agent
        if not sub_agents:
            sub_agents.append(AgentProfile(
                name="GeneralAgent",
                role="General Problem Solver",
                tools=["general_reasoning", "planning"],
                description="General purpose agent for various tasks"
            ))

        # Spawn the sub-agents
        new_children_ids = []
        for agent_profile in sub_agents:
            try:
                # Track the cost of creating an agent
                self.budget_manager.track_spending(
                    agent_id=state["agent_id"],
                    operation="create_agent",
                    cost=0.05,  # Estimated cost for creating an agent
                    details={"agent_type": agent_profile.role}
                )

                # Spawn the agent
                child_agent = spawn_agent(
                    goal=f"Sub-task for: {state['goal']}",
                    agent_profile=agent_profile,
                    parent_id=state["agent_id"],
                    budget_manager=self.budget_manager
                )

                if child_agent:
                    new_children_ids.append(child_agent["agent_id"])
            except Exception as e:
                print(f"Failed to create sub-agent: {e}")
                continue

        # Update the state with new children
        updated_children = state["children_ids"] + new_children_ids

        return {"children_ids": updated_children, "status": "sub_agents_created"}

    def _execute_agent(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the current agent task.

        Args:
            state: Current agent state

        Returns:
            Updated state with execution results
        """
        # Track the cost of execution
        try:
            self.budget_manager.track_spending(
                agent_id=state["agent_id"],
                operation="execute_agent",
                cost=0.1,  # Estimated cost for execution
                details={"task": state["current_task"]}
            )
        except Exception as e:
            return {"status": "failed_budget", "error": str(e)}

        # Simulate agent execution
        # In a real implementation, this would call the LLM and process the results
        execution_result = {
            "status": "completed",
            "result": f"Executed task: {state['current_task']}",
            "timestamp": state["updated_at"]
        }

        # Update results in state
        results = state.get("results", {})
        results[state["current_task"]] = execution_result

        return {"results": results, "status": "executed"}

    def _aggregate_results(self, state: AgentState) -> Dict[str, Any]:
        """
        Aggregate results from all agents in the network.

        Args:
            state: Current agent state

        Returns:
            Updated state with aggregated results
        """
        # In a real implementation, this would gather results from all child agents
        # For now, we'll just return the current results
        return {"status": "results_aggregated"}

    async def run(self, goal: str, initial_budget: Optional[float] = None) -> Dict[str, Any]:
        """
        Run the orchestrator with a specific goal.

        Args:
            goal: The goal or task for the agent to accomplish
            initial_budget: Optional initial budget for the operation

        Returns:
            Results from the agent execution
        """
        # Set initial budget if provided
        if initial_budget is not None:
            self.budget_manager = BudgetManager(max_budget=initial_budget)

        # Create initial state
        initial_state = {
            "goal": goal,
            "current_task": goal,
            "conversation_history": [],
            "task_queue": [],
            "results": {},
            "budget_used": 0.0,
            "remaining_budget": self.budget_manager.get_current_budget_state().remaining_budget,
            "depth": 0,
            "max_depth": self.budget_manager.get_current_budget_state().max_depth,
            "agent_id": f"agent_{id(self)}",
            "parent_id": None,
            "children_ids": [],
            "status": "pending",
            "created_at": asyncio.get_event_loop().time(),
            "updated_at": asyncio.get_event_loop().time(),
            "metadata": {}
        }

        # Run the graph
        try:
            result = await self.compiled_graph.ainvoke(initial_state)
            return result
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def save_state_to_memory(self, state: AgentState, memory_manager) -> str:
        """
        Save the current agent state to memory.

        Args:
            state: Current agent state to save
            memory_manager: Memory manager to use for storage

        Returns:
            ID of the saved memory
        """
        content = f"Agent State for {state['agent_id']}: {state['goal']}"
        metadata = {
            "agent_id": state["agent_id"],
            "status": state["status"],
            "depth": state["depth"],
            "budget_used": state["budget_used"]
        }

        memory_id = await memory_manager.store_memory(
            agent_id=state["agent_id"],
            content=content,
            metadata=metadata,
            tags=["agent_state", "checkpoint"]
        )

        return memory_id

    def run_sync(self, goal: str, initial_budget: Optional[float] = None) -> Dict[str, Any]:
        """
        Synchronous version of the run method.

        Args:
            goal: The goal or task for the agent to accomplish
            initial_budget: Optional initial budget for the operation

        Returns:
            Results from the agent execution
        """
        import threading

        if threading.current_thread() is threading.main_thread():
            # If we're in the main thread, create a new event loop
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(self.run(goal, initial_budget))
        else:
            # If we're in a worker thread, run in a temporary loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.run(goal, initial_budget))
            finally:
                loop.close()