# ccontext-mcp — 面向 AI Agent 的执行上下文

[English](README.md) | **中文** | [日本語](README.ja.md)

ccontext 是一个本地优先的 MCP Server，让 AI agents 在多次会话之间共享并持续维护**可执行的“项目上下文”**：
**Vision（愿景/北极星）** · **Sketch（静态蓝图）** · **Milestones（阶段时间线）** · **Tasks（可验收交付项）** · **Notes/Refs（知识沉淀）** · **Presence（协作状态）**

**🧠 可持续的 agent 记忆** • **📋 agent 原生任务管理** • **🧹 内建卫生机制（诊断 + 生命周期）** • **⚡ 一次调用批量更新** • **🔒 全部本地文件，零基础设施**

[![PyPI](https://img.shields.io/pypi/v/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🖼️ 一眼看懂 ccontext

### 落盘文件（可移植、适合 Git）

```
your-project/
└── context/
    ├── context.yaml           # vision, sketch, milestones, notes, references（内置 contract）
    ├── tasks/
    │   ├── T001.yaml          # 交付型任务（含 steps）
    │   └── T002.yaml
    ├── presence.yaml          # 运行时状态（建议 gitignore）
    ├── .ccontext.lock         # 锁文件（建议 gitignore）
    └── archive/               # 自动归档（notes/refs/tasks，可选 gitignore）
```

### 一次调用“加载大脑”

`get_context()` 返回 **version + now + diagnostics**，让 agent 迅速对齐现状：

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

## 为什么需要 ccontext？（痛点 → 收益）

### 常见痛点

- agent 在会话之间丢失“我到底在做什么”。
- 多 agent 协作缺少统一事实源，沟通成本 N² 放大。
- 上下文无限膨胀：旧笔记变噪音，任务状态漂移。

### 直接收益

- **秒级续航**：每次启动都从同一份结构化上下文继续推进。
- **协作更干净**：presence 解决“谁在做什么”；tasks 解决“做到哪一步”。
- **长期可控**：diagnostics 提醒“上下文债务”；生命周期防止上下文越用越乱。

---

## ✨ ccontext 有什么不同

<table>
<tr>
<td width="50%">

**🗂️ 本地优先、可移植**  
上下文就是你 repo 里的 YAML 文件：无 DB、无云、无锁定。

**📋 agent 原生结构**  
围绕 agent 的真实工作方式建模：愿景、蓝图、里程碑、任务、笔记。

**⚡ 低摩擦更新**  
`commit_updates()` 一次提交多个变更（状态 + step + 笔记）。

</td>
<td width="50%">

**🧹 上下文卫生**  
`get_context()` 输出 diagnostics/top issues，明确“下一步该修哪里”。

**⏳ 内建生命周期**  
笔记/引用按 ttl 衰减并自动归档，避免“记忆膨胀”。

**👥 Presence 可读**  
Presence 默认规范化：单行、去重，避免 header 被长文本撑爆。

</td>
</tr>
</table>

---

## 核心模型（Contract）

- **Vision**：一句话北极星，低频更新。
- **Sketch**：**只写静态蓝图**（架构、策略、关键约束、重大决策）。  
  **禁止**写 TODO / 日常进度 / 任务清单（这些属于 tasks/milestones）。
- **Milestones**：粗粒度阶段（通常 2–6 个），且应当只有一个处于 *active*。
- **Tasks**：可验收交付项，3–7 个 steps；跨 handoff 的工作都应落到 task。
- **Notes/References**：必须记住的经验/决策；以及“去哪看”的路径/链接。
- **Presence**：此刻在做什么/想什么（请保持简短）。

这个 contract 会以 `meta.contract` 的形式写入 `context.yaml`，方便脱离任何 orchestrator 单独使用。

---

## 安装

### Claude Code

```bash
# uvx（推荐）
claude mcp add ccontext -- uvx ccontext-mcp

# 或 pipx
claude mcp add ccontext -- pipx run ccontext-mcp
```

### Claude Desktop

在 `claude_desktop_config.json` 中添加：

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

### 其它 MCP Client / 手动运行

```bash
pip install ccontext-mcp
CCONTEXT_ROOT=/path/to/project ccontext-mcp
```

**Root 选择规则：**优先使用 `CCONTEXT_ROOT`；否则使用当前工作目录。

---

## 推荐的 Agent 工作闭环

1) **每次开始先对齐上下文**

```python
ctx = get_context()  # 优先调用
```

2) **缺基础信息就先补齐**

```python
update_vision("Ship a reliable X that achieves Y.")
update_sketch("## Architecture\n...\n## Strategy\n...\n## Risks\n...")
```

3) **保证一个 active milestone**

```python
create_milestone(name="Phase 1: Foundation", description="...", status="active")
```

4) **把真实工作落到 tasks**

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

5) **低摩擦更新（一次提交）**

```python
commit_updates(ops=[
  {"op":"presence.set","agent_id":"peer-a","status":"Auth: implementing session validation; checking edge cases"},
  {"op":"task.step","task_id":"T001","step_id":"S2","step_status":"done"},
  {"op":"note.add","content":"Edge case: empty header triggers fallback path","ttl":50}
])
```

---

## Tools 一览

| 分类 | Tool | 用途 |
|------|------|------|
| **Context** | `get_context()` | 首先调用。返回 `version`/`now`/`diagnostics` + 全量 context。 |
| | `commit_updates()` | 一次批量提交多个更新（presence + task 进度 + notes/refs）。 |
| **Vision / Sketch** | `update_vision()` | 设置北极星。 |
| | `update_sketch()` | 更新蓝图（静态；不写 TODO/进度）。 |
| **Presence** | `get_presence()` | 看团队状态。 |
| | `update_my_status()` | 更新自己的状态（1–2 句）。 |
| | `clear_status()` | 清空状态（避免旧状态残留误导）。 |
| **Milestones** | `create_milestone()` / `update_milestone()` / `complete_milestone()` / `remove_milestone()` | 管理阶段时间线。 |
| **Tasks** | `list_tasks()` / `create_task()` / `update_task()` / `delete_task()` | 管理任务与 steps。 |
| **Notes / Refs** | `add_note()` / `update_note()` / `remove_note()` | 知识沉淀（带 ttl 生命周期）。 |
| | `add_reference()` / `update_reference()` / `remove_reference()` | 路径/链接书签（带 ttl 生命周期）。 |

---

## Version Tracking（类似 ETag）

agent 可以轻量检测上下文是否被别人更新：

```python
v = get_context()["version"]
# ... later ...
if get_context()["version"] != v:
    ctx = get_context()
```

注意：`version` 是“语义版”哈希，刻意忽略 notes/refs 的 `ttl` 衰减，避免频繁读取导致 version 抖动。

---

## Diagnostics & Lifecycle（上下文卫生）

- **Diagnostics**：`get_context()` 返回 `diagnostics`（含 `debt_score` 与 `top_issues`），提示 agent “上下文哪里需要维护”。
- **TTL 生命周期**：notes/references 每次 `get_context()` 调用会 -1，过旧会自动归档，防止上下文无限膨胀。
- **Presence 规范化**：agent_id 规范化 + 去重；status 单行化，保证可读性。

---

## Git 建议

多数团队会这样配置：

```gitignore
context/presence.yaml
context/.ccontext.lock
context/archive/
```

建议提交 `context/context.yaml` 与 `context/tasks/`，让工作可审计、可回溯、可协作。

---

## 可独立使用，也可与 Orchestrator 配合

- **独立使用**：任何支持 MCP 的 agent client 都可以直接用 ccontext。
- **配合 Orchestrator**：例如 CCCC 可以直接读写同一套 `context/` 文件，提供多 agent 的 runtime UX。
- **没有 MCP？** 依然可以手动读写 YAML 文件（只是少了 MCP 的批量更新/诊断等“易用性”）。

---

## License

MIT
