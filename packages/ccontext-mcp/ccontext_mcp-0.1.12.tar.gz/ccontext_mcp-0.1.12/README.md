# ccontext-mcp — Execution Context for AI Agents

**English** | [中文](README.zh-CN.md) | [日本語](README.ja.md)

Local-first MCP server that gives agents a **shared, durable “execution context”** across sessions:
**Vision** (why) · **Sketch** (static blueprint) · **Milestones** (timeline) · **Tasks** (deliverables) · **Notes/Refs** (knowledge) · **Presence** (who’s doing what).

**🧠 Persistent agent memory** • **📋 Agent-native task tracking** • **🧹 Built-in hygiene (diagnostics + lifecycle)** • **⚡ Batch updates (one call)** • **🔒 Local files, zero infra**

[![PyPI](https://img.shields.io/pypi/v/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🖼️ ccontext at a Glance

### Files on disk (portable, git-friendly)

```
your-project/
└── context/
    ├── context.yaml           # vision, sketch, milestones, notes, references (+ embedded contract)
    ├── tasks/
    │   ├── T001.yaml          # deliverable tasks with steps
    │   └── T002.yaml
    ├── presence.yaml          # runtime status (recommend gitignore)
    ├── .ccontext.lock         # lock file (recommend gitignore)
    └── archive/               # auto-archived notes/refs/tasks (optional gitignore)
```

### One call to “load the brain”

`get_context()` returns **version + now + diagnostics** so agents can quickly orient:

```jsonc
{
  "version": "abc123def456",
  "now": {
    "active_milestone": { "id": "M2", "name": "Phase 2", "description": "...", "status": "active" },
    "active_tasks": [{ "id": "T001", "name": "Implement auth", "milestone": "M2" }]
  },
  "diagnostics": {
    "debt_score": 2,
    "top_issues": [{ "id": "NO_ACTIVE_MILESTONE", "severity": "info", "message": "No active milestone." }]
  },
  "context": { "...": "vision/sketch/milestones/notes/references/tasks_summary" }
}
```

---

## Why ccontext? (Pain → Payoff)

### The Pain

- Agents forget what they were doing between sessions.
- Multi-agent work becomes N² coordination noise without a shared “source of truth”.
- Context grows unbounded; old notes become misleading; task state drifts.

### The Payoff

- **Resume instantly**: agents always start from the same structured context.
- **Coordinate cleanly**: presence shows who’s doing what; tasks show what’s actually done.
- **Stay sane**: diagnostics highlight context debt; ttl-based lifecycle prevents bloat.

---

## ✨ What Makes ccontext Different

<table>
<tr>
<td width="50%">

**🗂️ Local-first, Portable**  
Context is plain YAML in your repo. No DB, no cloud, no lock-in.

**📋 Agent-native Structure**  
Designed around how agents actually work: vision, blueprint, milestones, tasks, notes.

**⚡ Low-friction Updates**  
`commit_updates()` batches multiple changes in one call (status + task step + note).

</td>
<td width="50%">

**🧹 Context Hygiene**  
`get_context()` emits diagnostics + top issues so agents know what to fix.

**⏳ Lifecycle Built-in**  
Notes/refs decay by ttl and auto-archive, keeping context fresh.

**👥 Presence That Stays Readable**  
Presence is normalized (single-line, de-duped) by design.

</td>
</tr>
</table>

---

## Core Model (The “Contract”)

- **Vision**: one-sentence north star. Low frequency.
- **Sketch**: **static blueprint only** (architecture, strategy, constraints, major decisions).  
  Do **not** put TODO/progress/task lists here.
- **Milestones**: coarse phases (typically 2–6). Exactly one *active* at a time.
- **Tasks**: deliverables with 3–7 steps. If work spans handoffs, it belongs in a task.
- **Notes/References**: “things we must not forget” + “where to look”.
- **Presence**: what each agent is doing/thinking **right now** (keep it short).

This contract is embedded into `context.yaml` under `meta.contract` for standalone use.

---

## Installation

### Claude Code

```bash
# Using uvx (recommended)
claude mcp add ccontext -- uvx ccontext-mcp

# Or using pipx
claude mcp add ccontext -- pipx run ccontext-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ccontext": {
      "command": "uvx",
      "args": ["ccontext-mcp"],
      "env": { "CCONTEXT_ROOT": "/path/to/your/project" }
    }
  }
}
```

### Other MCP clients / manual

```bash
pip install ccontext-mcp
CCONTEXT_ROOT=/path/to/project ccontext-mcp
```

**Root selection:** ccontext uses `CCONTEXT_ROOT` when set; otherwise it uses the current working directory.

---

## Agent Loop (Recommended)

1) **Start every run**

```python
ctx = get_context()  # call first
```

2) **If missing, set the foundation**

```python
update_vision("Ship a reliable X that achieves Y.")
update_sketch("## Architecture\n...\n## Strategy\n...\n## Risks\n...")
```

3) **Keep one milestone active**

```python
create_milestone(name="Phase 1: Foundation", description="...", status="active")
```

4) **Track real work as tasks**

```python
create_task(
  name="Implement auth",
  goal="Users can sign in and sessions are validated",
  steps=[
    {"name":"Design", "acceptance":"Spec reviewed"},
    {"name":"Implement", "acceptance":"Tests passing"},
    {"name":"Rollout", "acceptance":"Docs updated"}
  ],
  milestone_id="M1",
  assignee="peer-a"
)
```

5) **Update with low friction (one call)**

```python
commit_updates(ops=[
  {"op":"presence.set","agent_id":"peer-a","status":"Auth: implementing session validation; checking edge cases"},
  {"op":"task.step","task_id":"T001","step_id":"S2","step_status":"done"},
  {"op":"note.add","content":"Edge case: empty header triggers fallback path","ttl":50}
])
```

---

## Tools

| Category | Tool | Purpose |
|----------|------|---------|
| **Context** | `get_context()` | Call first. Returns `version`, `now`, `diagnostics`, and the full context. |
| | `commit_updates()` | Batch multiple updates (presence + task progress + notes/refs) in one call. |
| **Vision / Sketch** | `update_vision()` | Set the north star. |
| | `update_sketch()` | Update blueprint (static, no TODO/progress). |
| **Presence** | `get_presence()` | See what other agents are doing. |
| | `update_my_status()` | Update your status (1–2 sentences). |
| | `clear_status()` | Clear your status (remove stale/finished status). |
| **Milestones** | `create_milestone()` / `update_milestone()` / `complete_milestone()` / `remove_milestone()` | Manage coarse phases. |
| **Tasks** | `list_tasks()` / `create_task()` / `update_task()` / `delete_task()` | Track deliverables with steps. |
| **Notes / Refs** | `add_note()` / `update_note()` / `remove_note()` | Preserve lessons/decisions with ttl lifecycle. |
| | `add_reference()` / `update_reference()` / `remove_reference()` | Bookmark key files/URLs with ttl lifecycle. |

---

## Version Tracking (ETag-style)

Agents can detect change without guessing:

```python
v = get_context()["version"]
# ... later ...
if get_context()["version"] != v:
    # someone changed context/tasks
    ctx = get_context()
```

Note: `version` is semantic. It intentionally ignores notes/refs `ttl` decay so frequent reads don’t churn the hash.

---

## Diagnostics & Lifecycle (Context Hygiene)

- **Diagnostics**: `get_context()` returns `diagnostics` (including `debt_score` and `top_issues`) so agents can keep the context clean.
- **TTL-based lifecycle**: notes and references decay by 1 each `get_context()` call and auto-archive when stale, preventing “memory bloat”.
- **Presence normalization**: agent IDs are canonicalized and de-duped; status is normalized to a single concise line for readability.

---

## Git Recommendations

Most teams prefer:

```gitignore
context/presence.yaml
context/.ccontext.lock
context/archive/
```

Commit `context/context.yaml` and `context/tasks/` so work survives sessions and can be reviewed.

---

## Works With (and Without) Orchestrators

- **Standalone**: any MCP-capable agent client can use ccontext directly.
- **Orchestrators**: tools like CCCC can read/write the same `context/` files for multi-agent runtime UX.
- **No MCP?** You can still read/write the YAML files manually (you just won’t get MCP ergonomics like batch updates and diagnostics).

---

## License

MIT
