"""File storage layer for context data."""

import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import yaml

from .schema import (
    AgentPresence,
    Context,
    Milestone,
    MilestoneStatus,
    Note,
    PresenceData,
    Reference,
    Step,
    StepStatus,
    Task,
    TaskStatus,
)

# Archive threshold for score
ARCHIVE_SCORE_THRESHOLD = -5

# Archive threshold for done tasks (days)
ARCHIVE_DONE_DAYS = 7

# Max done tasks before archiving oldest
MAX_DONE_TASKS = 10

# Max done milestones to return in get_context
MAX_DONE_MILESTONES_RETURNED = 3


class ContextStorage:
    """Handles reading and writing context data to YAML files."""

    def __init__(self, root: Optional[Path] = None):
        """Initialize storage with project root directory."""
        self.root = Path(root) if root else Path.cwd()
        self.context_dir = self.root / "context"
        self.tasks_dir = self.context_dir / "tasks"
        self.archive_dir = self.context_dir / "archive"
        self.archive_tasks_dir = self.archive_dir / "tasks"

    def _ensure_dirs(self) -> None:
        """Create context directories if they don't exist."""
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.archive_tasks_dir.mkdir(parents=True, exist_ok=True)

    def _context_path(self) -> Path:
        """Get path to context.yaml."""
        return self.context_dir / "context.yaml"

    def _task_path(self, task_id: str) -> Path:
        """Get path to a task file."""
        return self.tasks_dir / f"{task_id}.yaml"

    def _archive_task_path(self, task_id: str) -> Path:
        """Get path to an archived task file."""
        return self.archive_tasks_dir / f"{task_id}.yaml"

    def _archive_notes_path(self) -> Path:
        """Get path to archived notes file."""
        return self.archive_dir / "notes.yaml"

    def _archive_refs_path(self) -> Path:
        """Get path to archived references file."""
        return self.archive_dir / "references.yaml"

    def _presence_path(self) -> Path:
        """Get path to presence.yaml (gitignored, runtime state)."""
        return self.context_dir / "presence.yaml"

    # =========================================================================
    # Version Computation
    # =========================================================================

    def compute_version(self) -> str:
        """
        Compute a version hash for the current context state.
        
        The version is a content-based hash of all context files. Any change
        to context.yaml or tasks/*.yaml will produce a different version.
        
        This enables agents to detect when context has changed without
        re-reading all data.
        
        Returns:
            12-character hex string (SHA256 prefix)
        """
        h = hashlib.sha256()
        
        # Hash context.yaml content
        ctx_path = self._context_path()
        if ctx_path.exists():
            h.update(ctx_path.read_bytes())
        
        # Hash all task files in sorted order (for determinism)
        if self.tasks_dir.exists():
            task_files = sorted(self.tasks_dir.glob("T*.yaml"))
            for task_file in task_files:
                h.update(task_file.read_bytes())
        
        return h.hexdigest()[:12]

    # =========================================================================
    # Context Operations
    # =========================================================================

    def load_context(self) -> Context:
        """Load context from context.yaml."""
        path = self._context_path()
        if not path.exists():
            return Context()

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data is None:
                return Context()

            # Parse vision and sketch
            vision = data.get("vision")
            sketch = data.get("sketch")

            # Parse milestones
            milestones = []
            for m in data.get("milestones", []):
                milestones.append(Milestone(
                    id=m.get("id", ""),
                    name=m.get("name", ""),
                    description=m.get("description", ""),
                    status=MilestoneStatus(m.get("status", "pending")),
                    started=m.get("started"),
                    completed=m.get("completed"),
                    outcomes=m.get("outcomes"),
                    updated_at=m.get("updated_at"),
                ))

            # Parse notes
            notes = []
            for n in data.get("notes", []):
                notes.append(Note(
                    id=n.get("id", ""),
                    content=n.get("content", ""),
                    score=n.get("score", 15),
                ))

            # Parse references
            refs = []
            for r in data.get("references", []):
                refs.append(Reference(
                    id=r.get("id", ""),
                    url=r.get("url", ""),
                    note=r.get("note", ""),
                    score=r.get("score", 15),
                ))

            return Context(vision=vision, sketch=sketch, milestones=milestones, notes=notes, references=refs)
        except (yaml.YAMLError, ValueError):
            return Context()

    def save_context(self, context: Context) -> None:
        """Save context to context.yaml."""
        self._ensure_dirs()

        data = {}

        # Add vision and sketch if present
        if context.vision is not None:
            data["vision"] = context.vision
        if context.sketch is not None:
            data["sketch"] = context.sketch

        data["milestones"] = [
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
            for m in context.milestones
        ]
        data["notes"] = [
            {"id": n.id, "content": n.content, "score": n.score}
            for n in context.notes
        ]
        data["references"] = [
            {"id": r.id, "url": r.url, "note": r.note, "score": r.score}
            for r in context.references
        ]

        # Remove None values from milestones
        for m in data["milestones"]:
            m_copy = dict(m)
            for k, v in m_copy.items():
                if v is None:
                    del m[k]

        path = self._context_path()
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8"
        )

    # =========================================================================
    # Milestone Operations
    # =========================================================================

    def generate_milestone_id(self, context: Context) -> str:
        """Generate the next milestone ID (M1, M2...)."""
        max_num = 0
        for m in context.milestones:
            match = re.match(r"M(\d+)", m.id)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
        return f"M{max_num + 1}"

    def get_milestone(self, context: Context, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by ID."""
        for m in context.milestones:
            if m.id == milestone_id:
                return m
        return None

    def get_milestones_for_response(self, context: Context) -> list[Milestone]:
        """Get milestones for MCP response (last N done + all active/pending)."""
        done = [m for m in context.milestones if m.status == MilestoneStatus.DONE]
        active_pending = [m for m in context.milestones if m.status != MilestoneStatus.DONE]

        # Take last N done milestones
        recent_done = done[-MAX_DONE_MILESTONES_RETURNED:] if done else []

        return recent_done + active_pending

    # =========================================================================
    # Note Operations
    # =========================================================================

    def generate_note_id(self, context: Context) -> str:
        """Generate the next note ID (N001, N002...)."""
        max_num = 0
        for note in context.notes:
            match = re.match(r"N(\d+)", note.id)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
        return f"N{max_num + 1:03d}"

    def get_note_by_id(self, context: Context, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        for n in context.notes:
            if n.id == note_id:
                return n
        return None

    # =========================================================================
    # Reference Operations
    # =========================================================================

    def generate_reference_id(self, context: Context) -> str:
        """Generate the next reference ID (R001, R002...)."""
        max_num = 0
        for ref in context.references:
            match = re.match(r"R(\d+)", ref.id)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
        return f"R{max_num + 1:03d}"

    def get_reference_by_id(self, context: Context, ref_id: str) -> Optional[Reference]:
        """Get a reference by ID."""
        for r in context.references:
            if r.id == ref_id:
                return r
        return None

    # =========================================================================
    # Task Operations
    # =========================================================================

    def load_task(self, task_id: str, include_archived: bool = False) -> Optional[Task]:
        """Load a task by ID."""
        path = self._task_path(task_id)
        if path.exists():
            return self._parse_task(path)

        if include_archived:
            archive_path = self._archive_task_path(task_id)
            if archive_path.exists():
                return self._parse_task(archive_path)

        return None

    def _parse_task(self, path: Path) -> Optional[Task]:
        """Parse a task from a YAML file."""
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data is None:
                return None

            steps = []
            for s in data.get("steps", []):
                steps.append(Step(
                    id=s.get("id", ""),
                    name=s.get("name", ""),
                    acceptance=s.get("acceptance", ""),
                    status=StepStatus(s.get("status", "pending"))
                ))

            return Task(
                id=data.get("id", ""),
                name=data.get("name", ""),
                goal=data.get("goal", ""),
                status=TaskStatus(data.get("status", "planned")),
                assignee=data.get("assignee"),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at"),
                steps=steps
            )
        except (yaml.YAMLError, ValueError):
            return None

    def save_task(self, task: Task) -> None:
        """Save a task to its file."""
        self._ensure_dirs()

        data = {
            "id": task.id,
            "name": task.name,
            "goal": task.goal,
            "status": task.status.value,
            "assignee": task.assignee,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "steps": [
                {"id": s.id, "name": s.name, "acceptance": s.acceptance, "status": s.status.value}
                for s in task.steps
            ]
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        path = self._task_path(task.id)
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8"
        )

    def delete_task(self, task_id: str) -> bool:
        """Delete a task file."""
        path = self._task_path(task_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_tasks(self, include_archived: bool = False) -> list[Task]:
        """List all tasks sorted by ID."""
        tasks = []

        if self.tasks_dir.exists():
            for path in self.tasks_dir.glob("T*.yaml"):
                task = self._parse_task(path)
                if task:
                    tasks.append(task)

        if include_archived and self.archive_tasks_dir.exists():
            for path in self.archive_tasks_dir.glob("T*.yaml"):
                task = self._parse_task(path)
                if task:
                    tasks.append(task)

        tasks.sort(key=lambda t: t.id)
        return tasks

    def generate_task_id(self) -> str:
        """Generate the next task ID (T001, T002...)."""
        max_num = 0

        if self.tasks_dir.exists():
            for path in self.tasks_dir.glob("T*.yaml"):
                match = re.match(r"T(\d+)", path.stem)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)

        if self.archive_tasks_dir.exists():
            for path in self.archive_tasks_dir.glob("T*.yaml"):
                match = re.match(r"T(\d+)", path.stem)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)

        return f"T{max_num + 1:03d}"

    # =========================================================================
    # Score Decay and Archive Operations
    # =========================================================================

    def decay_scores(self, context: Context) -> tuple[Context, list[Note], list[Reference]]:
        """Decay scores for all notes and references.

        Called during get_context(). Decrements all scores by 1.
        """
        archived_notes = []
        archived_refs = []
        remaining_notes = []
        remaining_refs = []

        for note in context.notes:
            note.score -= 1
            if note.score <= ARCHIVE_SCORE_THRESHOLD:
                archived_notes.append(note)
            else:
                remaining_notes.append(note)

        for ref in context.references:
            ref.score -= 1
            if ref.score <= ARCHIVE_SCORE_THRESHOLD:
                archived_refs.append(ref)
            else:
                remaining_refs.append(ref)

        context.notes = remaining_notes
        context.references = remaining_refs

        return context, archived_notes, archived_refs

    def archive_entries(self, notes: list[Note], refs: list[Reference]) -> None:
        """Archive notes and references to archive files."""
        if not notes and not refs:
            return

        self._ensure_dirs()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        if notes:
            existing = []
            notes_path = self._archive_notes_path()
            if notes_path.exists():
                try:
                    data = yaml.safe_load(notes_path.read_text(encoding="utf-8"))
                    existing = data if isinstance(data, list) else []
                except yaml.YAMLError:
                    existing = []

            for note in notes:
                existing.append({
                    "id": note.id,
                    "content": note.content,
                    "score": note.score,
                    "archived_at": now
                })

            notes_path.write_text(
                yaml.safe_dump(existing, allow_unicode=True, sort_keys=False),
                encoding="utf-8"
            )

        if refs:
            existing = []
            refs_path = self._archive_refs_path()
            if refs_path.exists():
                try:
                    data = yaml.safe_load(refs_path.read_text(encoding="utf-8"))
                    existing = data if isinstance(data, list) else []
                except yaml.YAMLError:
                    existing = []

            for ref in refs:
                existing.append({
                    "id": ref.id,
                    "url": ref.url,
                    "note": ref.note,
                    "score": ref.score,
                    "archived_at": now
                })

            refs_path.write_text(
                yaml.safe_dump(existing, allow_unicode=True, sort_keys=False),
                encoding="utf-8"
            )

    def archive_old_tasks(self) -> list[str]:
        """Archive old done tasks."""
        archived_ids = []
        tasks = self.list_tasks(include_archived=False)

        done_tasks = [t for t in tasks if t.status == TaskStatus.DONE]

        if not done_tasks:
            return archived_ids

        now = datetime.now(timezone.utc)
        threshold = now - timedelta(days=ARCHIVE_DONE_DAYS)

        for task in done_tasks:
            try:
                created = datetime.fromisoformat(task.created_at.rstrip("Z"))
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created < threshold:
                    self._move_to_archive(task.id)
                    archived_ids.append(task.id)
            except ValueError:
                pass

        remaining_done = [t for t in done_tasks if t.id not in archived_ids]
        if len(remaining_done) > MAX_DONE_TASKS:
            remaining_done.sort(key=lambda t: t.created_at)
            to_archive = remaining_done[:len(remaining_done) - MAX_DONE_TASKS]
            for task in to_archive:
                self._move_to_archive(task.id)
                archived_ids.append(task.id)

        return archived_ids

    def _move_to_archive(self, task_id: str) -> None:
        """Move a task file to archive."""
        src = self._task_path(task_id)
        dst = self._archive_task_path(task_id)

        if src.exists():
            self._ensure_dirs()
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            src.unlink()

    # =========================================================================
    # Presence Operations (presence.yaml - gitignored runtime state)
    # =========================================================================

    def load_presence(self) -> PresenceData:
        """Load presence from presence.yaml."""
        path = self._presence_path()
        if not path.exists():
            return PresenceData()

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data is None:
                return PresenceData()

            agents = []
            for a in data.get("agents", []):
                agents.append(AgentPresence(
                    id=a.get("id", ""),
                    status=a.get("status", ""),
                    updated_at=a.get("updated_at", ""),
                ))

            return PresenceData(
                agents=agents,
                heartbeat_timeout_seconds=data.get("heartbeat_timeout_seconds", 300),
            )
        except (yaml.YAMLError, ValueError):
            return PresenceData()

    def save_presence(self, presence: PresenceData) -> None:
        """Save presence to presence.yaml."""
        self._ensure_dirs()

        data = {
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

        # Remove empty status values
        for agent in data["agents"]:
            if not agent.get("status"):
                del agent["status"]

        path = self._presence_path()
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8"
        )

    def update_agent_presence(
        self,
        agent_id: str,
        status: str,
    ) -> AgentPresence:
        """Update a specific agent's presence status.

        Args:
            agent_id: Agent identifier
            status: Natural language description of what the agent is doing/thinking

        Note: Agent ID is stored as-is. Callers are responsible for
        ensuring consistent ID format across calls.
        """
        presence = self.load_presence()

        # Find or create agent entry
        agent = None
        for a in presence.agents:
            if a.id == agent_id:
                agent = a
                break

        if agent is None:
            agent = AgentPresence(id=agent_id)
            presence.agents.append(agent)

        # Update fields
        agent.status = status
        agent.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.save_presence(presence)
        return agent

    def set_agent_idle(self, agent_id: str) -> AgentPresence:
        """Clear an agent's status (set to empty string)."""
        return self.update_agent_presence(
            agent_id=agent_id,
            status="",
        )
