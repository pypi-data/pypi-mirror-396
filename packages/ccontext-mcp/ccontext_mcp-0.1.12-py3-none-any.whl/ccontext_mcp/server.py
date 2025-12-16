"""MCP Server for ccontext."""

import json
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import ContextTools, TOOL_DESCRIPTIONS


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("ccontext-mcp")
    root_env = (os.environ.get("CCONTEXT_ROOT") or "").strip()
    if root_env:
        root = Path(root_env).expanduser()
        if not root.exists():
            raise ValueError(f"CCONTEXT_ROOT does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"CCONTEXT_ROOT must be a directory: {root}")
        root = root.resolve()
    else:
        root = Path.cwd()

    tools = ContextTools(root)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            # Context
            Tool(
                name="get_context",
                description=TOOL_DESCRIPTIONS["get_context"],
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="commit_updates",
                description=TOOL_DESCRIPTIONS["commit_updates"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dry_run": {
                            "type": "boolean",
                            "default": False,
                            "description": "Validate and preview changes without writing files",
                        },
                        "ops": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "op": {"type": "string", "description": "Operation type"},
                                },
                                "required": ["op"],
                                "additionalProperties": True,
                            },
                            "description": "List of operations to apply in order",
                        },
                    },
                    "required": ["ops"],
                },
            ),
            # Vision/Sketch tools
            Tool(
                name="update_vision",
                description=TOOL_DESCRIPTIONS["update_vision"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vision": {"type": "string", "description": "Project vision statement"},
                    },
                    "required": ["vision"],
                },
            ),
            Tool(
                name="update_sketch",
                description=TOOL_DESCRIPTIONS["update_sketch"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sketch": {"type": "string", "description": "Execution blueprint (markdown)"},
                    },
                    "required": ["sketch"],
                },
            ),
            # Presence tools
            Tool(
                name="get_presence",
                description=TOOL_DESCRIPTIONS["get_presence"],
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="update_my_status",
                description=TOOL_DESCRIPTIONS["update_my_status"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Your agent ID (e.g., peer-a)"},
                        "status": {
                            "type": "string",
                            "description": "What you're doing/thinking (1-2 sentences)",
                        },
                    },
                    "required": ["agent_id", "status"],
                },
            ),
            Tool(
                name="clear_status",
                description=TOOL_DESCRIPTIONS["clear_status"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Your agent ID (e.g., peer-a)"},
                    },
                    "required": ["agent_id"],
                },
            ),
            # Milestone tools
            Tool(
                name="create_milestone",
                description=TOOL_DESCRIPTIONS["create_milestone"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Milestone name/goal"},
                        "description": {"type": "string", "description": "Detailed description"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "active", "done"],
                            "default": "pending",
                            "description": "Initial status",
                        },
                    },
                    "required": ["name", "description"],
                },
            ),
            Tool(
                name="update_milestone",
                description=TOOL_DESCRIPTIONS["update_milestone"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "milestone_id": {"type": "string", "description": "Milestone ID (M1, M2...)"},
                        "name": {"type": "string", "description": "New name"},
                        "description": {"type": "string", "description": "New description"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "active", "done"],
                            "description": "New status",
                        },
                    },
                    "required": ["milestone_id"],
                },
            ),
            Tool(
                name="complete_milestone",
                description=TOOL_DESCRIPTIONS["complete_milestone"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "milestone_id": {"type": "string", "description": "Milestone ID"},
                        "outcomes": {"type": "string", "description": "Results summary"},
                    },
                    "required": ["milestone_id", "outcomes"],
                },
            ),
            Tool(
                name="remove_milestone",
                description=TOOL_DESCRIPTIONS["remove_milestone"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "milestone_id": {"type": "string", "description": "Milestone ID to remove"},
                    },
                    "required": ["milestone_id"],
                },
            ),
            # Task tools
            Tool(
                name="list_tasks",
                description=TOOL_DESCRIPTIONS["list_tasks"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Get specific task by ID"},
                        "status": {
                            "type": "string",
                            "enum": ["planned", "active", "done"],
                            "description": "Filter by status",
                        },
                        "assignee": {"type": "string", "description": "Filter by assignee"},
                        "include_archived": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include archived tasks",
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="create_task",
                description=TOOL_DESCRIPTIONS["create_task"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Task name"},
                        "goal": {"type": "string", "description": "Completion criteria"},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "acceptance": {"type": "string", "description": "Acceptance criteria"},
                                },
                                "required": ["name", "acceptance"],
                            },
                            "description": "List of steps with acceptance criteria",
                        },
                        "task_id": {"type": "string", "description": "Custom task ID (optional)"},
                        "milestone_id": {"type": "string", "description": "Associated milestone ID (optional)"},
                        "assignee": {"type": "string", "description": "Assignee"},
                    },
                    "required": ["name", "goal", "steps"],
                },
            ),
            Tool(
                name="update_task",
                description=TOOL_DESCRIPTIONS["update_task"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to update"},
                        "status": {
                            "type": "string",
                            "enum": ["planned", "active", "done"],
                            "description": "New status",
                        },
                        "name": {"type": "string", "description": "New name"},
                        "goal": {"type": "string", "description": "New goal"},
                        "assignee": {"type": "string", "description": "New assignee"},
                        "milestone_id": {"type": "string", "description": "Associated milestone ID (optional)"},
                        "step_id": {"type": "string", "description": "Step ID to update"},
                        "step_status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "done"],
                            "description": "New step status",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="delete_task",
                description=TOOL_DESCRIPTIONS["delete_task"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to delete"},
                    },
                    "required": ["task_id"],
                },
            ),
            # Note tools
            Tool(
                name="add_note",
                description=TOOL_DESCRIPTIONS["add_note"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Note content"},
                        "ttl": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 100,
                            "default": 30,
                            "description": "Initial ttl (recommended: 10 short-term, 30 normal, 100 long-term)",
                        },
                    },
                    "required": ["content"],
                },
            ),
            Tool(
                name="update_note",
                description=TOOL_DESCRIPTIONS["update_note"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "Note ID (N001, N002...)"},
                        "content": {"type": "string", "description": "New content"},
                        "ttl": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "New ttl",
                        },
                    },
                    "required": ["note_id"],
                },
            ),
            Tool(
                name="remove_note",
                description=TOOL_DESCRIPTIONS["remove_note"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "Note ID to remove"},
                    },
                    "required": ["note_id"],
                },
            ),
            # Reference tools
            Tool(
                name="add_reference",
                description=TOOL_DESCRIPTIONS["add_reference"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "File path or URL"},
                        "note": {"type": "string", "description": "Description"},
                        "ttl": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 100,
                            "default": 30,
                            "description": "Initial ttl (recommended: 10 short-term, 30 normal, 100 long-term)",
                        },
                    },
                    "required": ["url", "note"],
                },
            ),
            Tool(
                name="update_reference",
                description=TOOL_DESCRIPTIONS["update_reference"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "string", "description": "Reference ID (R001...)"},
                        "url": {"type": "string", "description": "New URL"},
                        "note": {"type": "string", "description": "New description"},
                        "ttl": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "New ttl",
                        },
                    },
                    "required": ["reference_id"],
                },
            ),
            Tool(
                name="remove_reference",
                description=TOOL_DESCRIPTIONS["remove_reference"],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "string", "description": "Reference ID to remove"},
                    },
                    "required": ["reference_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        try:
            # Context
            if name == "get_context":
                result = tools.get_context()
            elif name == "commit_updates":
                result = tools.commit_updates(
                    ops=arguments["ops"],
                    dry_run=arguments.get("dry_run", False),
                )

            # Vision/Sketch tools
            elif name == "update_vision":
                result = tools.update_vision(vision=arguments["vision"])
            elif name == "update_sketch":
                result = tools.update_sketch(sketch=arguments["sketch"])

            # Presence tools
            elif name == "get_presence":
                result = tools.get_presence()
            elif name == "update_my_status":
                result = tools.update_my_status(
                    agent_id=arguments["agent_id"],
                    status=arguments["status"],
                )
            elif name == "clear_status":
                result = tools.clear_status(agent_id=arguments["agent_id"])

            # Milestone tools
            elif name == "create_milestone":
                result = tools.create_milestone(
                    name=arguments["name"],
                    description=arguments["description"],
                    status=arguments.get("status", "pending"),
                )
            elif name == "update_milestone":
                result = tools.update_milestone(
                    milestone_id=arguments["milestone_id"],
                    name=arguments.get("name"),
                    description=arguments.get("description"),
                    status=arguments.get("status"),
                )
            elif name == "complete_milestone":
                result = tools.complete_milestone(
                    milestone_id=arguments["milestone_id"],
                    outcomes=arguments["outcomes"],
                )
            elif name == "remove_milestone":
                result = tools.remove_milestone(milestone_id=arguments["milestone_id"])

            # Task tools
            elif name == "list_tasks":
                result = tools.list_tasks(
                    task_id=arguments.get("task_id"),
                    status=arguments.get("status"),
                    assignee=arguments.get("assignee"),
                    include_archived=arguments.get("include_archived", False),
                )
            elif name == "create_task":
                result = tools.create_task(
                    name=arguments["name"],
                    goal=arguments["goal"],
                    steps=arguments["steps"],
                    task_id=arguments.get("task_id"),
                    assignee=arguments.get("assignee"),
                    milestone_id=arguments.get("milestone_id"),
                )
            elif name == "update_task":
                result = tools.update_task(
                    task_id=arguments["task_id"],
                    status=arguments.get("status"),
                    name=arguments.get("name"),
                    goal=arguments.get("goal"),
                    assignee=arguments.get("assignee"),
                    milestone_id=arguments.get("milestone_id"),
                    step_id=arguments.get("step_id"),
                    step_status=arguments.get("step_status"),
                    steps=arguments.get("steps"),
                )
            elif name == "delete_task":
                result = tools.delete_task(task_id=arguments["task_id"])

            # Note tools
            elif name == "add_note":
                result = tools.add_note(
                    content=arguments["content"],
                    ttl=arguments.get("ttl", 30),
                )
            elif name == "update_note":
                result = tools.update_note(
                    note_id=arguments["note_id"],
                    content=arguments.get("content"),
                    ttl=arguments.get("ttl"),
                )
            elif name == "remove_note":
                result = tools.remove_note(note_id=arguments["note_id"])

            # Reference tools
            elif name == "add_reference":
                result = tools.add_reference(
                    url=arguments["url"],
                    note=arguments["note"],
                    ttl=arguments.get("ttl", 30),
                )
            elif name == "update_reference":
                result = tools.update_reference(
                    reference_id=arguments["reference_id"],
                    url=arguments.get("url"),
                    note=arguments.get("note"),
                    ttl=arguments.get("ttl"),
                )
            elif name == "remove_reference":
                result = tools.remove_reference(reference_id=arguments["reference_id"])

            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    return server


async def main():
    """Run the MCP server."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Entry point for the server."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
