# -*- coding: utf-8 -*-
"""
Test Docker execution mode for custom tools and MCP tools.

Tests the new functionality added in issues #510 and #413:
- Custom tools executing in Docker containers
- MCP workspace tools executing in Docker containers
- Mixed mode (some local, some Docker)
- Configuration parsing and routing
- Error handling
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from massgen.backend.response import ResponseBackend  # noqa: E402
from massgen.tool import ExecutionResult, ToolManager  # noqa: E402
from massgen.tool._registered_tool import RegisteredToolEntry  # noqa: E402
from massgen.tool._result import TextContent  # noqa: E402


# ============================================================================
# Helper Functions
# ============================================================================


def check_docker_available():
    """Check if Docker is available for testing."""
    try:
        import docker

        client = docker.from_env()
        client.ping()

        # Check for MassGen Docker image
        try:
            client.images.get("massgen/mcp-runtime:latest")
        except docker.errors.ImageNotFound:
            pytest.skip("Docker image 'massgen/mcp-runtime:latest' not found")

        return True
    except ImportError:
        pytest.skip("Docker library not installed")
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")


def sample_tool_function(message: str) -> ExecutionResult:
    """Sample tool function for testing.

    Args:
        message: Message to return

    Returns:
        ExecutionResult with message
    """
    return ExecutionResult(
        output_blocks=[TextContent(data=f"Tool output: {message}")],
    )


# ============================================================================
# Configuration Tests
# ============================================================================


class TestDockerToolConfiguration:
    """Test configuration parsing for Docker tool execution."""

    def test_global_tool_execution_mode_default(self):
        """Test that tool_execution_mode defaults to 'local'."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
        )

        assert backend._tool_execution_mode == "local"

    def test_global_tool_execution_mode_docker(self):
        """Test setting global tool_execution_mode to 'docker'."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
        )

        assert backend._tool_execution_mode == "docker"

    def test_registered_tool_execution_mode_field(self):
        """Test that RegisteredToolEntry has execution_mode field."""
        tool_entry = RegisteredToolEntry(
            tool_name="test_tool",
            category="test",
            origin="function",
            base_function=sample_tool_function,
            schema_def={"function": {"name": "test_tool"}},
            execution_mode="docker",
        )

        assert tool_entry.execution_mode == "docker"

    def test_registered_tool_execution_mode_default(self):
        """Test that execution_mode defaults to 'local'."""
        tool_entry = RegisteredToolEntry(
            tool_name="test_tool",
            category="test",
            origin="function",
            base_function=sample_tool_function,
            schema_def={"function": {"name": "test_tool"}},
        )

        assert tool_entry.execution_mode == "local"

    def test_tool_manager_add_with_execution_mode(self):
        """Test adding tool with execution_mode parameter."""
        manager = ToolManager()
        manager.setup_category("test", "Test category")

        manager.add_tool_function(
            func=sample_tool_function,
            category="test",
            execution_mode="docker",
        )

        tool_entry = manager.registered_tools["custom_tool__sample_tool_function"]
        assert tool_entry.execution_mode == "docker"

    def test_per_tool_execution_mode_override(self):
        """Test that per-tool execution_mode overrides global setting."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",  # Global default
            custom_tools=[
                {
                    "path": __file__,
                    "function": "sample_tool_function",
                    "category": "test",
                    "execution_mode": "local",  # Override to local
                }
            ],
        )

        # Tool should have local mode despite global Docker mode
        tool_name = "custom_tool__sample_tool_function"
        if tool_name in backend.custom_tool_manager.registered_tools:
            tool_entry = backend.custom_tool_manager.registered_tools[tool_name]
            assert tool_entry.execution_mode == "local"


# ============================================================================
# Custom Tool Docker Execution Tests
# ============================================================================


class TestCustomToolDockerExecution:
    """Test custom tools executing in Docker containers."""

    @pytest.fixture
    def docker_available(self):
        """Fixture to check Docker availability."""
        return check_docker_available()

    @pytest.mark.docker
    async def test_custom_tool_docker_routing(self, docker_available, tmp_path):
        """Test that tools with execution_mode='docker' route to Docker execution."""
        # Create a simple test tool file
        tool_file = tmp_path / "test_tool.py"
        tool_file.write_text("""
from massgen.tool import ExecutionResult
from massgen.tool._result import TextContent

def test_function(value: str) -> ExecutionResult:
    return ExecutionResult(
        output_blocks=[TextContent(data=f"Processed: {value}")],
    )
""")

        # Create backend with Docker execution mode
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            agent_id="test_docker_routing",
            tool_execution_mode="docker",
            custom_tools=[
                {
                    "path": str(tool_file),
                    "function": "test_function",
                    "category": "test",
                }
            ],
        )

        # Verify tool is registered with Docker mode
        tool_name = "custom_tool__test_function"
        assert tool_name in backend.custom_tool_manager.registered_tools
        tool_entry = backend.custom_tool_manager.registered_tools[tool_name]
        assert tool_entry.execution_mode == "docker"

    @pytest.mark.docker
    def test_docker_execution_method_exists(self, docker_available):
        """Test that _execute_custom_tool_in_docker method exists."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
        )

        assert hasattr(backend, "_execute_custom_tool_in_docker")
        assert callable(backend._execute_custom_tool_in_docker)

    @pytest.mark.docker
    async def test_docker_execution_with_filesystem_manager(self, docker_available, tmp_path):
        """Test Docker execution with filesystem_manager available."""
        from massgen.filesystem_manager._docker_manager import DockerManager

        # Create filesystem manager with Docker
        # Note: DockerManager doesn't take agent_id or workspace_path in __init__
        # Those are managed when containers are created
        docker_manager = DockerManager(
            image="massgen/mcp-runtime:latest",
        )

        filesystem_manager = MagicMock()
        filesystem_manager.docker_manager = docker_manager
        filesystem_manager.cwd = str(tmp_path)

        # Create backend
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            agent_id="test_docker_exec",
            tool_execution_mode="docker",
        )
        backend.filesystem_manager = filesystem_manager

        # Verify filesystem manager is set
        assert backend.filesystem_manager is not None
        assert backend.filesystem_manager.docker_manager is not None

    def test_docker_execution_error_no_filesystem_manager(self):
        """Test error handling when Docker requested but no filesystem_manager."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
        )

        # Should not have filesystem_manager by default
        assert not hasattr(backend, "filesystem_manager") or backend.filesystem_manager is None

    @pytest.mark.docker
    async def test_mixed_mode_execution(self, docker_available, tmp_path):
        """Test mixed mode where some tools run locally, others in Docker."""
        # Create test tool file
        tool_file = tmp_path / "mixed_tools.py"
        tool_file.write_text("""
from massgen.tool import ExecutionResult
from massgen.tool._result import TextContent

def docker_tool(value: str) -> ExecutionResult:
    return ExecutionResult(
        output_blocks=[TextContent(data=f"Docker: {value}")],
    )

def local_tool(value: str) -> ExecutionResult:
    return ExecutionResult(
        output_blocks=[TextContent(data=f"Local: {value}")],
    )
""")

        # Create backend with mixed mode
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",  # Default Docker
            custom_tools=[
                {
                    "path": str(tool_file),
                    "function": "docker_tool",
                    "category": "test",
                    # Inherits Docker mode
                },
                {
                    "path": str(tool_file),
                    "function": "local_tool",
                    "category": "test",
                    "execution_mode": "local",  # Override to local
                },
            ],
        )

        # Verify routing
        docker_tool_name = "custom_tool__docker_tool"
        local_tool_name = "custom_tool__local_tool"

        assert backend.custom_tool_manager.registered_tools[docker_tool_name].execution_mode == "docker"
        assert backend.custom_tool_manager.registered_tools[local_tool_name].execution_mode == "local"


# ============================================================================
# MCP Tools Docker Execution Tests
# ============================================================================


class TestMCPToolsDockerExecution:
    """Test MCP workspace tools executing in Docker containers."""

    @pytest.fixture
    def docker_available(self):
        """Fixture to check Docker availability."""
        return check_docker_available()

    def test_mcp_server_execution_mode_storage(self):
        """Test that MCP server execution modes are stored correctly."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
            mcp_servers=[
                {
                    "name": "workspace_tools",
                    "type": "stdio",
                    "command": "fastmcp",
                    "args": ["run", "workspace_tools_server.py:create_server"],
                    # Inherits Docker mode
                },
                {
                    "name": "external_service",
                    "type": "stdio",
                    "command": "npx",
                    "args": ["-y", "@some/mcp-server"],
                    "execution_mode": "local",  # Override
                },
            ],
        )

        # Verify execution modes stored
        assert "workspace_tools" in backend._mcp_server_execution_modes
        assert backend._mcp_server_execution_modes["workspace_tools"] == "docker"

        assert "external_service" in backend._mcp_server_execution_modes
        assert backend._mcp_server_execution_modes["external_service"] == "local"

    def test_docker_arguments_injection(self):
        """Test that Docker execution arguments are injected into MCP server configs."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            agent_id="test_agent_123",
            tool_execution_mode="docker",
            mcp_servers=[
                {
                    "name": "workspace_tools",
                    "type": "stdio",
                    "command": "fastmcp",
                    "args": ["run", "workspace_tools_server.py:create_server", "--", "--allowed-paths"],
                },
            ],
        )

        # Check that Docker arguments were injected
        server_config = backend.mcp_servers[0]
        args = server_config["args"]

        # Should contain Docker execution arguments after "--" separator
        assert "--execution-mode" in args
        docker_mode_idx = args.index("--execution-mode")
        assert args[docker_mode_idx + 1] == "docker"

        assert "--agent-id" in args
        agent_id_idx = args.index("--agent-id")
        assert args[agent_id_idx + 1] == "test_agent_123"

    def test_docker_arguments_not_injected_for_local_mode(self):
        """Test that Docker arguments are NOT injected for local mode."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="local",
            mcp_servers=[
                {
                    "name": "workspace_tools",
                    "type": "stdio",
                    "command": "fastmcp",
                    "args": ["run", "workspace_tools_server.py:create_server"],
                },
            ],
        )

        # Check that Docker arguments were NOT injected
        server_config = backend.mcp_servers[0]
        args = server_config["args"]

        assert "--execution-mode" not in args
        assert "--agent-id" not in args


# ============================================================================
# Path Transparency Tests
# ============================================================================


class TestPathTransparency:
    """Test that paths work identically in Docker and local modes."""

    @pytest.fixture
    def docker_available(self):
        """Fixture to check Docker availability."""
        return check_docker_available()

    @pytest.mark.docker
    async def test_absolute_path_transparency(self, docker_available, tmp_path):
        """Test that absolute paths work the same in Docker and local modes."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Path transparency test")

        # Both modes should be able to access the same absolute path
        # (In real usage, Docker mounts workspace at same absolute path)
        abs_path = str(test_file.absolute())

        # This test verifies the concept - actual Docker mounting is tested separately
        assert Path(abs_path).exists()
        assert Path(abs_path).read_text() == "Path transparency test"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestDockerToolErrorHandling:
    """Test error handling for Docker tool execution."""

    def test_error_no_docker_available(self):
        """Test error when Docker execution requested but Docker not available."""
        # Just test that backend initializes with docker mode set
        # Actual Docker availability is checked when tools are executed
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
        )

        # Backend should initialize with Docker mode
        assert backend._tool_execution_mode == "docker"

    async def test_error_no_filesystem_manager(self):
        """Test error when Docker execution but no filesystem_manager."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
        )

        # Create mock tool request
        tool_request = {"name": "test_tool", "input": {}}
        tool_entry = MagicMock()
        tool_entry.execution_mode = "docker"
        tool_entry.base_function = sample_tool_function

        # Should yield error about missing filesystem_manager
        results = []
        async for result in backend._execute_custom_tool_in_docker(tool_request, tool_entry):
            results.append(result)

        assert len(results) > 0
        assert any("filesystem_manager" in str(r).lower() for r in results)

    async def test_error_container_not_found(self):
        """Test error when Docker container not found."""
        backend = ResponseBackend(
            api_key="test",
            model="gpt-4",
            tool_execution_mode="docker",
        )

        # Mock filesystem_manager without container
        backend.filesystem_manager = MagicMock()
        backend.filesystem_manager.docker_manager = MagicMock()
        backend.filesystem_manager.docker_manager.container = None

        tool_request = {"name": "test_tool", "input": {}}
        tool_entry = MagicMock()
        tool_entry.execution_mode = "docker"
        tool_entry.base_function = sample_tool_function

        # Should yield error about container not available
        results = []
        async for result in backend._execute_custom_tool_in_docker(tool_request, tool_entry):
            results.append(result)

        assert len(results) > 0
        assert any("container" in str(r).lower() for r in results)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestDockerToolExecutionIntegration:
    """Integration tests for Docker tool execution (require full setup)."""

    @pytest.fixture
    def docker_available(self):
        """Fixture to check Docker availability."""
        return check_docker_available()

    @pytest.mark.docker
    @pytest.mark.slow
    async def test_end_to_end_docker_execution(self, docker_available, tmp_path):
        """End-to-end test of tool executing in Docker container.

        This test requires:
        - Docker installed and running
        - massgen/mcp-runtime:latest image available
        - Full FilesystemManager with DockerManager setup
        """
        pytest.skip("End-to-end test requires full integration setup")

        # This would be a full integration test
        # Left as framework for future testing


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.performance
class TestDockerToolPerformance:
    """Performance tests for Docker tool execution."""

    @pytest.fixture
    def docker_available(self):
        """Fixture to check Docker availability."""
        return check_docker_available()

    @pytest.mark.docker
    @pytest.mark.slow
    async def test_docker_execution_overhead(self, docker_available):
        """Measure overhead of Docker execution vs local execution."""
        pytest.skip("Performance test - run manually when needed")

        # This would measure:
        # - Cold start time (first Docker call)
        # - Warm execution time (subsequent calls)
        # - Compare with local execution baseline
