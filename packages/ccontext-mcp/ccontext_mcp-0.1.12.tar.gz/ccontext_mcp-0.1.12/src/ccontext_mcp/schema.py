"""Pydantic models for ccontext data structures."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class MilestoneStatus(str, Enum):
    """Milestone status values."""
    DONE = "done"
    ACTIVE = "active"
    PENDING = "pending"


class TaskStatus(str, Enum):
    """Task status values."""
    PLANNED = "planned"
    ACTIVE = "active"
    DONE = "done"


class StepStatus(str, Enum):
    """Step status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# =============================================================================
# Milestone Models
# =============================================================================

class Milestone(BaseModel):
    """A project milestone/phase."""
    id: str = Field(..., description="Milestone ID (M1, M2...)")
    name: str = Field(..., description="Milestone name/goal")
    description: str = Field(..., description="Detailed description (can include checkpoints)")
    status: MilestoneStatus = Field(default=MilestoneStatus.PENDING, description="Status")
    started: Optional[str] = Field(default=None, description="Start date (ISO format)")
    completed: Optional[str] = Field(default=None, description="Completion date (ISO format, done only)")
    outcomes: Optional[str] = Field(default=None, description="Results summary (done only)")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp (ISO format)")


# =============================================================================
# Note and Reference Models
# =============================================================================

class Note(BaseModel):
    """A note entry (lesson, discovery, warning, etc.)."""
    id: str = Field(..., description="Note ID (N001, N002...)")
    content: str = Field(..., description="Note content")
    ttl: int = Field(
        default=30,
        ge=0,
        le=100,
        description="TTL turns (recommended: 10 short-term, 30 normal, 100 long-term; decays)",
    )

    @property
    def expiring(self) -> bool:
        """Check if the note is expiring soon (ttl <= 3)."""
        return self.ttl <= 3


class Reference(BaseModel):
    """A reference entry (useful file/URL)."""
    id: str = Field(..., description="Reference ID (R001, R002...)")
    url: str = Field(..., description="File path or URL")
    note: str = Field(..., description="Description of why this is useful")
    ttl: int = Field(
        default=30,
        ge=0,
        le=100,
        description="TTL turns (recommended: 10 short-term, 30 normal, 100 long-term; decays)",
    )

    @property
    def expiring(self) -> bool:
        """Check if the reference is expiring soon (ttl <= 3)."""
        return self.ttl <= 3


# =============================================================================
# Task Models
# =============================================================================

class Step(BaseModel):
    """A step within a task."""
    id: str = Field(..., description="Step ID (S1, S2...)")
    name: str = Field(..., description="Step name")
    acceptance: str = Field(..., description="Acceptance criteria - when is this step done?")
    status: StepStatus = Field(default=StepStatus.PENDING, description="Step status")


class Task(BaseModel):
    """A task with steps."""
    id: str = Field(..., description="Task ID (T001, T002...)")
    name: str = Field(..., description="Task name")
    goal: str = Field(..., description="Completion criteria")
    status: TaskStatus = Field(default=TaskStatus.PLANNED, description="Task status")
    milestone: Optional[str] = Field(default=None, description="Associated milestone ID (e.g., M2)")
    assignee: Optional[str] = Field(default=None, description="Agent ID")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp (ISO format)")
    steps: list[Step] = Field(default_factory=list, description="Task steps")

    @property
    def current_step(self) -> Optional[Step]:
        """Get the first non-done step."""
        for step in self.steps:
            if step.status != StepStatus.DONE:
                return step
        return None

    @property
    def progress(self) -> float:
        """Calculate progress as done steps / total steps."""
        if not self.steps:
            return 0.0
        done_count = sum(1 for s in self.steps if s.status == StepStatus.DONE)
        return done_count / len(self.steps)


# =============================================================================
# Context Model
# =============================================================================

class Context(BaseModel):
    """The main context structure stored in context.yaml."""
    vision: Optional[str] = Field(default=None, description="Project vision/goal - what we're building")
    sketch: Optional[str] = Field(default=None, description="Static execution blueprint - architecture/strategy only (markdown, no TODO/progress/tasks)")
    milestones: list[Milestone] = Field(default_factory=list, description="Project milestones")
    notes: list[Note] = Field(default_factory=list, description="Notes")
    references: list[Reference] = Field(default_factory=list, description="References")
    meta: dict[str, Any] = Field(default_factory=dict, description="Internal meta/contract for agents")


# =============================================================================
# Presence Models (stored in presence.yaml, gitignored)
# =============================================================================

class AgentPresence(BaseModel):
    """A single agent's presence status.

    Presence captures what an agent is currently thinking/doing in natural language.
    This is subjective, human-readable status - not structured task progress.
    """
    id: str = Field(..., description="Agent ID (e.g., peer-a, worker-1)")
    status: str = Field(default="", description="What the agent is currently doing/thinking (1-2 sentences)")
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="Last update timestamp"
    )


class PresenceData(BaseModel):
    """The presence data structure stored in presence.yaml."""
    agents: list[AgentPresence] = Field(default_factory=list, description="Agent presence list")
    heartbeat_timeout_seconds: int = Field(default=300, description="Timeout for stale detection")


# =============================================================================
# Response Models
# =============================================================================

class TasksSummary(BaseModel):
    """Summary of tasks for get_context response."""
    total: int = Field(default=0, description="Total tasks")
    done: int = Field(default=0, description="Done tasks")
    active: int = Field(default=0, description="Active tasks")
    planned: int = Field(default=0, description="Planned tasks")


class ContextResponse(BaseModel):
    """Response structure for get_context tool."""
    vision: Optional[str] = None
    sketch: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)
    milestones: list[dict] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    references: list[dict] = Field(default_factory=list)
    tasks_summary: TasksSummary = Field(default_factory=TasksSummary)
    active_task: Optional[dict] = None
