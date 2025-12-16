"""MCP tool implementations for ccontext."""

import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

from .schema import (
    AgentPresence,
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

try:
    import fcntl  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


# =============================================================================
# Tool Descriptions - Critical for Agent adoption
# =============================================================================

TOOL_DESCRIPTIONS = {
    # Context - THE entry point
    "get_context": (
        "**Read this first or risk repeating work and missing critical decisions.** "
        "Your execution memory that persists across sessions. Contains: vision (goal), "
        "sketch (static blueprint), milestones (phases), tasks (deliverables), notes (lessons), "
        "and references (key files). Other agents update this too - check regularly. "
        "Returns 'version' for change detection, 'now' for active status, "
        "'diagnostics' (debt score + top issues), "
        "and may include 'warnings'/'hints' for suggested actions."
    ),
    "commit_updates": (
        "Apply multiple updates in ONE call (reduces friction; keeps context current). "
        "Input: ops=[{op: ...}, ...] and optional dry_run=true. "
        "Supported ops:\n"
        "- context.set: vision?, sketch?\n"
        "- presence.set: agent_id, status\n"
        "- milestone.update: milestone_id, name?, description?, status?, outcomes?\n"
        "- milestone.complete: milestone_id, outcomes\n"
        "- task.update: task_id, status?, name?, goal?, assignee?, milestone_id?, steps?\n"
        "- task.step: task_id, step_id, step_status\n"
        "- note.add: content, ttl? (10/30/100 recommended)\n"
        "- note.update: note_id, content?, ttl?\n"
        "- note.remove: note_id\n"
        "- reference.add: url, note, ttl? (10/30/100 recommended)\n"
        "- reference.update: reference_id, url?, note?, ttl?\n"
        "- reference.remove: reference_id\n"
        "Example ops: "
        "[{op:'presence.set',agent_id:'peer-a',status:'Implementing X'},"
        "{op:'task.step',task_id:'T001',step_id:'S2',step_status:'done'},"
        "{op:'note.add',content:'Found edge case in parser',ttl:50}]"
    ),

    # Vision/Sketch tools - project blueprint
    "update_vision": (
        "Set or update the project vision - what we're building. "
        "This is a short, fixed statement that captures the project goal. "
        "Example: 'Build secure SaaS platform for 10K users'"
    ),
    "update_sketch": (
        "Update the execution blueprint (markdown). "
        "Sketch is **static**: architecture, strategy, constraints, major decisions. "
        "**Do NOT put TODOs, daily progress, task lists, or milestone status here** "
        "(use tasks/milestones instead). "
        "Recommended sections: ## Architecture, ## Strategy, ## Risks, ## Decisions. "
        "Update on: architecture/strategy shifts or major risk changes."
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
    "clear_status": (
        "Clear your presence status (remove stale/finished status). "
        "Use this when you’re done or after a handoff so old statuses don’t linger and mislead."
    ),

    # Milestone tools - project timeline
    "create_milestone": (
        "Start a new coarse project phase (timeline). "
        "Use for 2–6 big stages (e.g., 'Phase 1: Core Implementation'). "
        "Exactly one milestone should be active at a time."
    ),
    "update_milestone": (
        "Modify milestone details or advance status (pending→active→done). "
        "Use to mark phase transitions or adjust phase scope/outcomes."
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
        "Create a **deliverable** work item with 3–7 steps. "
        "Use for concrete outcomes that span handoffs or need tracking. "
        "Prefer linking it to a milestone via milestone_id."
    ),
    "update_task": (
        "Update task execution state - status/steps/details (and optional milestone link). "
        "Keeps progress accurate for handoffs and resumption."
    ),
    "delete_task": (
        "Remove a cancelled or mistaken task. "
        "Completed tasks auto-archive after 7 days - no need to delete them."
    ),

    # Note tools - knowledge preservation
    "add_note": (
        "Preserve important knowledge for future sessions - lessons, warnings, decisions. "
        "TTL decays and auto-archives over time. Recommended tiers: "
        "10=short-term, 30=normal, 100=long-term. "
        "Example: 'API rate limit is 100/min - batch requests to avoid throttling'"
    ),
    "update_note": (
        "Refresh a note's ttl to prevent decay, or update its content. "
        "Use when a note is still valuable but its ttl is getting low."
    ),
    "remove_note": (
        "Delete an obsolete note immediately. "
        "Prefer letting low-value notes decay naturally via ttl lifecycle."
    ),

    # Reference tools - navigation bookmarks
    "add_reference": (
        "Bookmark important file paths or URLs for quick navigation. "
        "TTL decays over time. Recommended tiers: 10=short-term, 30=normal, 100=long-term. "
        "Use for: key source files, API docs, configs. "
        "Example: 'src/core/auth.py - OAuth implementation'"
    ),
    "update_reference": (
        "Refresh a reference's ttl to prevent decay, or update its details. "
        "Use when a reference is still valuable but its ttl is getting low."
    ),
    "remove_reference": (
        "Delete an obsolete reference immediately. "
        "Prefer letting outdated references decay naturally via ttl lifecycle."
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

        Each call triggers ttl decay for notes and references.

        Returns a dict with:
        - version: Content-based hash for change detection
        - context: The actual context data (milestones, notes, refs, tasks)
        - hints: Suggestions for filling incomplete context (only when applicable)

        Agents can cache the version and check if context changed
        by comparing versions on subsequent calls.
        """
        context = self.storage.load_context()

        # Decay ttl and archive if needed
        context, archived_notes, archived_refs = self.storage.decay_ttl(context)

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
            meta=context.meta or {},
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
                    "ttl": n.ttl,
                    "expiring": n.expiring,
                }
                for n in context.notes
            ],
            references=[
                {
                    "id": r.id,
                    "url": r.url,
                    "note": r.note,
                    "ttl": r.ttl,
                    "expiring": r.expiring,
                }
                for r in context.references
            ],
            tasks_summary=summary,
            active_task=active_task,
        )

        # Generate hints for incomplete context
        diagnostics, hints, warnings = self._generate_diagnostics(context, tasks)

        # Now view: active milestone + active tasks (compact)
        now_view = self._build_now_view(context, tasks)

        # Return with version for change detection
        result = {
            "version": self.storage.compute_version(),
            "context": response.model_dump(),
            "now": now_view,
            "diagnostics": diagnostics,
        }

        # Only include hints if there are any
        if warnings:
            result["warnings"] = warnings

        if hints:
            result["hints"] = hints

        # Add getting_started guide for truly empty context
        if self._is_empty_context(context, tasks):
            result["getting_started"] = self._get_getting_started_guide()

        return result

    @contextmanager
    def _context_lock(self) -> Iterator[None]:
        """Best-effort inter-process lock for multi-file updates."""
        self.storage._ensure_dirs()
        lock_path = self.storage.context_dir / ".ccontext.lock"
        with lock_path.open("a", encoding="utf-8") as f:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def commit_updates(
        self,
        ops: list[dict[str, Any]],
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Apply multiple updates in one call (single transaction-like batch)."""
        if not isinstance(ops, list) or not ops:
            raise ValueError("ops must be a non-empty list")

        changes: list[dict[str, Any]] = []

        with self._context_lock():
            context = self.storage.load_context()
            tasks = self.storage.list_tasks(include_archived=False)
            tasks_by_id: dict[str, Task] = {t.id: t for t in tasks}
            presence = self.storage.load_presence()

            context_path = self.storage.context_dir / "context.yaml"

            context_dirty = False
            presence_dirty = False
            dirty_task_ids: set[str] = set()

            now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            def _mark_change(op_index: int, op: str, summary: str, changed: bool = True) -> None:
                changes.append(
                    {
                        "op_index": op_index,
                        "op": op,
                        "changed": changed,
                        "summary": summary,
                    }
                )

            def _validate_ttl(ttl: Any, *, allow_zero: bool) -> int:
                if not isinstance(ttl, int):
                    raise ValueError("ttl must be an integer")
                if allow_zero:
                    if ttl < 0 or ttl > 100:
                        raise ValueError("ttl must be between 0 and 100")
                else:
                    if ttl < 10 or ttl > 100:
                        raise ValueError("ttl must be between 10 and 100")
                return ttl

            for idx, item in enumerate(ops):
                if not isinstance(item, dict):
                    raise ValueError(f"ops[{idx}] must be an object")
                op_name = item.get("op")
                if not isinstance(op_name, str) or not op_name.strip():
                    raise ValueError(f"ops[{idx}].op must be a non-empty string")
                op_name = op_name.strip()

                if op_name == "context.set":
                    vision = item.get("vision", None)
                    sketch = item.get("sketch", None)
                    if vision is None and sketch is None:
                        raise ValueError("context.set requires at least one of: vision, sketch")

                    if vision is not None and vision != context.vision:
                        context.vision = str(vision)
                        context_dirty = True
                    if sketch is not None and sketch != context.sketch:
                        context.sketch = str(sketch)
                        context_dirty = True

                    _mark_change(idx, op_name, "Updated context fields")

                elif op_name == "presence.set":
                    agent_id = item.get("agent_id")
                    status = item.get("status")
                    if not isinstance(agent_id, str) or not agent_id.strip():
                        raise ValueError("presence.set requires agent_id (string)")
                    if not isinstance(status, str):
                        raise ValueError("presence.set requires status (string; may be empty)")

                    canonical_id = self.storage._canonicalize_agent_id(agent_id)
                    if not canonical_id:
                        raise ValueError("presence.set requires agent_id (string)")
                    status_norm = self.storage._normalize_presence_status(status)

                    agent = next((a for a in presence.agents if a.id == canonical_id), None)
                    if agent is None:
                        agent = AgentPresence(id=canonical_id, status=status_norm, updated_at=now_iso)
                        presence.agents.append(agent)
                    else:
                        agent.status = status_norm
                        agent.updated_at = now_iso

                    presence_dirty = True
                    _mark_change(idx, op_name, f"Set presence for {canonical_id}")

                elif op_name in ("milestone.update", "milestone.complete"):
                    milestone_id = item.get("milestone_id")
                    if not isinstance(milestone_id, str) or not milestone_id.strip():
                        raise ValueError(f"{op_name} requires milestone_id (string)")

                    milestone = self.storage.get_milestone(context, milestone_id)
                    if milestone is None:
                        raise ValueError(f"Milestone not found: {milestone_id}")

                    if op_name == "milestone.complete":
                        outcomes = item.get("outcomes")
                        if not isinstance(outcomes, str) or not outcomes.strip():
                            raise ValueError("milestone.complete requires outcomes (string)")
                        milestone.status = MilestoneStatus.DONE
                        milestone.completed = milestone.completed or now_date
                        milestone.outcomes = outcomes
                        milestone.updated_at = now_iso
                        context_dirty = True
                        _mark_change(idx, op_name, f"Completed {milestone_id}")
                    else:
                        if item.get("name") is not None:
                            milestone.name = str(item.get("name"))
                        if item.get("description") is not None:
                            milestone.description = str(item.get("description"))
                        if item.get("outcomes") is not None:
                            milestone.outcomes = str(item.get("outcomes"))
                        if item.get("status") is not None:
                            try:
                                new_status = MilestoneStatus(str(item.get("status")))
                            except ValueError:
                                raise ValueError(f"Invalid milestone status: {item.get('status')}")
                            if new_status == MilestoneStatus.ACTIVE and milestone.status != MilestoneStatus.ACTIVE:
                                milestone.started = milestone.started or now_date
                            milestone.status = new_status

                        milestone.updated_at = now_iso
                        context_dirty = True
                        _mark_change(idx, op_name, f"Updated {milestone_id}")

                elif op_name == "task.update":
                    task_id = item.get("task_id")
                    if not isinstance(task_id, str) or not task_id.strip():
                        raise ValueError("task.update requires task_id (string)")
                    task = tasks_by_id.get(task_id) or self.storage.load_task(task_id)
                    if task is None:
                        raise ValueError(f"Task not found: {task_id}")
                    tasks_by_id[task_id] = task

                    if item.get("status") is not None:
                        try:
                            task.status = TaskStatus(str(item.get("status")))
                        except ValueError:
                            raise ValueError(f"Invalid task status: {item.get('status')}")
                    if item.get("name") is not None:
                        task.name = str(item.get("name"))
                    if item.get("goal") is not None:
                        task.goal = str(item.get("goal"))
                    if item.get("assignee") is not None:
                        task.assignee = str(item.get("assignee"))
                    if item.get("milestone_id") is not None:
                        milestone_id = str(item.get("milestone_id"))
                        if milestone_id and self.storage.get_milestone(context, milestone_id) is None:
                            raise ValueError(f"Milestone not found: {milestone_id}")
                        task.milestone = milestone_id or None

                    if item.get("steps") is not None:
                        if not isinstance(item.get("steps"), list):
                            raise ValueError("task.update steps must be a list")
                        new_steps: list[Step] = []
                        for s in item.get("steps"):
                            if not isinstance(s, dict):
                                raise ValueError("task.update steps items must be objects")
                            step = Step(
                                id=str(s.get("id", "")),
                                name=str(s.get("name", "")),
                                acceptance=str(s.get("acceptance", "")),
                                status=StepStatus(str(s.get("status", "pending"))),
                            )
                            new_steps.append(step)
                        task.steps = new_steps

                    task.updated_at = now_iso
                    dirty_task_ids.add(task_id)
                    _mark_change(idx, op_name, f"Updated {task_id}")

                elif op_name == "task.step":
                    task_id = item.get("task_id")
                    step_id = item.get("step_id")
                    step_status = item.get("step_status")
                    if not isinstance(task_id, str) or not task_id.strip():
                        raise ValueError("task.step requires task_id (string)")
                    if not isinstance(step_id, str) or not step_id.strip():
                        raise ValueError("task.step requires step_id (string)")
                    if not isinstance(step_status, str) or not step_status.strip():
                        raise ValueError("task.step requires step_status (string)")

                    task = tasks_by_id.get(task_id) or self.storage.load_task(task_id)
                    if task is None:
                        raise ValueError(f"Task not found: {task_id}")
                    tasks_by_id[task_id] = task

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

                    task.updated_at = now_iso
                    dirty_task_ids.add(task_id)
                    _mark_change(idx, op_name, f"Updated {task_id} {step_id} -> {step_status}")

                elif op_name == "note.add":
                    content = item.get("content")
                    if not isinstance(content, str) or not content.strip():
                        raise ValueError("note.add requires content (string)")
                    ttl = item.get("ttl", 30)
                    ttl_int = _validate_ttl(ttl if ttl is not None else 30, allow_zero=False)

                    note_id = self.storage.generate_note_id(context)
                    context.notes.append(Note(id=note_id, content=content, ttl=ttl_int))
                    context_dirty = True
                    _mark_change(idx, op_name, f"Added {note_id}")

                elif op_name == "note.update":
                    note_id = item.get("note_id")
                    if not isinstance(note_id, str) or not note_id.strip():
                        raise ValueError("note.update requires note_id (string)")
                    note = self.storage.get_note_by_id(context, note_id)
                    if note is None:
                        raise ValueError(f"Note not found: {note_id}")
                    if item.get("content") is not None:
                        note.content = str(item.get("content"))
                    if item.get("ttl") is not None:
                        note.ttl = _validate_ttl(item.get("ttl"), allow_zero=True)
                    context_dirty = True
                    _mark_change(idx, op_name, f"Updated {note_id}")

                elif op_name == "note.remove":
                    note_id = item.get("note_id")
                    if not isinstance(note_id, str) or not note_id.strip():
                        raise ValueError("note.remove requires note_id (string)")
                    before = len(context.notes)
                    context.notes = [n for n in context.notes if n.id != note_id]
                    if len(context.notes) == before:
                        raise ValueError(f"Note not found: {note_id}")
                    context_dirty = True
                    _mark_change(idx, op_name, f"Removed {note_id}")

                elif op_name == "reference.add":
                    url = item.get("url")
                    note = item.get("note")
                    if not isinstance(url, str) or not url.strip():
                        raise ValueError("reference.add requires url (string)")
                    if not isinstance(note, str) or not note.strip():
                        raise ValueError("reference.add requires note (string)")
                    ttl = item.get("ttl", 30)
                    ttl_int = _validate_ttl(ttl if ttl is not None else 30, allow_zero=False)

                    ref_id = self.storage.generate_reference_id(context)
                    context.references.append(Reference(id=ref_id, url=url, note=note, ttl=ttl_int))
                    context_dirty = True
                    _mark_change(idx, op_name, f"Added {ref_id}")

                elif op_name == "reference.update":
                    reference_id = item.get("reference_id")
                    if not isinstance(reference_id, str) or not reference_id.strip():
                        raise ValueError("reference.update requires reference_id (string)")
                    ref = self.storage.get_reference_by_id(context, reference_id)
                    if ref is None:
                        raise ValueError(f"Reference not found: {reference_id}")
                    if item.get("url") is not None:
                        ref.url = str(item.get("url"))
                    if item.get("note") is not None:
                        ref.note = str(item.get("note"))
                    if item.get("ttl") is not None:
                        ref.ttl = _validate_ttl(item.get("ttl"), allow_zero=True)
                    context_dirty = True
                    _mark_change(idx, op_name, f"Updated {reference_id}")

                elif op_name == "reference.remove":
                    reference_id = item.get("reference_id")
                    if not isinstance(reference_id, str) or not reference_id.strip():
                        raise ValueError("reference.remove requires reference_id (string)")
                    before = len(context.references)
                    context.references = [r for r in context.references if r.id != reference_id]
                    if len(context.references) == before:
                        raise ValueError(f"Reference not found: {reference_id}")
                    context_dirty = True
                    _mark_change(idx, op_name, f"Removed {reference_id}")

                else:
                    raise ValueError(f"Unsupported op: {op_name}")

            if not dry_run:
                # Ensure a durable context.yaml exists for standalone use.
                if not context_path.exists():
                    context_dirty = True

                if context_dirty:
                    self.storage.save_context(context)
                for task_id in sorted(dirty_task_ids):
                    self.storage.save_task(tasks_by_id[task_id])
                if presence_dirty:
                    self.storage.save_presence(presence)

            tasks_out = sorted(tasks_by_id.values(), key=lambda t: t.id)
            diagnostics, hints, warnings = self._generate_diagnostics(context, tasks_out)
            now_view = self._build_now_view(context, tasks_out)

            result: dict[str, Any] = {
                "success": True,
                "dry_run": dry_run,
                "changes": changes,
                "version": self.storage.compute_version(),
                "now": now_view,
                "diagnostics": diagnostics,
            }

            if warnings:
                result["warnings"] = warnings
            if hints:
                result["hints"] = hints

            return result

    def _build_now_view(self, context: Context, tasks: list[Task]) -> dict[str, Any]:
        """Build a compact 'now' view for agents (active milestone/tasks)."""
        active_ms = next((m for m in context.milestones if m.status == MilestoneStatus.ACTIVE), None)
        active_tasks = [t for t in tasks if t.status == TaskStatus.ACTIVE]
        return {
            "active_milestone": (
                {
                    "id": active_ms.id,
                    "name": active_ms.name,
                    "description": active_ms.description,
                    "status": active_ms.status.value,
                }
                if active_ms
                else None
            ),
            "active_tasks": [{"id": t.id, "name": t.name, "milestone": t.milestone} for t in active_tasks[:5]],
        }

    def _generate_diagnostics(
        self,
        context: Context,
        tasks: list[Task],
    ) -> tuple[dict[str, Any], list[str], list[str]]:
        """Generate structured diagnostics for context hygiene (standalone-friendly).

        Returns:
            diagnostics: {debt_score, issues, top_issues}
            hints: derived actionable suggestions
            warnings: derived warning/error messages
        """
        if self._is_empty_context(context, tasks):
            diagnostics = {
                "debt_score": 0,
                "issues": [
                    {
                        "id": "CONTEXT_EMPTY",
                        "severity": "info",
                        "category": "context",
                        "message": "Context is empty (new project). Initialize vision/milestone/task to avoid losing continuity.",
                        "suggestion": "Use update_vision(), create_milestone(), create_task(), and update_my_status() to initialize.",
                    }
                ],
                "top_issues": [],
            }
            hints = [diagnostics["issues"][0]["suggestion"]]
            return diagnostics, hints, []

        issues: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        def _add(
            issue_id: str,
            severity: str,
            category: str,
            message: str,
            suggestion: Optional[str] = None,
            entity_type: Optional[str] = None,
            entity_id: Optional[str] = None,
        ) -> None:
            item: dict[str, Any] = {
                "id": issue_id,
                "severity": severity,
                "category": category,
                "message": message,
            }
            if suggestion:
                item["suggestion"] = suggestion
            if entity_type:
                item["entity_type"] = entity_type
            if entity_id:
                item["entity_id"] = entity_id
            issues.append(item)

        # Vision (north star)
        if not context.vision:
            _add(
                "VISION_MISSING",
                "info",
                "vision",
                "No vision set.",
                "Consider setting a vision with update_vision() - a short statement of what we're building helps keep work focused.",
                entity_type="context",
            )

        # Sketch (static blueprint only)
        if not context.sketch:
            _add(
                "SKETCH_MISSING",
                "info",
                "sketch",
                "No sketch set.",
                "Consider creating a sketch with update_sketch() - a static blueprint (architecture/strategy/risks) helps maintain continuity.",
                entity_type="context",
            )
        else:
            sk = str(context.sketch)
            exec_signals = [
                r"\bTODO\b",
                r"\bT\d{3}\b",
                r"\bM\d+\b",
                r"\bprogress\b",
                r"\b(in_progress|active|done)\b",
            ]
            if any(re.search(pat, sk, re.I) for pat in exec_signals):
                _add(
                    "SKETCH_HAS_EXECUTION_ITEMS",
                    "warning",
                    "sketch",
                    "Sketch seems to contain execution items (TODO/progress/tasks/milestones).",
                    "Sketch is static blueprint only; move execution state into milestones/tasks.",
                    entity_type="context",
                )

        # Milestones (timeline)
        milestones_all = list(context.milestones or [])
        active_milestones = [m for m in milestones_all if m.status == MilestoneStatus.ACTIVE]
        pending_milestones = [m for m in milestones_all if m.status == MilestoneStatus.PENDING]

        if not milestones_all:
            _add(
                "MILESTONES_MISSING",
                "info",
                "milestones",
                "No milestones defined.",
                "Consider using create_milestone() to define 2–6 coarse project phases (timeline).",
                entity_type="context",
            )
        else:
            if len(active_milestones) > 1:
                ids = ", ".join([m.id for m in active_milestones][:5])
                _add(
                    "MULTIPLE_ACTIVE_MILESTONES",
                    "error",
                    "milestones",
                    f"Multiple active milestones found ({ids}).",
                    "Keep exactly one active milestone; mark others pending/done with update_milestone().",
                    entity_type="milestone",
                )
            elif not active_milestones and pending_milestones:
                _add(
                    "NO_ACTIVE_MILESTONE",
                    "info",
                    "milestones",
                    "No active milestone.",
                    f"Consider activating {pending_milestones[0].id} with update_milestone(status='active') to mark the current work phase.",
                    entity_type="milestone",
                    entity_id=pending_milestones[0].id,
                )
            else:
                for m in active_milestones:
                    if m.updated_at:
                        days_stale = self._days_since(m.updated_at, now)
                        if days_stale is not None and days_stale >= 7:
                            _add(
                                "ACTIVE_MILESTONE_STALE",
                                "info",
                                "milestones",
                                f"Milestone {m.id} active for {days_stale} days with no updates.",
                                "Still in progress, or ready to complete/transition?",
                                entity_type="milestone",
                                entity_id=m.id,
                            )
                            break

        # Tasks (deliverables)
        active_tasks = [t for t in tasks if t.status == TaskStatus.ACTIVE]
        planned_tasks = [t for t in tasks if t.status == TaskStatus.PLANNED]

        if not tasks:
            _add(
                "TASKS_MISSING",
                "info",
                "tasks",
                "No tasks defined.",
                "Consider using create_task() to break down current work into a deliverable with 3–7 steps.",
                entity_type="context",
            )
        elif not active_tasks and planned_tasks:
            _add(
                "NO_ACTIVE_TASK",
                "info",
                "tasks",
                "No active task.",
                f"Consider activating {planned_tasks[0].id} with update_task(status='active') to track current work.",
                entity_type="task",
                entity_id=planned_tasks[0].id,
            )
        else:
            for t in active_tasks:
                if t.updated_at:
                    days_stale = self._days_since(t.updated_at, now)
                    if days_stale is not None and days_stale >= 3:
                        _add(
                            "ACTIVE_TASK_STALE",
                            "info",
                            "tasks",
                            f"Task {t.id} active for {days_stale} days with no updates.",
                            "Still working on it? Update step status or mark task done if complete.",
                            entity_type="task",
                            entity_id=t.id,
                        )
                        break
            for t in active_tasks:
                if t.steps and all(s.status == StepStatus.DONE for s in t.steps):
                    _add(
                        "ACTIVE_TASK_ALL_STEPS_DONE",
                        "warning",
                        "tasks",
                        f"Task {t.id} has all steps done but is still active.",
                        f"Mark {t.id} as done with update_task(status='done').",
                        entity_type="task",
                        entity_id=t.id,
                    )
                    break

        # Linking: tasks should belong to milestones for clarity
        unlinked = [t for t in tasks if not t.milestone and t.status != TaskStatus.DONE]
        if unlinked:
            if active_milestones:
                am = active_milestones[0]
                _add(
                    "TASKS_UNLINKED",
                    "info",
                    "linking",
                    f"{len(unlinked)} task(s) have no milestone link.",
                    f"Consider setting milestone_id='{am.id}' on relevant tasks.",
                    entity_type="task",
                )
            else:
                _add(
                    "TASKS_UNLINKED",
                    "info",
                    "linking",
                    f"{len(unlinked)} task(s) have no milestone link.",
                    "Consider setting milestone_id on tasks to keep the tree clear.",
                    entity_type="task",
                )

        # Notes: preserve key learnings
        if (context.vision or context.sketch) and not context.notes:
            _add(
                "NOTES_MISSING",
                "info",
                "notes",
                "No notes recorded.",
                "Consider adding notes with add_note() to preserve lessons, warnings, or important decisions.",
                entity_type="context",
            )

        expiring_notes = [n for n in context.notes if n.ttl <= 3]
        if expiring_notes:
            _add(
                "NOTES_EXPIRING",
                "info",
                "notes",
                f"{len(expiring_notes)} note(s) expiring soon (ttl ≤ 3).",
                "Boost with update_note(ttl=...) if still relevant.",
                entity_type="note",
            )

        weights = {"info": 1, "warning": 3, "error": 5}
        debt_score = min(99, sum(weights.get(it.get("severity", "info"), 1) for it in issues))
        issues_sorted = sorted(
            issues,
            key=lambda it: (-weights.get(it.get("severity", "info"), 1), str(it.get("id") or "")),
        )
        top_issues = issues_sorted[:3]

        diagnostics = {
            "debt_score": debt_score,
            "issues": issues,
            "top_issues": top_issues,
        }

        seen: set[str] = set()
        hints_out: list[str] = []
        for it in issues_sorted:
            s = str(it.get("suggestion") or "").strip()
            if s and s not in seen:
                seen.add(s)
                hints_out.append(s)

        warnings_out = [
            str(it.get("message") or "").strip()
            for it in issues_sorted
            if str(it.get("severity") or "") in ("warning", "error")
        ]

        return diagnostics, hints_out, warnings_out

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

    def clear_status(self, agent_id: str) -> dict[str, Any]:
        """Clear an agent's presence status (set to empty string)."""
        agent = self.storage.clear_agent_status(agent_id)

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
        milestone_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        if milestone_id:
            context = self.storage.load_context()
            if self.storage.get_milestone(context, milestone_id) is None:
                raise ValueError(f"Milestone not found: {milestone_id}")

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
            milestone=milestone_id,
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
        milestone_id: Optional[str] = None,
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

        if milestone_id is not None:
            milestone_id = str(milestone_id)
            if not milestone_id.strip():
                task.milestone = None
            else:
                context = self.storage.load_context()
                if self.storage.get_milestone(context, milestone_id) is None:
                    raise ValueError(f"Milestone not found: {milestone_id}")
                task.milestone = milestone_id

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

    def add_note(self, content: str, ttl: int = 30) -> dict[str, Any]:
        """Add a note."""
        if ttl < 10 or ttl > 100:
            raise ValueError(f"ttl must be between 10 and 100, got: {ttl}")

        context = self.storage.load_context()

        note_id = self.storage.generate_note_id(context)
        note = Note(id=note_id, content=content, ttl=ttl)
        context.notes.append(note)

        self.storage.save_context(context)

        return {"id": note_id, "content": content, "ttl": ttl}

    def update_note(
        self,
        note_id: str,
        content: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update a note."""
        context = self.storage.load_context()

        note = self.storage.get_note_by_id(context, note_id)
        if note is None:
            raise ValueError(f"Note not found: {note_id}")

        if content is not None:
            note.content = content

        if ttl is not None:
            if ttl < 0 or ttl > 100:
                raise ValueError(f"ttl must be between 0 and 100, got: {ttl}")
            note.ttl = ttl

        self.storage.save_context(context)

        return {"id": note.id, "content": note.content, "ttl": note.ttl}

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

    def add_reference(self, url: str, note: str, ttl: int = 30) -> dict[str, Any]:
        """Add a reference."""
        if ttl < 10 or ttl > 100:
            raise ValueError(f"ttl must be between 10 and 100, got: {ttl}")

        context = self.storage.load_context()

        ref_id = self.storage.generate_reference_id(context)
        ref = Reference(id=ref_id, url=url, note=note, ttl=ttl)
        context.references.append(ref)

        self.storage.save_context(context)

        return {"id": ref_id, "url": url, "note": note, "ttl": ttl}

    def update_reference(
        self,
        reference_id: str,
        url: Optional[str] = None,
        note: Optional[str] = None,
        ttl: Optional[int] = None,
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

        if ttl is not None:
            if ttl < 0 or ttl > 100:
                raise ValueError(f"ttl must be between 0 and 100, got: {ttl}")
            ref.ttl = ttl

        self.storage.save_context(context)

        return {"id": ref.id, "url": ref.url, "note": ref.note, "ttl": ref.ttl}

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
            "milestone": task.milestone,
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
