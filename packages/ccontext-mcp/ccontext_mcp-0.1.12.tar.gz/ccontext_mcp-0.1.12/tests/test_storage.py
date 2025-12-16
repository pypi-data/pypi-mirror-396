"""Tests for storage module."""

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


@pytest.fixture
def storage(tmp_path):
    """Create a storage instance with a temporary directory."""
    return ContextStorage(tmp_path)


class TestContextOperations:
    """Tests for context.yaml operations."""

    def test_load_empty_context(self, storage):
        """Loading non-existent context returns empty Context."""
        context = storage.load_context()
        assert context.milestones == []
        assert context.notes == []
        assert context.references == []

    def test_save_and_load_context(self, storage):
        """Save and load context with milestones, notes, references."""
        context = Context(
            milestones=[
                Milestone(
                    id="M1",
                    name="Phase 1",
                    description="First phase",
                    status=MilestoneStatus.DONE,
                    started="2024-01-01",
                    completed="2024-01-31",
                    outcomes="Completed successfully",
                ),
                Milestone(
                    id="M2",
                    name="Phase 2",
                    description="Second phase",
                    status=MilestoneStatus.ACTIVE,
                    started="2024-02-01",
                ),
            ],
            notes=[
                Note(id="N001", content="Important note", ttl=50),
            ],
            references=[
                Reference(id="R001", url="src/main.py", note="Main file", ttl=30),
            ],
        )

        storage.save_context(context)
        loaded = storage.load_context()

        assert len(loaded.milestones) == 2
        assert loaded.milestones[0].name == "Phase 1"
        assert loaded.milestones[0].status == MilestoneStatus.DONE
        assert loaded.milestones[1].status == MilestoneStatus.ACTIVE

        assert len(loaded.notes) == 1
        assert loaded.notes[0].content == "Important note"

        assert len(loaded.references) == 1
        assert loaded.references[0].url == "src/main.py"


class TestMilestoneOperations:
    """Tests for milestone operations."""

    def test_generate_milestone_id(self, storage):
        """Generate sequential milestone IDs."""
        context = Context()
        assert storage.generate_milestone_id(context) == "M1"

        context.milestones.append(
            Milestone(id="M1", name="Test", description="Test", status=MilestoneStatus.PENDING)
        )
        assert storage.generate_milestone_id(context) == "M2"

        context.milestones.append(
            Milestone(id="M5", name="Test", description="Test", status=MilestoneStatus.PENDING)
        )
        assert storage.generate_milestone_id(context) == "M6"

    def test_get_milestone(self, storage):
        """Get milestone by ID."""
        context = Context(
            milestones=[
                Milestone(id="M1", name="First", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M2", name="Second", description="...", status=MilestoneStatus.ACTIVE),
            ]
        )

        m1 = storage.get_milestone(context, "M1")
        assert m1 is not None
        assert m1.name == "First"

        m3 = storage.get_milestone(context, "M3")
        assert m3 is None

    def test_get_milestones_for_response(self, storage):
        """Only return recent done milestones + all active/pending."""
        context = Context(
            milestones=[
                Milestone(id="M1", name="Done 1", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M2", name="Done 2", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M3", name="Done 3", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M4", name="Done 4", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M5", name="Done 5", description="...", status=MilestoneStatus.DONE),
                Milestone(id="M6", name="Active", description="...", status=MilestoneStatus.ACTIVE),
                Milestone(id="M7", name="Pending", description="...", status=MilestoneStatus.PENDING),
            ]
        )

        result = storage.get_milestones_for_response(context)

        # Should have last 3 done (M3, M4, M5) + active + pending
        assert len(result) == 5
        assert result[0].id == "M3"
        assert result[1].id == "M4"
        assert result[2].id == "M5"
        assert result[3].id == "M6"
        assert result[4].id == "M7"


class TestNoteOperations:
    """Tests for note operations."""

    def test_generate_note_id(self, storage):
        """Generate sequential note IDs."""
        context = Context()
        assert storage.generate_note_id(context) == "N001"

        context.notes.append(Note(id="N001", content="Test", ttl=30))
        assert storage.generate_note_id(context) == "N002"

    def test_get_note_by_id(self, storage):
        """Get note by ID."""
        context = Context(
            notes=[
                Note(id="N001", content="First", ttl=50),
                Note(id="N002", content="Second", ttl=30),
            ]
        )

        n1 = storage.get_note_by_id(context, "N001")
        assert n1 is not None
        assert n1.content == "First"

        n3 = storage.get_note_by_id(context, "N003")
        assert n3 is None


class TestReferenceOperations:
    """Tests for reference operations."""

    def test_generate_reference_id(self, storage):
        """Generate sequential reference IDs."""
        context = Context()
        assert storage.generate_reference_id(context) == "R001"

        context.references.append(Reference(id="R001", url="test.py", note="Test", ttl=30))
        assert storage.generate_reference_id(context) == "R002"

    def test_get_reference_by_id(self, storage):
        """Get reference by ID."""
        context = Context(
            references=[
                Reference(id="R001", url="a.py", note="File A", ttl=50),
                Reference(id="R002", url="b.py", note="File B", ttl=30),
            ]
        )

        r1 = storage.get_reference_by_id(context, "R001")
        assert r1 is not None
        assert r1.url == "a.py"

        r3 = storage.get_reference_by_id(context, "R003")
        assert r3 is None


class TestTaskOperations:
    """Tests for task file operations."""

    def test_save_and_load_task(self, storage):
        """Save and load a task."""
        task = Task(
            id="T001",
            name="Test Task",
            goal="Complete testing",
            status=TaskStatus.ACTIVE,
            steps=[
                Step(id="S1", name="Step 1", acceptance="Done 1", status=StepStatus.DONE),
                Step(id="S2", name="Step 2", acceptance="Done 2", status=StepStatus.IN_PROGRESS),
            ],
        )

        storage.save_task(task)
        loaded = storage.load_task("T001")

        assert loaded is not None
        assert loaded.name == "Test Task"
        assert loaded.status == TaskStatus.ACTIVE
        assert len(loaded.steps) == 2
        assert loaded.steps[0].status == StepStatus.DONE

    def test_delete_task(self, storage):
        """Delete a task."""
        task = Task(id="T001", name="Test", goal="Test", status=TaskStatus.PLANNED, steps=[])
        storage.save_task(task)

        assert storage.load_task("T001") is not None
        assert storage.delete_task("T001") is True
        assert storage.load_task("T001") is None
        assert storage.delete_task("T001") is False

    def test_list_tasks(self, storage):
        """List tasks sorted by ID."""
        storage.save_task(Task(id="T003", name="Third", goal="...", status=TaskStatus.PLANNED, steps=[]))
        storage.save_task(Task(id="T001", name="First", goal="...", status=TaskStatus.DONE, steps=[]))
        storage.save_task(Task(id="T002", name="Second", goal="...", status=TaskStatus.ACTIVE, steps=[]))

        tasks = storage.list_tasks()
        assert len(tasks) == 3
        assert tasks[0].id == "T001"
        assert tasks[1].id == "T002"
        assert tasks[2].id == "T003"

    def test_generate_task_id(self, storage):
        """Generate sequential task IDs."""
        assert storage.generate_task_id() == "T001"

        storage.save_task(Task(id="T001", name="Test", goal="...", status=TaskStatus.PLANNED, steps=[]))
        assert storage.generate_task_id() == "T002"


class TestTtlDecay:
    """Tests for ttl decay and archiving."""

    def test_decay_ttl(self, storage):
        """Decay ttl for notes and references."""
        context = Context(
            milestones=[],
            notes=[
                Note(id="N001", content="High", ttl=50),
                Note(id="N003", content="Archive", ttl=0),
                Note(id="N002", content="Expire", ttl=1),
            ],
            references=[
                Reference(id="R001", url="a.py", note="High", ttl=30),
                Reference(id="R002", url="b.py", note="Archive", ttl=0),
            ],
        )

        context, archived_notes, archived_refs = storage.decay_ttl(context)

        # Active entries decremented (floored at 0) and kept (even when reaching ttl=0)
        assert len(context.notes) == 2
        assert context.notes[0].ttl == 49
        assert context.notes[1].ttl == 0
        assert len(context.references) == 1
        assert context.references[0].ttl == 29

        # Archived entries removed from active context (ttl==0 at start)
        assert sorted(n.id for n in archived_notes) == ["N003"]
        assert sorted(r.id for r in archived_refs) == ["R002"]

    def test_archive_entries(self, storage):
        """Archive notes and references to files."""
        notes = [Note(id="N001", content="Archived note", ttl=0)]
        refs = [Reference(id="R001", url="old.py", note="Old file", ttl=0)]

        storage.archive_entries(notes, refs)

        # Check archive files exist
        notes_path = storage._archive_notes_path()
        refs_path = storage._archive_refs_path()

        assert notes_path.exists()
        assert refs_path.exists()


def test_compute_version(tmp_path):
    """Test version computation for change detection."""
    storage = ContextStorage(tmp_path)
    
    # Empty context - should have a version
    v1 = storage.compute_version()
    assert isinstance(v1, str)
    assert len(v1) == 12
    
    # Same empty state - same version
    v2 = storage.compute_version()
    assert v1 == v2
    
    # Add context - version changes
    ctx = Context(
        milestones=[
            Milestone(id="M1", name="Test", description="Desc", status=MilestoneStatus.ACTIVE)
        ],
        notes=[],
        references=[]
    )
    storage.save_context(ctx)
    v3 = storage.compute_version()
    assert v3 != v1
    
    # Modify context - version changes again
    ctx.milestones[0].status = MilestoneStatus.DONE
    storage.save_context(ctx)
    v4 = storage.compute_version()
    assert v4 != v3
    
    # Add task - version changes
    task = Task(
        id="T001",
        name="Task",
        goal="Goal",
        status=TaskStatus.PLANNED,
        steps=[]
    )
    storage.save_task(task)
    v5 = storage.compute_version()
    assert v5 != v4
    
    # Version is deterministic - same content = same version
    v6 = storage.compute_version()
    assert v5 == v6
