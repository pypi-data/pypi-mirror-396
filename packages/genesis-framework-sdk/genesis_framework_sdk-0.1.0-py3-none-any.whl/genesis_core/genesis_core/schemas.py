"""
Data schemas for the Genesis Core framework.

This module defines the core data structures used throughout the framework,
including AgentState, AgentProfile, and MemorySchema.
"""

from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    """
    TypedDict for LangGraph state management.

    Holds conversation history, task queue, budget usage, and other agent state.
    """
    goal: str
    current_task: str
    conversation_history: List[Dict[str, Any]]
    task_queue: List[str]
    results: Dict[str, Any]
    budget_used: float
    remaining_budget: float
    depth: int
    max_depth: int
    agent_id: str
    parent_id: Optional[str]
    children_ids: List[str]
    status: str  # 'pending', 'running', 'completed', 'failed', 'terminated'
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class AgentProfile(BaseModel):
    """
    Pydantic model for agent profiles.

    Defines the structure for agent name, role, and available tools.
    """
    name: str = Field(..., description="The name of the agent")
    role: str = Field(..., description="The role or specialization of the agent")
    tools: List[str] = Field(default_factory=list, description="List of tools available to the agent")
    description: Optional[str] = Field(None, description="Optional description of the agent's capabilities")
    capabilities: List[str] = Field(default_factory=list, description="List of capabilities the agent possesses")

    class Config:
        extra = "forbid"


class MemorySchema(BaseModel):
    """
    Pydantic model for Qdrant vector payload structure.

    Defines the structure for storing agent memories in Qdrant vector database.
    """
    id: str = Field(..., description="Unique identifier for the memory entry")
    agent_id: str = Field(..., description="ID of the agent that generated this memory")
    content: str = Field(..., description="The actual memory content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the memory")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when memory was created")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the memory")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")

    class Config:
        extra = "forbid"


class BudgetState(BaseModel):
    """
    Pydantic model for tracking budget state across agent operations.
    """
    total_budget: float = Field(..., description="Total budget allocated for the operation")
    remaining_budget: float = Field(..., description="Budget remaining for the operation")
    max_depth: int = Field(..., description="Maximum allowed recursion depth")
    current_depth: int = Field(..., description="Current recursion depth")
    cost_per_call: float = Field(default=0.0, description="Estimated cost per LLM call")
    spending_log: List[Dict[str, Any]] = Field(default_factory=list, description="Log of all spending events")

    class Config:
        extra = "forbid"


class SpendingEvent(BaseModel):
    """
    Pydantic model for recording individual spending events.
    """
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    agent_id: str = Field(..., description="ID of the agent that incurred the cost")
    operation: str = Field(..., description="Type of operation that incurred the cost")
    cost: float = Field(..., description="Amount of cost incurred")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the cost")

    class Config:
        extra = "forbid"