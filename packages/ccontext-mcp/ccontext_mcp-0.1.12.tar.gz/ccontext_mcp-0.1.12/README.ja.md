# ccontext-mcp — AI エージェントの実行コンテキスト

[English](README.md) | [中文](README.zh-CN.md) | **日本語**

ccontext はローカルファーストの MCP サーバーです。AI エージェントがセッションを跨いでも迷子にならないよう、**実行可能な「プロジェクトの共通コンテキスト」**を維持します：
**Vision（北極星）** · **Sketch（静的ブループリント）** · **Milestones（フェーズ）** · **Tasks（成果物）** · **Notes/Refs（知識）** · **Presence（いま何をしているか）**

**🧠 永続的なエージェント記憶** • **📋 エージェント向けタスク設計** • **🧹 衛生機構（診断 + ライフサイクル）** • **⚡ 1 回でまとめて更新** • **🔒 ローカル YAML、インフラ不要**

[![PyPI](https://img.shields.io/pypi/v/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/ccontext-mcp)](https://pypi.org/project/ccontext-mcp/)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🖼️ ccontext を一目で

### ディスク上のファイル（移植性が高く Git と相性が良い）

```
your-project/
└── context/
    ├── context.yaml           # vision, sketch, milestones, notes, references（contract を内蔵）
    ├── tasks/
    │   ├── T001.yaml          # 成果物タスク（steps 付き）
    │   └── T002.yaml
    ├── presence.yaml          # ランタイム状態（gitignore 推奨）
    ├── .ccontext.lock         # ロックファイル（gitignore 推奨）
    └── archive/               # 自動アーカイブ（notes/refs/tasks、任意で gitignore）
```

### 1 回の呼び出しで「脳をロード」

`get_context()` は **version + now + diagnostics** を返し、エージェントが素早く状況把握できます：

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

## なぜ ccontext？（痛み → 効果）

### よくある問題

- セッションを跨ぐと「何をしていたか」を忘れる。
- マルチエージェントは共通の事実源がないと調整コストが N² になる。
- コンテキストが肥大化し、古い情報がノイズ/誤誘導になる。

### 得られる効果

- **即再開**：毎回同じ構造化コンテキストから続きができる。
- **協調が整理される**：presence は「誰が何をしているか」、tasks は「何がどこまで終わったか」。
- **長期運用に強い**：diagnostics が「コンテキストの負債」を可視化し、ライフサイクルが肥大化を防ぐ。

---

## ✨ ccontext の強み

<table>
<tr>
<td width="50%">

**🗂️ ローカルファースト / 移植性**  
コンテキストはリポジトリ内の YAML。DB もクラウドも不要、ロックインなし。

**📋 エージェント向け構造**  
Vision/Sketch/Milestones/Tasks/Notes で「実行」を支える形に最適化。

**⚡ 低摩擦の更新**  
`commit_updates()` で status + task step + note を 1 回で更新。

</td>
<td width="50%">

**🧹 コンテキスト衛生**  
`get_context()` が diagnostics/top issues を返し、次の手入れが明確。

**⏳ ライフサイクル内蔵**  
notes/refs は ttl により減衰・自動アーカイブされ、鮮度を維持。

**👥 読める Presence**  
Presence は単一行・重複排除で、表示が破綻しにくい。

</td>
</tr>
</table>

---

## コアモデル（Contract）

- **Vision**：1 行の北極星。頻繁に変えない。
- **Sketch**：**静的ブループリントのみ**（設計/戦略/制約/重要決定）。  
  TODO/日次進捗/タスクリストは **書かない**（tasks/milestones に置く）。
- **Milestones**：粗いフェーズ（通常 2–6）。*active* は原則 1 つ。
- **Tasks**：成果物単位、3–7 steps。handoff を跨ぐ仕事は task にする。
- **Notes/References**：忘れてはいけない知見と、参照すべき場所。
- **Presence**：いま何をしている/考えているか（短く）。

この contract は `context.yaml` の `meta.contract` に埋め込まれ、単体運用でも迷わないようにします。

---

## インストール

### Claude Code

```bash
# uvx（推奨）
claude mcp add ccontext -- uvx ccontext-mcp

# または pipx
claude mcp add ccontext -- pipx run ccontext-mcp
```

### Claude Desktop

`claude_desktop_config.json` に追加：

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

### その他の MCP クライアント / 手動実行

```bash
pip install ccontext-mcp
CCONTEXT_ROOT=/path/to/project ccontext-mcp
```

**ルート選択:** `CCONTEXT_ROOT` があればそれを使用し、なければカレントディレクトリを使用します。

---

## 推奨エージェントループ

1) **毎回最初にコンテキストを読む**

```python
ctx = get_context()  # first
```

2) **足りなければ基礎を整える**

```python
update_vision("Ship a reliable X that achieves Y.")
update_sketch("## Architecture\n...\n## Strategy\n...\n## Risks\n...")
```

3) **active milestone を 1 つ保つ**

```python
create_milestone(name="Phase 1: Foundation", description="...", status="active")
```

4) **実作業は tasks に落とす**

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

5) **更新は 1 回でまとめる**

```python
commit_updates(ops=[
  {"op":"presence.set","agent_id":"peer-a","status":"Auth: implementing session validation; checking edge cases"},
  {"op":"task.step","task_id":"T001","step_id":"S2","step_status":"done"},
  {"op":"note.add","content":"Edge case: empty header triggers fallback path","ttl":50}
])
```

---

## Tools 一覧

| カテゴリ | Tool | 目的 |
|----------|------|------|
| **Context** | `get_context()` | 最初に呼ぶ。`version`/`now`/`diagnostics` + 全体の context を返す。 |
| | `commit_updates()` | presence + task 進捗 + notes/refs を 1 回で更新。 |
| **Vision / Sketch** | `update_vision()` | 北極星を設定。 |
| | `update_sketch()` | ブループリント更新（静的。TODO/進捗は書かない）。 |
| **Presence** | `get_presence()` | 他のエージェント状況を見る。 |
| | `update_my_status()` | 自分の状況を更新（1–2 文）。 |
| | `clear_status()` | 状況をクリア（古い status を残さない）。 |
| **Milestones** | `create_milestone()` / `update_milestone()` / `complete_milestone()` / `remove_milestone()` | フェーズ管理。 |
| **Tasks** | `list_tasks()` / `create_task()` / `update_task()` / `delete_task()` | 成果物と steps を管理。 |
| **Notes / Refs** | `add_note()` / `update_note()` / `remove_note()` | 知見を残す（ttl ライフサイクル）。 |
| | `add_reference()` / `update_reference()` / `remove_reference()` | 参照（ファイル/URL）を残す（ttl ライフサイクル）。 |

---

## Version Tracking（ETag 風）

軽量に変更検出できます：

```python
v = get_context()["version"]
# ... later ...
if get_context()["version"] != v:
    ctx = get_context()
```

注：`version` はセマンティックです。notes/refs の `ttl` 減衰は意図的に無視し、頻繁な read で version が揺れないようにします。

---

## Diagnostics & Lifecycle（衛生と鮮度）

- **Diagnostics**：`get_context()` が `diagnostics`（`debt_score` と `top_issues` など）を返し、手入れポイントが分かる。
- **TTL ライフサイクル**：notes/refs は `get_context()` 呼び出しで -1 され、古いものは自動アーカイブ。
- **Presence 正規化**：agent_id は正規化 + 重複排除。status は単一行に整形し、読みやすく保つ。

---

## Git 推奨設定

多くのチームは以下を好みます：

```gitignore
context/presence.yaml
context/.ccontext.lock
context/archive/
```

`context/context.yaml` と `context/tasks/` はコミットし、変更がレビュー可能になるようにします。

---

## 単体でも、Orchestrator と一緒でも

- **単体運用**：MCP 対応のエージェントクライアントでそのまま使えます。
- **Orchestrator 連携**：CCCC のようなツールは同じ `context/` を読み書きしてランタイム UX を提供できます。
- **MCP がなくても**：YAML を直接読み書きできます（ただし batch updates や diagnostics の利便性は落ちます）。

---

## License

MIT
