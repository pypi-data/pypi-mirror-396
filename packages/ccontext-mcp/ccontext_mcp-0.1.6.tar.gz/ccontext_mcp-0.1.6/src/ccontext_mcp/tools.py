"""MCP tool implementations for ccontext."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .schema import (
    Context,
    ContextResponse,
    Milestone,
    MilestoneStatus,
    Note,
    Reference,
    Step,
    StepStatus,
    Task,
    TasksSummary,
    TaskStatus,
)
from .storage import ContextStorage


# =============================================================================
# Tool Descriptions - Critical for Agent adoption
# =============================================================================

TOOL_DESCRIPTIONS = {
    # Context - THE entry point
    "get_context": (
        "**Read this first or risk repeating work and missing critical decisions.** "
        "Your execution memory that persists across sessions. Contains: vision (goal), "
        "sketch (plan), milestones (phases), tasks (current work), notes (lessons), "
        "and references (key files). Other agents update this too - check regularly. "
        "Returns 'version' for change detection and 'hints' for suggested actions."
    ),

    # Vision/Sketch tools - project blueprint
    "update_vision": (
        "Set or update the project vision - what we're building. "
        "This is a short, fixed statement that captures the project goal. "
        "Example: 'Build secure SaaS platform for 10K users'"
    ),
    "update_sketch": (
        "Update the execution blueprint (markdown). "
        "Use for architecture diagrams, current phase, upcoming work, risks, and decisions. "
        "Recommended sections: ## Architecture, ## Current Phase, ## Upcoming, ## History. "
        "Update on: phase transitions, architecture changes, major risks, strategic decisions. "
        "Avoid updating for: daily progress (use task status), small fixes, routine task switches."
    ),

    # Presence tools - agent coordination
    "get_presence": (
        "Get all agents' current status - what they're doing/thinking. "
        "Essential for multi-agent coordination. Each agent has: ID, status (natural language), last update time."
    ),
    "update_my_status": (
        "**Tell other agents what you're doing** - they can't see your work otherwise. "
        "1-2 sentences describing your current focus, intent, or blockers. "
        "Example: 'Debugging JWT edge case, found timezone issue' or 'Blocked on schema confirmation'."
    ),
    "set_idle": (
        "Clear your status when you're done working or handing off. "
        "This signals to peers that you're not actively focused on anything."
    ),

    # Milestone tools - project timeline
    "create_milestone": (
        "Start a new project phase that persists across sessions. "
        "Use when beginning major work (e.g., 'Phase 1: Core Implementation'). "
        "Milestones create a timeline showing project evolution."
    ),
    "update_milestone": (
        "Modify a milestone's details or advance its status (pending→active→done). "
        "Use when scope changes or when starting work on a pending phase."
    ),
    "complete_milestone": (
        "Close a milestone and record what was accomplished. "
        "Outcomes become permanent project history visible to future sessions."
    ),
    "remove_milestone": (
        "Delete a cancelled or mistaken milestone. "
        "Completed milestones should be kept as project history."
    ),

    # Task tools - work tracking
    "list_tasks": (
        "Find tasks by status (planned/active/done) or assignee. "
        "Use to see what work exists and check progress across sessions."
    ),
    "create_task": (
        "Break down work into trackable steps that persist across sessions. "
        "Use when starting work that spans multiple actions or needs progress tracking."
    ),
    "update_task": (
        "Update task progress - change status, mark steps done, or modify details. "
        "Keeps execution state accurate for session handoffs and work resumption."
    ),
    "delete_task": (
        "Remove a cancelled or mistaken task. "
        "Completed tasks auto-archive after 7 days - no need to delete them."
    ),

    # Note tools - knowledge preservation
    "add_note": (
        "Preserve important knowledge for future sessions - lessons, warnings, decisions. "
        "High scores (50-100) persist longer; low scores decay and auto-archive. "
        "Example: 'API rate limit is 100/min - batch requests to avoid throttling'"
    ),
    "update_note": (
        "Refresh a note's score to prevent decay, or update its content. "
        "Use when a note is still valuable but its score is getting low."
    ),
    "remove_note": (
        "Delete an obsolete note immediately. "
        "Prefer letting low-value notes decay naturally via score system."
    ),

    # Reference tools - navigation bookmarks
    "add_reference": (
        "Bookmark important file paths or URLs for quick navigation. "
        "High scores persist longer. Use for: key source files, API docs, configs. "
        "Example: 'src/core/auth.py - OAuth implementation'"
    ),
    "update_reference": (
        "Refresh a reference's score to prevent decay, or update its details. "
        "Use when a reference is still valuable but its score is getting low."
    ),
    "remove_reference": (
        "Delete an obsolete reference immediately. "
        "Prefer letting outdated references decay naturally via score system."
    ),
}


class ContextTools:
    """Implementation of ccontext MCP tools."""

    def __init__(self, root: Optional[Path] = None):
        """Initialize tools with project root directory."""
        self.storage = ContextStorage(root)

    # =========================================================================
    # Context Tool
    # =========================================================================

    def get_context(self) -> dict[str, Any]:
        """Get the full execution context with version tracking.

        Each call triggers score decay for notes and references.

        Returns a dict with:
        - version: Content-based hash for change detection
        - context: The actual context data (milestones, notes, refs, tasks)
        - hints: Suggestions for filling incomplete context (only when applicable)

        Agents can cache the version and check if context changed
        by comparing versions on subsequent calls.
        """
        context = self.storage.load_context()

        # Decay scores and archive if needed
        context, archived_notes, archived_refs = self.storage.decay_scores(context)

        if archived_notes or archived_refs:
            self.storage.archive_entries(archived_notes, archived_refs)

        self.storage.save_context(context)

        # Archive old tasks
        self.storage.archive_old_tasks()

        # Get milestones for response (limited done + all active/pending)
        milestones = self.storage.get_milestones_for_response(context)

        # Build tasks summary
        tasks = self.storage.list_tasks(include_archived=False)
        summary = TasksSummary(
            total=len(tasks),
            done=len([t for t in tasks if t.status == TaskStatus.DONE]),
            active=len([t for t in tasks if t.status == TaskStatus.ACTIVE]),
            planned=len([t for t in tasks if t.status == TaskStatus.PLANNED]),
        )

        # Find active task
        active_task = None
        for task in tasks:
            if task.status == TaskStatus.ACTIVE:
                active_task = self._task_to_dict(task)
                break

        # Build response
        response = ContextResponse(
            vision=context.vision,
            sketch=context.sketch,
            milestones=[
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "status": m.status.value,
                    "started": m.started,
                    "completed": m.completed,
                    "outcomes": m.outcomes,
                    "updated_at": m.updated_at,
                }
                for m in milestones
            ],
            notes=[
                {
                    "id": n.id,
                    "content": n.content,
                    "score": n.score,
                    "expiring": n.expiring,
                }
                for n in context.notes
            ],
            references=[
                {
                    "id": r.id,
                    "url": r.url,
                    "note": r.note,
                    "score": r.score,
                    "expiring": r.expiring,
                }
                for r in context.references
            ],
            tasks_summary=summary,
            active_task=active_task,
        )

        # Generate hints for incomplete context
        hints = self._generate_context_hints(context, milestones, tasks)

        # Return with version for change detection
        result = {
            "version": self.storage.compute_version(),
            "context": response.model_dump(),
        }

        # Only include hints if there are any
        if hints:
            result["hints"] = hints

        # Add getting_started guide for truly empty context
        if self._is_empty_context(context, tasks):
            result["getting_started"] = self._get_getting_started_guide()

        return result

    def _generate_context_hints(
        self,
        context: Context,
        milestones: list[Milestone],
        tasks: list[Task]
    ) -> list[str]:
        """Generate hints for filling incomplete context.

        Returns a list of actionable suggestions based on what's missing or stale.
        These hints help agents understand what context would be valuable to add.
        """
        hints = []
        now = datetime.now(timezone.utc)

        # Vision check - most fundamental
        if not context.vision:
            hints.append(
                "Consider setting a vision with update_vision() - "
                "a short statement of what we're building helps keep work focused."
            )

        # Sketch check - execution blueprint
        if not context.sketch:
            hints.append(
                "Consider creating a sketch with update_sketch() - "
                "an execution blueprint (architecture, current phase, upcoming work) "
                "helps maintain continuity across sessions."
            )

        # Milestones check - project phases
        active_milestones = [m for m in milestones if m.status == MilestoneStatus.ACTIVE]
        if not milestones:
            hints.append(
                "No milestones defined yet. Consider using create_milestone() "
                "to define project phases - this creates a visible timeline of progress."
            )
        elif not active_milestones:
            pending = [m for m in milestones if m.status == MilestoneStatus.PENDING]
            if pending:
                hints.append(
                    f"No active milestone. Consider activating {pending[0].id} "
                    "with update_milestone() to mark the current work phase."
                )
        else:
            # Check freshness of active milestone
            for m in active_milestones:
                if m.updated_at:
                    days_stale = self._days_since(m.updated_at, now)
                    if days_stale is not None and days_stale >= 7:
                        hints.append(
                            f"Milestone {m.id} active for {days_stale} days with no updates. "
                            "Still in progress, or ready to complete?"
                        )
                        break  # Only one freshness hint per category

        # Tasks check - work tracking
        active_tasks = [t for t in tasks if t.status == TaskStatus.ACTIVE]
        if not tasks:
            hints.append(
                "No tasks defined. Consider using create_task() to break down "
                "your current work into trackable steps."
            )
        elif not active_tasks:
            planned = [t for t in tasks if t.status == TaskStatus.PLANNED]
            if planned:
                hints.append(
                    f"No active task. Consider activating {planned[0].id} "
                    "with update_task(status='active') to track current work."
                )
        else:
            # Check freshness of active tasks
            for t in active_tasks:
                if t.updated_at:
                    days_stale = self._days_since(t.updated_at, now)
                    if days_stale is not None and days_stale >= 3:
                        hints.append(
                            f"Task {t.id} active for {days_stale} days with no step updates. "
                            "Still working on it?"
                        )
                        break  # Only one freshness hint per category

            # Check if any active task has all steps done
            for t in active_tasks:
                if t.steps and all(s.status == StepStatus.DONE for s in t.steps):
                    hints.append(
                        f"Task {t.id} has all steps done but is still active. "
                        "Ready to mark as done?"
                    )
                    break

        # Notes check - knowledge preservation (only hint if context is otherwise populated)
        if (context.vision or context.sketch) and not context.notes:
            hints.append(
                "Consider adding notes with add_note() to preserve lessons, "
                "warnings, or important decisions for future sessions."
            )

        # Check for expiring notes
        expiring_notes = [n for n in context.notes if n.score <= 3]
        if expiring_notes:
            count = len(expiring_notes)
            hints.append(
                f"{count} note(s) expiring soon (score ≤ 3). "
                "Boost with update_note(score=...) if still relevant."
            )

        return hints

    def _days_since(self, iso_timestamp: str, now: datetime) -> Optional[int]:
        """Calculate days since a timestamp. Returns None if parsing fails."""
        try:
            # Handle both Z suffix and +00:00
            ts = iso_timestamp.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = now - dt
            return delta.days
        except (ValueError, TypeError):
            return None

    def _is_empty_context(self, context: Context, tasks: list[Task]) -> bool:
        """Check if context is truly empty (new project, no setup yet).

        Returns True only when there's nothing meaningful configured:
        no vision, no sketch, no milestones, and no tasks.
        """
        return (
            not context.vision
            and not context.sketch
            and not context.milestones
            and not tasks
        )

    def _get_getting_started_guide(self) -> dict[str, Any]:
        """Return onboarding guide for new/empty context.

        Provides clear first steps to help agents understand how to use ccontext
        effectively. This only appears when context is truly empty.
        """
        return {
            "message": (
                "This is a fresh project with no execution context yet. "
                "ccontext helps you maintain continuity across sessions and "
                "coordinate with other agents."
            ),
            "recommended_first_steps": [
                {
                    "order": 1,
                    "action": "update_vision",
                    "why": "Set a clear goal - keeps work focused across sessions",
                    "example": "Build secure SaaS platform for 10K users",
                },
                {
                    "order": 2,
                    "action": "create_milestone",
                    "why": "Define the first project phase - creates visible timeline",
                    "example": "Phase 1: Core Implementation",
                },
                {
                    "order": 3,
                    "action": "create_task",
                    "why": "Break down work into trackable steps",
                    "example": "Set up project structure with auth scaffolding",
                },
                {
                    "order": 4,
                    "action": "update_my_status",
                    "why": "Tell other agents what you're working on",
                    "example": "Starting project setup, reviewing requirements",
                },
            ],
            "tip": (
                "Call get_context() at session start and after major work. "
                "Other agents may have updated context since your last session."
            ),
        }

    # =========================================================================
    # Vision/Sketch Tools
    # =========================================================================

    def update_vision(self, vision: str) -> dict[str, Any]:
        """Update the project vision."""
        context = self.storage.load_context()
        context.vision = vision
        self.storage.save_context(context)

        return {
            "success": True,
            "vision": vision,
            "version": self.storage.compute_version(),
        }

    def update_sketch(self, sketch: str) -> dict[str, Any]:
        """Update the execution blueprint (sketch)."""
        context = self.storage.load_context()
        context.sketch = sketch
        self.storage.save_context(context)

        return {
            "success": True,
            "version": self.storage.compute_version(),
        }

    # =========================================================================
    # Presence Tools
    # =========================================================================

    def get_presence(self) -> dict[str, Any]:
        """Get all agents' presence status."""
        presence = self.storage.load_presence()

        return {
            "agents": [
                {
                    "id": a.id,
                    "status": a.status,
                    "updated_at": a.updated_at,
                }
                for a in presence.agents
            ],
            "heartbeat_timeout_seconds": presence.heartbeat_timeout_seconds,
        }

    def update_my_status(
        self,
        agent_id: str,
        status: str,
    ) -> dict[str, Any]:
        """Update an agent's presence status.

        Args:
            agent_id: Your agent identifier
            status: Natural language description of what you're doing/thinking (1-2 sentences)
        """
        agent = self.storage.update_agent_presence(
            agent_id=agent_id,
            status=status,
        )

        return {
            "success": True,
            "agent": {
                "id": agent.id,
                "status": agent.status,
                "updated_at": agent.updated_at,
            },
        }

    def set_idle(self, agent_id: str) -> dict[str, Any]:
        """Clear an agent's status."""
        agent = self.storage.set_agent_idle(agent_id)

        return {
            "success": True,
            "agent": {
                "id": agent.id,
                "status": agent.status,
                "updated_at": agent.updated_at,
            },
        }

    # =========================================================================
    # Milestone Tools
    # =========================================================================

    def create_milestone(
        self,
        name: str,
        description: str,
        status: str = "pending",
    ) -> dict[str, Any]:
        """Create a new milestone."""
        context = self.storage.load_context()

        # Generate ID
        milestone_id = self.storage.generate_milestone_id(context)

        # Validate status
        try:
            status_enum = MilestoneStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}. Must be done/active/pending.")

        now = datetime.now(timezone.utc)

        # Set started date for active milestones
        started = None
        if status_enum == MilestoneStatus.ACTIVE:
            started = now.strftime("%Y-%m-%d")

        milestone = Milestone(
            id=milestone_id,
            name=name,
            description=description,
            status=status_enum,
            started=started,
            updated_at=now.isoformat().replace("+00:00", "Z"),
        )

        context.milestones.append(milestone)
        self.storage.save_context(context)

        return {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
            "status": milestone.status.value,
            "started": milestone.started,
            "updated_at": milestone.updated_at,
        }

    def update_milestone(
        self,
        milestone_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing milestone."""
        context = self.storage.load_context()

        milestone = self.storage.get_milestone(context, milestone_id)
        if milestone is None:
            raise ValueError(f"Milestone not found: {milestone_id}")

        if name is not None:
            milestone.name = name

        if description is not None:
            milestone.description = description

        if status is not None:
            try:
                new_status = MilestoneStatus(status)
            except ValueError:
                raise ValueError(f"Invalid status: {status}")

            # Set started date when becoming active
            if new_status == MilestoneStatus.ACTIVE and milestone.status != MilestoneStatus.ACTIVE:
                if milestone.started is None:
                    milestone.started = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            milestone.status = new_status

        # Update timestamp
        milestone.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.storage.save_context(context)

        # Build response
        result: dict[str, Any] = {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
            "status": milestone.status.value,
            "started": milestone.started,
            "completed": milestone.completed,
            "outcomes": milestone.outcomes,
            "updated_at": milestone.updated_at,
        }

        # Add next_step hint if milestone just became active
        if status == "active":
            # Check if there are tasks for this work
            tasks = self.storage.list_tasks(include_archived=False)
            active_tasks = [t for t in tasks if t.status == TaskStatus.ACTIVE]
            if not active_tasks:
                planned_tasks = [t for t in tasks if t.status == TaskStatus.PLANNED]
                if planned_tasks:
                    result["next_step"] = f"Activate a task? {planned_tasks[0].id}: {planned_tasks[0].name}"
                else:
                    result["next_step"] = "Create tasks for this milestone with create_task()"

        return result

    def complete_milestone(
        self,
        milestone_id: str,
        outcomes: str,
    ) -> dict[str, Any]:
        """Complete a milestone with outcomes."""
        context = self.storage.load_context()

        milestone = self.storage.get_milestone(context, milestone_id)
        if milestone is None:
            raise ValueError(f"Milestone not found: {milestone_id}")

        now = datetime.now(timezone.utc)
        milestone.status = MilestoneStatus.DONE
        milestone.completed = now.strftime("%Y-%m-%d")
        milestone.outcomes = outcomes
        milestone.updated_at = now.isoformat().replace("+00:00", "Z")

        self.storage.save_context(context)

        # Build response
        result: dict[str, Any] = {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
            "status": milestone.status.value,
            "started": milestone.started,
            "completed": milestone.completed,
            "outcomes": milestone.outcomes,
            "updated_at": milestone.updated_at,
        }

        # Add next_step hint - suggest next milestone
        pending_milestones = [m for m in context.milestones if m.status == MilestoneStatus.PENDING]
        if pending_milestones:
            next_m = pending_milestones[0]
            result["next_step"] = f"Ready to start {next_m.id}: {next_m.name}?"
        else:
            result["next_step"] = "All milestones done! Consider planning the next phase."

        return result

    def remove_milestone(self, milestone_id: str) -> dict[str, Any]:
        """Remove a milestone."""
        context = self.storage.load_context()

        milestone = self.storage.get_milestone(context, milestone_id)
        if milestone is None:
            raise ValueError(f"Milestone not found: {milestone_id}")

        context.milestones = [m for m in context.milestones if m.id != milestone_id]
        self.storage.save_context(context)

        return {"deleted": True, "milestone_id": milestone_id}

    # =========================================================================
    # Task Tools
    # =========================================================================

    def list_tasks(
        self,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        include_archived: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """List or get tasks."""
        if task_id:
            task = self.storage.load_task(task_id, include_archived=include_archived)
            if task is None:
                raise ValueError(f"Task not found: {task_id}")
            return self._task_to_dict(task)

        tasks = self.storage.list_tasks(include_archived=include_archived)

        if status:
            try:
                status_enum = TaskStatus(status)
                tasks = [t for t in tasks if t.status == status_enum]
            except ValueError:
                raise ValueError(f"Invalid status: {status}")

        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]

        return [self._task_to_dict(t) for t in tasks]

    def create_task(
        self,
        name: str,
        goal: str,
        steps: list[dict[str, str]],
        task_id: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        if task_id is None:
            task_id = self.storage.generate_task_id()

        if not task_id.startswith("T") or not task_id[1:].isdigit():
            raise ValueError(f"Invalid task ID format: {task_id}")

        if self.storage.load_task(task_id) is not None:
            raise ValueError(f"Task already exists: {task_id}")

        task_steps = []
        for i, s in enumerate(steps, start=1):
            step = Step(
                id=f"S{i}",
                name=s.get("name", ""),
                acceptance=s.get("acceptance", ""),
                status=StepStatus.PENDING,
            )
            task_steps.append(step)

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        task = Task(
            id=task_id,
            name=name,
            goal=goal,
            status=TaskStatus.PLANNED,
            assignee=assignee,
            created_at=now,
            updated_at=now,
            steps=task_steps,
        )

        self.storage.save_task(task)

        return self._task_to_dict(task)

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        name: Optional[str] = None,
        goal: Optional[str] = None,
        assignee: Optional[str] = None,
        step_id: Optional[str] = None,
        step_status: Optional[str] = None,
        steps: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Update a task."""
        task = self.storage.load_task(task_id)
        if task is None:
            raise ValueError(f"Task not found: {task_id}")

        # Track if task is being marked done for next_step logic
        task_becoming_done = False

        if status is not None:
            try:
                new_status = TaskStatus(status)
                if new_status == TaskStatus.DONE and task.status != TaskStatus.DONE:
                    task_becoming_done = True
                task.status = new_status
            except ValueError:
                raise ValueError(f"Invalid status: {status}")

        if name is not None:
            task.name = name

        if goal is not None:
            task.goal = goal

        if assignee is not None:
            task.assignee = assignee

        # Track if step is being marked done for next_step logic
        all_steps_done = False
        if step_id is not None and step_status is not None:
            found = False
            for step in task.steps:
                if step.id == step_id:
                    try:
                        step.status = StepStatus(step_status)
                    except ValueError:
                        raise ValueError(f"Invalid step status: {step_status}")
                    found = True
                    break
            if not found:
                raise ValueError(f"Step not found: {step_id}")

            # Check if all steps are now done
            all_steps_done = all(s.status == StepStatus.DONE for s in task.steps)

        if steps is not None:
            new_steps = []
            for s in steps:
                step = Step(
                    id=s.get("id", ""),
                    name=s.get("name", ""),
                    acceptance=s.get("acceptance", ""),
                    status=StepStatus(s.get("status", "pending")),
                )
                new_steps.append(step)
            task.steps = new_steps

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.storage.save_task(task)

        # Build response with task data
        result = self._task_to_dict(task)

        # Add next_step hints based on what just happened
        if task_becoming_done:
            # Task was just completed - check if there are more tasks
            all_tasks = self.storage.list_tasks(include_archived=False)
            active_tasks = [t for t in all_tasks if t.status == TaskStatus.ACTIVE and t.id != task_id]
            if not active_tasks:
                planned_tasks = [t for t in all_tasks if t.status == TaskStatus.PLANNED]
                if planned_tasks:
                    result["next_step"] = f"Next task: {planned_tasks[0].id}: {planned_tasks[0].name}"
                else:
                    # All tasks done - maybe complete milestone?
                    result["next_step"] = "All tasks done. Ready to complete milestone?"
        elif all_steps_done and task.status == TaskStatus.ACTIVE:
            # All steps done but task still active
            result["next_step"] = f"All steps done. Mark {task_id} as done?"

        return result

    def delete_task(self, task_id: str) -> dict[str, Any]:
        """Delete a task."""
        if not self.storage.delete_task(task_id):
            raise ValueError(f"Task not found: {task_id}")

        return {"deleted": True, "task_id": task_id}

    # =========================================================================
    # Note Tools
    # =========================================================================

    def add_note(self, content: str, score: int = 15) -> dict[str, Any]:
        """Add a note."""
        if score < 10 or score > 100:
            raise ValueError(f"Score must be between 10 and 100, got: {score}")

        context = self.storage.load_context()

        note_id = self.storage.generate_note_id(context)
        note = Note(id=note_id, content=content, score=score)
        context.notes.append(note)

        self.storage.save_context(context)

        return {"id": note_id, "content": content, "score": score}

    def update_note(
        self,
        note_id: str,
        content: Optional[str] = None,
        score: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update a note."""
        context = self.storage.load_context()

        note = self.storage.get_note_by_id(context, note_id)
        if note is None:
            raise ValueError(f"Note not found: {note_id}")

        if content is not None:
            note.content = content

        if score is not None:
            if score < 10 or score > 100:
                raise ValueError(f"Score must be between 10 and 100, got: {score}")
            note.score = score

        self.storage.save_context(context)

        return {"id": note.id, "content": note.content, "score": note.score}

    def remove_note(self, note_id: str) -> dict[str, Any]:
        """Remove a note."""
        context = self.storage.load_context()

        note = self.storage.get_note_by_id(context, note_id)
        if note is None:
            raise ValueError(f"Note not found: {note_id}")

        context.notes = [n for n in context.notes if n.id != note_id]
        self.storage.save_context(context)

        return {"deleted": True, "note_id": note_id}

    # =========================================================================
    # Reference Tools
    # =========================================================================

    def add_reference(self, url: str, note: str, score: int = 15) -> dict[str, Any]:
        """Add a reference."""
        if score < 10 or score > 100:
            raise ValueError(f"Score must be between 10 and 100, got: {score}")

        context = self.storage.load_context()

        ref_id = self.storage.generate_reference_id(context)
        ref = Reference(id=ref_id, url=url, note=note, score=score)
        context.references.append(ref)

        self.storage.save_context(context)

        return {"id": ref_id, "url": url, "note": note, "score": score}

    def update_reference(
        self,
        reference_id: str,
        url: Optional[str] = None,
        note: Optional[str] = None,
        score: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update a reference."""
        context = self.storage.load_context()

        ref = self.storage.get_reference_by_id(context, reference_id)
        if ref is None:
            raise ValueError(f"Reference not found: {reference_id}")

        if url is not None:
            ref.url = url

        if note is not None:
            ref.note = note

        if score is not None:
            if score < 10 or score > 100:
                raise ValueError(f"Score must be between 10 and 100, got: {score}")
            ref.score = score

        self.storage.save_context(context)

        return {"id": ref.id, "url": ref.url, "note": ref.note, "score": ref.score}

    def remove_reference(self, reference_id: str) -> dict[str, Any]:
        """Remove a reference."""
        context = self.storage.load_context()

        ref = self.storage.get_reference_by_id(context, reference_id)
        if ref is None:
            raise ValueError(f"Reference not found: {reference_id}")

        context.references = [r for r in context.references if r.id != reference_id]
        self.storage.save_context(context)

        return {"deleted": True, "reference_id": reference_id}

    # =========================================================================
    # Helpers
    # =========================================================================

    def _task_to_dict(self, task: Task) -> dict[str, Any]:
        """Convert a Task to a dict with computed fields."""
        current_step = task.current_step
        return {
            "id": task.id,
            "name": task.name,
            "goal": task.goal,
            "status": task.status.value,
            "assignee": task.assignee,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "acceptance": s.acceptance,
                    "status": s.status.value,
                }
                for s in task.steps
            ],
            "current_step": current_step.id if current_step else None,
            "progress": task.progress,
        }
