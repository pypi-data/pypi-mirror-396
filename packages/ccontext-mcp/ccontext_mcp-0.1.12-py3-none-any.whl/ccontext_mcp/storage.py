"""File storage layer for context data."""

import json
import hashlib
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

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

# Archive threshold for ttl (turns-to-live)
ARCHIVE_TTL_THRESHOLD = 0

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
        
        The version is a semantic hash of all context files. Any meaningful change
        to context.yaml or tasks/*.yaml will produce a different version.

        Note: notes/references ttl is intentionally ignored so automatic ttl decay
        does not churn the version on every get_context() call.
        
        This enables agents to detect when context has changed without
        re-reading all data.
        
        Returns:
            12-character hex string (SHA256 prefix)
        """
        def _jsonable(obj: Any) -> Any:
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, (datetime, date)):
                try:
                    return obj.isoformat()
                except Exception:
                    return str(obj)
            if isinstance(obj, list):
                return [_jsonable(x) for x in obj]
            if isinstance(obj, dict):
                out: dict[str, Any] = {}
                for k, v in obj.items():
                    out[str(k)] = _jsonable(v)
                return out
            return str(obj)

        def _strip_ttl(obj: Any) -> Any:
            if not isinstance(obj, dict):
                return obj
            out = dict(obj)
            for key in ("notes", "references"):
                items = out.get(key)
                if isinstance(items, list):
                    new_items: list[Any] = []
                    for it in items:
                        if isinstance(it, dict):
                            it2 = dict(it)
                            it2.pop("ttl", None)
                            it2.pop("score", None)  # legacy
                            new_items.append(it2)
                        else:
                            new_items.append(it)
                    out[key] = new_items
            return out

        def _stable_hash(obj: Any) -> bytes:
            payload = json.dumps(_jsonable(obj), sort_keys=True, separators=(",", ":")).encode("utf-8")
            return payload

        h = hashlib.sha256()

        ctx_path = self._context_path()
        if ctx_path.exists():
            try:
                data = yaml.safe_load(ctx_path.read_text(encoding="utf-8"))
            except Exception:
                data = None
            h.update(_stable_hash(_strip_ttl(data)))

        if self.tasks_dir.exists():
            task_files = sorted(self.tasks_dir.glob("T*.yaml"))
            for task_file in task_files:
                h.update(task_file.name.encode("utf-8"))
                try:
                    data = yaml.safe_load(task_file.read_text(encoding="utf-8"))
                except Exception:
                    data = None
                h.update(_stable_hash(data))

        return h.hexdigest()[:12]

    # =========================================================================
    # Context Operations
    # =========================================================================

    def _default_meta(self) -> dict[str, Any]:
        """Default contract embedded into context.yaml for standalone use."""
        return {
            "contract": {
                "vision": "One-sentence north star; update rarely.",
                "sketch": "Static blueprint only (architecture/strategy). No TODO/progress/tasks.",
                "milestones": "Coarse phase timeline (2-6). Exactly one active.",
                "tasks": "Deliverable work items with 3-7 steps.",
                "linking": "Each task should set milestone: Mx to form Vision→Milestones→Tasks tree."
            }
        }

    def load_context(self) -> Context:
        """Load context from context.yaml."""
        path = self._context_path()
        if not path.exists():
            return Context(meta=self._default_meta())

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data is None:
                return Context()

            # Parse vision and sketch
            vision = data.get("vision")
            sketch = data.get("sketch")

            # Parse meta/contract (preserve if present)
            meta = data.get("meta")
            if not isinstance(meta, dict) or not meta:
                meta = self._default_meta()

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

            def _parse_ttl(value: Any, default: int = 30) -> int:
                try:
                    ttl_int = int(value)
                except (TypeError, ValueError):
                    ttl_int = default
                if ttl_int < 0:
                    return 0
                if ttl_int > 100:
                    return 100
                return ttl_int

            # Parse notes
            notes = []
            for n in data.get("notes", []):
                if not isinstance(n, dict):
                    continue
                notes.append(Note(
                    id=n.get("id", ""),
                    content=n.get("content", ""),
                    ttl=_parse_ttl(n.get("ttl", n.get("score", 30)), default=30),
                ))

            # Parse references
            refs = []
            for r in data.get("references", []):
                if not isinstance(r, dict):
                    continue
                refs.append(Reference(
                    id=r.get("id", ""),
                    url=r.get("url", ""),
                    note=r.get("note", ""),
                    ttl=_parse_ttl(r.get("ttl", r.get("score", 30)), default=30),
                ))

            return Context(vision=vision, sketch=sketch, milestones=milestones, notes=notes, references=refs, meta=meta)
        except (yaml.YAMLError, ValueError):
            return Context(meta=self._default_meta())

    def save_context(self, context: Context) -> None:
        """Save context to context.yaml."""
        self._ensure_dirs()

        data = {}

        # Add vision and sketch if present
        if context.vision is not None:
            data["vision"] = context.vision
        if context.sketch is not None:
            data["sketch"] = context.sketch

        # Embed meta/contract for standalone ergonomics
        meta = context.meta if isinstance(getattr(context, "meta", None), dict) else {}
        if not meta:
            meta = self._default_meta()
        data["meta"] = meta

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
            {"id": n.id, "content": n.content, "ttl": n.ttl}
            for n in context.notes
        ]
        data["references"] = [
            {"id": r.id, "url": r.url, "note": r.note, "ttl": r.ttl}
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
                milestone=data.get("milestone") or data.get("milestone_id"),
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
            "milestone": task.milestone,
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
    # TTL Decay and Archive Operations
    # =========================================================================

    def decay_ttl(self, context: Context) -> tuple[Context, list[Note], list[Reference]]:
        """Decay ttl for all notes and references.

        Called during get_context(). Decrements ttl by 1 (floored at 0).
        Entries are archived when ttl is already 0 at the start of this step.
        """
        archived_notes = []
        archived_refs = []
        remaining_notes = []
        remaining_refs = []

        for note in context.notes:
            if note.ttl <= ARCHIVE_TTL_THRESHOLD:
                archived_notes.append(note)
                continue
            note.ttl = max(0, note.ttl - 1)
            remaining_notes.append(note)

        for ref in context.references:
            if ref.ttl <= ARCHIVE_TTL_THRESHOLD:
                archived_refs.append(ref)
                continue
            ref.ttl = max(0, ref.ttl - 1)
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
                    "ttl": note.ttl,
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
                    "ttl": ref.ttl,
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

            presence = PresenceData(
                agents=agents,
                heartbeat_timeout_seconds=data.get("heartbeat_timeout_seconds", 300),
            )
            return self._normalize_presence(presence)
        except (yaml.YAMLError, ValueError):
            return PresenceData()

    def save_presence(self, presence: PresenceData) -> None:
        """Save presence to presence.yaml."""
        self._ensure_dirs()
        presence = self._normalize_presence(presence)

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

    def _canonicalize_agent_id(self, agent_id: str) -> str:
        """Canonicalize agent identifiers to avoid duplicates (standalone-friendly)."""
        s = str(agent_id or "").strip()
        if not s:
            return ""
        # Split CamelCase/PascalCase: peerB -> peer-B, PeerA -> Peer-A
        s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", s)
        # Normalize separators
        s = s.replace("_", "-").replace(" ", "-")
        s = re.sub(r"-{2,}", "-", s)
        s = s.strip("-")
        return s.lower()

    def _normalize_presence_status(self, status: str) -> str:
        """Normalize presence status to a single concise line."""
        s = str(status or "")
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _parse_iso_timestamp(self, ts: str) -> Optional[datetime]:
        """Parse ISO timestamps best-effort; returns None if parsing fails."""
        if not ts:
            return None
        try:
            # Handle both Z suffix and +00:00
            normalized = str(ts).replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None

    def _normalize_presence(self, presence: PresenceData) -> PresenceData:
        """Normalize presence by canonicalizing agent IDs, de-duplicating, and trimming status."""
        best_by_id: dict[str, AgentPresence] = {}
        best_ts: dict[str, datetime] = {}

        for agent in list(presence.agents or []):
            cid = self._canonicalize_agent_id(agent.id)
            if not cid:
                continue

            status = self._normalize_presence_status(agent.status)
            updated_at = str(agent.updated_at or "")
            ts = self._parse_iso_timestamp(updated_at) or datetime.fromtimestamp(0, tz=timezone.utc)

            existing = best_by_id.get(cid)
            if existing is None:
                best_by_id[cid] = AgentPresence(id=cid, status=status, updated_at=updated_at)
                best_ts[cid] = ts
                continue

            # Keep the most recently updated entry.
            if ts >= best_ts.get(cid, datetime.fromtimestamp(0, tz=timezone.utc)):
                best_by_id[cid] = AgentPresence(id=cid, status=status, updated_at=updated_at)
                best_ts[cid] = ts

        agents_out = [best_by_id[k] for k in sorted(best_by_id.keys())]
        return PresenceData(
            agents=agents_out,
            heartbeat_timeout_seconds=presence.heartbeat_timeout_seconds,
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

        Agent IDs are canonicalized to avoid duplicates.
        """
        canonical_id = self._canonicalize_agent_id(agent_id)
        if not canonical_id:
            raise ValueError("agent_id must be a non-empty string")
        status_norm = self._normalize_presence_status(status)

        presence = self.load_presence()

        # Find or create agent entry
        agent = None
        for a in presence.agents:
            if a.id == canonical_id:
                agent = a
                break

        if agent is None:
            agent = AgentPresence(id=canonical_id)
            presence.agents.append(agent)

        # Update fields
        agent.status = status_norm
        agent.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.save_presence(presence)
        return agent

    def clear_agent_status(self, agent_id: str) -> AgentPresence:
        """Clear an agent's presence status (set to empty string)."""
        return self.update_agent_presence(agent_id=agent_id, status="")
