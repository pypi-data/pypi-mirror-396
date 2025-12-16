# -*- coding: utf-8 -*-
"""
Tests for the Subagent feature.

Tests cover:
- SubagentConfig creation and serialization
- SubagentResult creation and serialization
- SubagentPointer tracking
- TaskPlan subagent tracking
"""

import pytest
from datetime import datetime

from massgen.subagent.models import (
    SubagentConfig,
    SubagentResult,
    SubagentPointer,
    SubagentState,
)
from massgen.mcp_tools.planning.planning_dataclasses import TaskPlan


class TestSubagentConfig:
    """Tests for SubagentConfig dataclass."""

    def test_create_with_defaults(self):
        """Test creating config with default values."""
        config = SubagentConfig.create(
            task="Test task",
            parent_agent_id="parent_1",
        )
        assert config.task == "Test task"
        assert config.parent_agent_id == "parent_1"
        assert config.id.startswith("sub_")
        assert config.timeout_seconds == 300
        assert config.model is None
        assert config.context_files == []

    def test_create_with_custom_id(self):
        """Test creating config with custom ID."""
        config = SubagentConfig.create(
            task="Custom task",
            parent_agent_id="parent_1",
            subagent_id="custom_id",
        )
        assert config.id == "custom_id"

    def test_create_with_all_options(self):
        """Test creating config with all options specified."""
        config = SubagentConfig.create(
            task="Full config task",
            parent_agent_id="parent_1",
            subagent_id="full_config",
            model="gpt-4",
            timeout_seconds=600,
            context_files=["src/main.py", "README.md"],
            system_prompt="You are a test agent",
            metadata={"key": "value"},
        )
        assert config.id == "full_config"
        assert config.model == "gpt-4"
        assert config.timeout_seconds == 600
        assert config.context_files == ["src/main.py", "README.md"]
        assert config.system_prompt == "You are a test agent"
        assert config.metadata == {"key": "value"}

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = SubagentConfig.create(
            task="Test task",
            parent_agent_id="parent_1",
            subagent_id="test_id",
        )
        data = config.to_dict()
        assert data["id"] == "test_id"
        assert data["task"] == "Test task"
        assert data["parent_agent_id"] == "parent_1"
        assert "created_at" in data

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        config = SubagentConfig.create(
            task="Test task",
            parent_agent_id="parent_1",
            subagent_id="test_id",
        )
        data = config.to_dict()
        restored = SubagentConfig.from_dict(data)
        assert restored.id == config.id
        assert restored.task == config.task
        assert restored.parent_agent_id == config.parent_agent_id


class TestSubagentResult:
    """Tests for SubagentResult dataclass."""

    def test_create_success(self):
        """Test creating a successful result."""
        result = SubagentResult.create_success(
            subagent_id="test_sub",
            answer="Task completed successfully",
            workspace_path="/workspace/subagents/test_sub",
            files_created=["report.md"],
            execution_time_seconds=45.2,
        )
        assert result.success is True
        assert result.status == "completed"
        assert result.answer == "Task completed successfully"
        assert result.files_created == ["report.md"]
        assert result.execution_time_seconds == 45.2
        assert result.error is None

    def test_create_timeout(self):
        """Test creating a timeout result."""
        result = SubagentResult.create_timeout(
            subagent_id="test_sub",
            workspace_path="/workspace",
            files_created=["partial.md"],
            timeout_seconds=300.0,
        )
        assert result.success is False
        assert result.status == "timeout"
        assert result.answer is None
        assert "timeout" in result.error.lower()

    def test_create_error(self):
        """Test creating an error result."""
        result = SubagentResult.create_error(
            subagent_id="test_sub",
            error="Something went wrong",
        )
        assert result.success is False
        assert result.status == "error"
        assert result.error == "Something went wrong"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = SubagentResult.create_success(
            subagent_id="test_sub",
            answer="Done",
            workspace_path="/workspace",
            files_created=[],
            execution_time_seconds=10.0,
        )
        data = result.to_dict()
        assert data["subagent_id"] == "test_sub"
        assert data["success"] is True
        assert data["status"] == "completed"
        assert "workspace" in data


class TestSubagentPointer:
    """Tests for SubagentPointer dataclass."""

    def test_create_pointer(self):
        """Test creating a subagent pointer."""
        pointer = SubagentPointer(
            id="test_sub",
            task="Test task",
            workspace="/workspace/subagents/test_sub",
            status="running",
        )
        assert pointer.id == "test_sub"
        assert pointer.task == "Test task"
        assert pointer.status == "running"
        assert pointer.completed_at is None

    def test_mark_completed_success(self):
        """Test marking pointer completed with success."""
        pointer = SubagentPointer(
            id="test_sub",
            task="Test task",
            workspace="/workspace",
            status="running",
        )
        result = SubagentResult.create_success(
            subagent_id="test_sub",
            answer="Completed successfully with detailed output",
            workspace_path="/workspace",
            files_created=[],
            execution_time_seconds=10.0,
        )
        pointer.mark_completed(result)
        assert pointer.status == "completed"
        assert pointer.completed_at is not None
        assert pointer.result_summary is not None

    def test_mark_completed_failure(self):
        """Test marking pointer completed with failure."""
        pointer = SubagentPointer(
            id="test_sub",
            task="Test task",
            workspace="/workspace",
            status="running",
        )
        result = SubagentResult.create_error(
            subagent_id="test_sub",
            error="Failed",
        )
        pointer.mark_completed(result)
        assert pointer.status == "failed"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        pointer = SubagentPointer(
            id="test_sub",
            task="Test task",
            workspace="/workspace",
            status="running",
        )
        data = pointer.to_dict()
        assert data["id"] == "test_sub"
        assert data["task"] == "Test task"
        assert data["status"] == "running"


class TestTaskPlanSubagentTracking:
    """Tests for TaskPlan subagent tracking."""

    def test_add_subagent(self):
        """Test adding a subagent to task plan."""
        plan = TaskPlan(agent_id="test_agent")
        plan.add_subagent(
            subagent_id="sub_1",
            task="Research OAuth",
            workspace="/workspace/subagents/sub_1",
        )
        assert "sub_1" in plan.subagents
        assert plan.subagents["sub_1"]["task"] == "Research OAuth"
        assert plan.subagents["sub_1"]["status"] == "running"

    def test_update_subagent_status(self):
        """Test updating subagent status."""
        plan = TaskPlan(agent_id="test_agent")
        plan.add_subagent("sub_1", "Test task", "/workspace")
        plan.update_subagent_status("sub_1", "completed", "Task done")
        assert plan.subagents["sub_1"]["status"] == "completed"
        assert plan.subagents["sub_1"]["result_summary"] == "Task done"
        assert plan.subagents["sub_1"]["completed_at"] is not None

    def test_get_subagent(self):
        """Test getting a subagent by ID."""
        plan = TaskPlan(agent_id="test_agent")
        plan.add_subagent("sub_1", "Test task", "/workspace")
        sub = plan.get_subagent("sub_1")
        assert sub is not None
        assert sub["id"] == "sub_1"

    def test_get_subagent_not_found(self):
        """Test getting a non-existent subagent."""
        plan = TaskPlan(agent_id="test_agent")
        sub = plan.get_subagent("nonexistent")
        assert sub is None

    def test_to_dict_with_subagents(self):
        """Test serialization includes subagents."""
        plan = TaskPlan(agent_id="test_agent")
        plan.add_subagent("sub_1", "Test task", "/workspace")
        data = plan.to_dict()
        assert "subagents" in data
        assert "sub_1" in data["subagents"]

    def test_from_dict_with_subagents(self):
        """Test deserialization preserves subagents."""
        plan = TaskPlan(agent_id="test_agent")
        plan.add_subagent("sub_1", "Test task", "/workspace")
        data = plan.to_dict()
        restored = TaskPlan.from_dict(data)
        assert "sub_1" in restored.subagents
        assert restored.subagents["sub_1"]["task"] == "Test task"


class TestSubagentState:
    """Tests for SubagentState dataclass."""

    def test_create_state(self):
        """Test creating a subagent state."""
        config = SubagentConfig.create(
            task="Test task",
            parent_agent_id="parent_1",
        )
        state = SubagentState(config=config)
        assert state.status == "pending"
        assert state.result is None

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = SubagentConfig.create(
            task="Test task",
            parent_agent_id="parent_1",
        )
        state = SubagentState(config=config, status="running")
        data = state.to_dict()
        assert data["status"] == "running"
        assert "config" in data
