"""Tests for tools module."""

import pytest
from pathlib import Path

from ccontext_mcp.schema import (
    Context,
    Milestone,
    MilestoneStatus,
    Note,
    Reference,
    Task,
    TaskStatus,
    Step,
    StepStatus,
)
from ccontext_mcp.storage import ContextStorage
from ccontext_mcp.tools import ContextTools


@pytest.fixture
def tools(tmp_path):
    """Create a ContextTools instance with a temporary directory."""
    return ContextTools(tmp_path)


@pytest.fixture
def tools_with_data(tmp_path):
    """Create a ContextTools instance with pre-populated data."""
    tools = ContextTools(tmp_path)
    storage = tools.storage

    # Create context with milestones, notes, references
    context = Context(
        milestones=[
            Milestone(
                id="M1",
                name="Setup",
                description="Initial setup",
                status=MilestoneStatus.DONE,
                started="2024-01-01",
                completed="2024-01-15",
                outcomes="Environment configured",
            ),
            Milestone(
                id="M2",
                name="Development",
                description="Main development",
                status=MilestoneStatus.ACTIVE,
                started="2024-01-16",
            ),
        ],
        notes=[
            Note(id="N001", content="Important: use pytest", score=50),
            Note(id="N002", content="Watch for memory leaks", score=30),
        ],
        references=[
            Reference(id="R001", url="src/main.py", note="Entry point", score=40),
        ],
    )
    storage.save_context(context)

    # Create a task
    task = Task(
        id="T001",
        name="Implement feature X",
        goal="Feature X works end-to-end",
        status=TaskStatus.ACTIVE,
        assignee="PeerA",
        created_at="2024-01-16T10:00:00Z",
        steps=[
            Step(id="S1", name="Design", acceptance="Design doc ready", status=StepStatus.DONE),
            Step(id="S2", name="Code", acceptance="Code written", status=StepStatus.IN_PROGRESS),
            Step(id="S3", name="Test", acceptance="Tests pass", status=StepStatus.PENDING),
        ],
    )
    storage.save_task(task)

    return tools


class TestGetContext:
    """Tests for get_context tool."""

    def test_get_empty_context(self, tools):
        """Get context when empty."""
        result = tools.get_context()

        assert result["context"]["milestones"] == []
        assert result["context"]["notes"] == []
        assert result["context"]["references"] == []
        assert result["context"]["tasks_summary"]["total"] == 0
        assert result["context"]["active_task"] is None

    def test_get_full_context(self, tools_with_data):
        """Get context with data."""
        result = tools_with_data.get_context()

        # Milestones
        assert len(result["context"]["milestones"]) == 2
        assert result["context"]["milestones"][0]["name"] == "Setup"
        assert result["context"]["milestones"][1]["name"] == "Development"

        # Notes (scores decayed by 1)
        assert len(result["context"]["notes"]) == 2
        assert result["context"]["notes"][0]["content"] == "Important: use pytest"
        assert result["context"]["notes"][0]["score"] == 49  # Decayed from 50

        # References
        assert len(result["context"]["references"]) == 1
        assert result["context"]["references"][0]["url"] == "src/main.py"

        # Tasks
        assert result["context"]["tasks_summary"]["total"] == 1
        assert result["context"]["tasks_summary"]["active"] == 1
        assert result["context"]["active_task"]["id"] == "T001"


class TestMilestoneTools:
    """Tests for milestone tools."""

    def test_create_milestone(self, tools):
        """Create a new milestone."""
        result = tools.create_milestone(
            name="Phase 1",
            description="First phase of development",
            status="pending",
        )

        assert result["id"] == "M1"
        assert result["name"] == "Phase 1"
        assert result["status"] == "pending"

    def test_create_active_milestone(self, tools):
        """Create an active milestone sets started date."""
        result = tools.create_milestone(
            name="Active Phase",
            description="Currently in progress",
            status="active",
        )

        assert result["status"] == "active"
        assert result["started"] is not None

    def test_update_milestone(self, tools_with_data):
        """Update an existing milestone."""
        result = tools_with_data.update_milestone(
            milestone_id="M2",
            name="Development v2",
            description="Updated description",
        )

        assert result["id"] == "M2"
        assert result["name"] == "Development v2"
        assert result["description"] == "Updated description"

    def test_update_milestone_not_found(self, tools):
        """Update non-existent milestone raises error."""
        with pytest.raises(ValueError, match="Milestone not found"):
            tools.update_milestone(milestone_id="M99", name="Test")

    def test_complete_milestone(self, tools_with_data):
        """Complete a milestone with outcomes."""
        result = tools_with_data.complete_milestone(
            milestone_id="M2",
            outcomes="Feature X completed successfully",
        )

        assert result["status"] == "done"
        assert result["completed"] is not None
        assert result["outcomes"] == "Feature X completed successfully"

    def test_remove_milestone(self, tools_with_data):
        """Remove a milestone."""
        result = tools_with_data.remove_milestone(milestone_id="M1")

        assert result["deleted"] is True
        assert result["milestone_id"] == "M1"

        # Verify removed
        context = tools_with_data.storage.load_context()
        assert len(context.milestones) == 1
        assert context.milestones[0].id == "M2"


class TestTaskTools:
    """Tests for task tools."""

    def test_list_all_tasks(self, tools_with_data):
        """List all tasks."""
        result = tools_with_data.list_tasks()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "T001"

    def test_list_tasks_by_status(self, tools_with_data):
        """Filter tasks by status."""
        result = tools_with_data.list_tasks(status="active")
        assert len(result) == 1

        result = tools_with_data.list_tasks(status="done")
        assert len(result) == 0

    def test_get_task_by_id(self, tools_with_data):
        """Get specific task by ID."""
        result = tools_with_data.list_tasks(task_id="T001")

        assert isinstance(result, dict)
        assert result["id"] == "T001"
        assert result["name"] == "Implement feature X"

    def test_create_task(self, tools):
        """Create a new task."""
        result = tools.create_task(
            name="New Task",
            goal="Complete the task",
            steps=[
                {"name": "Step 1", "acceptance": "First done"},
                {"name": "Step 2", "acceptance": "Second done"},
            ],
            assignee="PeerB",
        )

        assert result["id"] == "T001"
        assert result["name"] == "New Task"
        assert result["status"] == "planned"
        assert len(result["steps"]) == 2
        assert result["assignee"] == "PeerB"

    def test_update_task_status(self, tools_with_data):
        """Update task status."""
        result = tools_with_data.update_task(
            task_id="T001",
            status="done",
        )

        assert result["status"] == "done"

    def test_update_step_status(self, tools_with_data):
        """Update a step's status."""
        result = tools_with_data.update_task(
            task_id="T001",
            step_id="S2",
            step_status="done",
        )

        assert result["steps"][1]["status"] == "done"

    def test_delete_task(self, tools_with_data):
        """Delete a task."""
        result = tools_with_data.delete_task(task_id="T001")

        assert result["deleted"] is True

        # Verify deleted
        with pytest.raises(ValueError, match="Task not found"):
            tools_with_data.list_tasks(task_id="T001")


class TestNoteTools:
    """Tests for note tools."""

    def test_add_note(self, tools):
        """Add a new note."""
        result = tools.add_note(content="New discovery", score=50)

        assert result["id"] == "N001"
        assert result["content"] == "New discovery"
        assert result["score"] == 50

    def test_add_note_default_score(self, tools):
        """Add note with default score."""
        result = tools.add_note(content="Default score note")

        assert result["score"] == 15

    def test_add_note_invalid_score(self, tools):
        """Add note with invalid score raises error."""
        with pytest.raises(ValueError, match="Score must be between"):
            tools.add_note(content="Test", score=5)

        with pytest.raises(ValueError, match="Score must be between"):
            tools.add_note(content="Test", score=150)

    def test_update_note(self, tools_with_data):
        """Update a note."""
        result = tools_with_data.update_note(
            note_id="N001",
            content="Updated content",
            score=80,
        )

        assert result["content"] == "Updated content"
        assert result["score"] == 80

    def test_update_note_not_found(self, tools):
        """Update non-existent note raises error."""
        with pytest.raises(ValueError, match="Note not found"):
            tools.update_note(note_id="N999", content="Test")

    def test_remove_note(self, tools_with_data):
        """Remove a note."""
        result = tools_with_data.remove_note(note_id="N001")

        assert result["deleted"] is True

        # Verify removed
        context = tools_with_data.storage.load_context()
        assert len(context.notes) == 1
        assert context.notes[0].id == "N002"


class TestReferenceTools:
    """Tests for reference tools."""

    def test_add_reference(self, tools):
        """Add a new reference."""
        result = tools.add_reference(
            url="docs/api.md",
            note="API documentation",
            score=60,
        )

        assert result["id"] == "R001"
        assert result["url"] == "docs/api.md"
        assert result["note"] == "API documentation"
        assert result["score"] == 60

    def test_add_reference_default_score(self, tools):
        """Add reference with default score."""
        result = tools.add_reference(url="test.py", note="Test file")

        assert result["score"] == 15

    def test_update_reference(self, tools_with_data):
        """Update a reference."""
        result = tools_with_data.update_reference(
            reference_id="R001",
            note="Updated description",
            score=70,
        )

        assert result["note"] == "Updated description"
        assert result["score"] == 70

    def test_update_reference_not_found(self, tools):
        """Update non-existent reference raises error."""
        with pytest.raises(ValueError, match="Reference not found"):
            tools.update_reference(reference_id="R999", note="Test")

    def test_remove_reference(self, tools_with_data):
        """Remove a reference."""
        result = tools_with_data.remove_reference(reference_id="R001")

        assert result["deleted"] is True

        # Verify removed
        context = tools_with_data.storage.load_context()
        assert len(context.references) == 0


class TestExpiringIndicator:
    """Tests for the expiring indicator on notes/references."""

    def test_note_expiring_property(self, tools):
        """Notes with score <= 0 should be marked as expiring."""
        # Add notes with different scores
        tools.add_note(content="High score", score=50)
        tools.add_note(content="Low score", score=10)

        # Manually lower score to test expiring
        # Note: get_context() decays scores by 1, so set to 1 to get 0 after decay
        context = tools.storage.load_context()
        context.notes[1].score = 1  # Will become 0 after decay
        tools.storage.save_context(context)

        result = tools.get_context()

        # High score note should not be expiring (49 after decay)
        assert result["context"]["notes"][0]["expiring"] is False

        # Low score note should be expiring (0 after decay)
        assert result["context"]["notes"][1]["expiring"] is True
        assert result["context"]["notes"][1]["score"] == 0


def test_get_context_returns_version(tmp_path):
    """Test that get_context returns version field."""
    tools = ContextTools(tmp_path)
    
    # Get context
    result = tools.get_context()
    
    # Should have version field
    assert "version" in result
    assert "context" in result
    assert isinstance(result["version"], str)
    assert len(result["version"]) == 12
    
    # Version should be consistent for same content
    result2 = tools.get_context()
    # Note: version may differ due to score decay
    # but structure should be same
    assert "version" in result2
    assert isinstance(result2["version"], str)


def test_version_changes_on_update(tmp_path):
    """Test that version changes when context is updated."""
    tools = ContextTools(tmp_path)
    
    # Initial version
    v1 = tools.get_context()["version"]
    
    # Create milestone
    tools.create_milestone(name="Test", description="Test milestone")
    v2 = tools.get_context()["version"]
    assert v2 != v1, "Version should change after creating milestone"
    
    # Create task
    tools.create_task(name="Task", goal="Test goal", steps=[])
    v3 = tools.get_context()["version"]
    assert v3 != v2, "Version should change after creating task"
    
    # Add note
    tools.add_note(content="Test note", score=50)
    v4 = tools.get_context()["version"]
    assert v4 != v3, "Version should change after adding note"
