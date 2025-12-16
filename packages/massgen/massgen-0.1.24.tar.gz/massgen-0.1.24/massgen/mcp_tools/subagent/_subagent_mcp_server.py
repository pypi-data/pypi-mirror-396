#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subagent MCP Server for MassGen

This MCP server provides tools for spawning and managing subagents,
enabling agents to delegate tasks to independent agent instances
with fresh context and isolated workspaces.

Tools provided:
- spawn_subagent: Spawn a single subagent for a specific task
- spawn_subagents_parallel: Spawn multiple subagents in parallel
- list_subagents: List all spawned subagents with their status
- get_subagent_result: Get the result from a completed subagent
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import fastmcp

from massgen.subagent.manager import SubagentManager

logger = logging.getLogger(__name__)

# Global storage for subagent manager (initialized per server instance)
_manager: Optional[SubagentManager] = None

# Server configuration
_workspace_path: Optional[Path] = None
_parent_agent_id: Optional[str] = None
_orchestrator_id: Optional[str] = None
_parent_backend_config: Dict[str, Any] = {}


def _get_manager() -> SubagentManager:
    """Get or create the SubagentManager instance."""
    global _manager
    if _manager is None:
        if _workspace_path is None:
            raise RuntimeError("Subagent server not properly configured: workspace_path is None")
        _manager = SubagentManager(
            parent_workspace=str(_workspace_path),
            parent_agent_id=_parent_agent_id or "unknown",
            orchestrator_id=_orchestrator_id or "unknown",
            parent_backend_config=_parent_backend_config,
        )
    return _manager


def _save_subagents_to_filesystem() -> None:
    """
    Save subagent registry to filesystem for visibility.

    Writes to subagents/_registry.json in the workspace directory.
    """
    if _workspace_path is None:
        return

    manager = _get_manager()
    subagents_dir = _workspace_path / "subagents"
    subagents_dir.mkdir(exist_ok=True)

    registry = {
        "parent_agent_id": _parent_agent_id,
        "orchestrator_id": _orchestrator_id,
        "subagents": manager.list_subagents(),
    }

    registry_file = subagents_dir / "_registry.json"
    registry_file.write_text(json.dumps(registry, indent=2))


async def create_server() -> fastmcp.FastMCP:
    """Factory function to create and configure the subagent MCP server."""
    global _workspace_path, _parent_agent_id, _orchestrator_id, _parent_backend_config

    parser = argparse.ArgumentParser(description="Subagent MCP Server")
    parser.add_argument(
        "--agent-id",
        type=str,
        required=True,
        help="ID of the parent agent using this subagent server",
    )
    parser.add_argument(
        "--orchestrator-id",
        type=str,
        required=True,
        help="ID of the orchestrator managing this agent",
    )
    parser.add_argument(
        "--workspace-path",
        type=str,
        required=True,
        help="Path to parent agent workspace for subagent workspaces",
    )
    parser.add_argument(
        "--backend-config",
        type=str,
        required=False,
        default="{}",
        help="JSON-encoded backend configuration to inherit",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent subagents (default: 3)",
    )
    parser.add_argument(
        "--default-timeout",
        type=int,
        default=300,
        help="Default timeout in seconds (default: 300)",
    )
    args = parser.parse_args()

    # Set global configuration
    _workspace_path = Path(args.workspace_path)
    _parent_agent_id = args.agent_id
    _orchestrator_id = args.orchestrator_id

    # Parse backend config
    try:
        _parent_backend_config = json.loads(args.backend_config)
    except json.JSONDecodeError:
        _parent_backend_config = {}

    # Create the FastMCP server
    mcp = fastmcp.FastMCP("Subagent Spawning")

    # Store configuration on server instance
    mcp.agent_id = args.agent_id
    mcp.orchestrator_id = args.orchestrator_id
    mcp.max_concurrent = args.max_concurrent
    mcp.default_timeout = args.default_timeout

    @mcp.tool()
    def spawn_subagent(
        task: str,
        subagent_id: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        context_files: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Spawn a subagent to work on a specific task with fresh context.

        Use subagents when you need:
        - Fresh context for a complex subtask (avoid context pollution)
        - Parallel execution of independent work streams
        - Specialized model for specific subtasks
        - Isolated workspace for experimental operations

        The subagent gets its own isolated workspace at subagents/{id}/workspace/.
        You can read files from the subagent's workspace but cannot modify them.

        Args:
            task: Clear description of what the subagent should accomplish.
                  Be specific about expected outputs and success criteria.
            subagent_id: Optional custom identifier (auto-generated if not provided).
                         Useful for tracking multiple related subagents.
            model: Override model for this subagent (default: inherit from parent).
            timeout_seconds: Maximum execution time (default: 300 seconds).
            context_files: List of files to copy into subagent workspace.
                          Paths are relative to your workspace.
            system_prompt: Optional custom system prompt for the subagent.

        Returns:
            Dictionary with subagent result:
            - success: bool - Whether execution succeeded
            - subagent_id: str - Subagent identifier
            - status: str - "completed", "timeout", or "error"
            - workspace: str - Path to subagent workspace (read-only to you)
            - answer: str - The subagent's answer (if completed)
            - files_created: list - Files created by the subagent
            - execution_time_seconds: float - How long it ran
            - error: str - Error message (if failed)

        Examples:
            # Simple task delegation
            spawn_subagent(
                task="Analyze the authentication code and identify security issues"
            )

            # With context files
            spawn_subagent(
                task="Write unit tests for the user module",
                context_files=["src/user.py", "src/models.py"]
            )

            # With custom ID for tracking
            spawn_subagent(
                task="Research OAuth2 best practices",
                subagent_id="research_oauth"
            )
        """
        try:
            manager = _get_manager()

            # Run the async spawn safely (handles both sync and nested async contexts)
            from massgen.utils import run_async_safely

            result = run_async_safely(
                manager.spawn_subagent(
                    task=task,
                    subagent_id=subagent_id,
                    model=model,
                    timeout_seconds=timeout_seconds or mcp.default_timeout,
                    context_files=context_files,
                    system_prompt=system_prompt,
                )
            )

            # Save registry to filesystem
            _save_subagents_to_filesystem()

            return {
                "success": result.success,
                "operation": "spawn_subagent",
                **result.to_dict(),
            }

        except Exception as e:
            logger.error(f"[SubagentMCP] Error spawning subagent: {e}")
            return {
                "success": False,
                "operation": "spawn_subagent",
                "error": str(e),
            }

    @mcp.tool()
    def spawn_subagents_parallel(
        tasks: List[Dict[str, Any]],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Spawn multiple subagents to work on tasks in parallel.

        This is more efficient than spawning subagents sequentially when
        you have multiple independent tasks that can run concurrently.

        Args:
            tasks: List of task configurations. Each task should have:
                   - task (required): Task description
                   - subagent_id (optional): Custom identifier
                   - model (optional): Model override
                   - context_files (optional): Files to copy
                   - system_prompt (optional): Custom system prompt
            timeout_seconds: Maximum execution time for ALL subagents.

        Returns:
            Dictionary with results:
            - success: bool - Whether all subagents succeeded
            - operation: str - "spawn_subagents_parallel"
            - results: list - Individual SubagentResult for each task
            - summary: dict - Count of completed, failed, timeout

        Example:
            spawn_subagents_parallel(
                tasks=[
                    {"task": "Write frontend components", "subagent_id": "frontend"},
                    {"task": "Write backend API", "subagent_id": "backend"},
                    {"task": "Write database migrations", "subagent_id": "database"}
                ],
                timeout_seconds=600
            )
        """
        try:
            manager = _get_manager()

            # Validate tasks
            for i, task_config in enumerate(tasks):
                if "task" not in task_config:
                    return {
                        "success": False,
                        "operation": "spawn_subagents_parallel",
                        "error": f"Task at index {i} missing required 'task' field",
                    }

            # Run the async spawn safely (handles both sync and nested async contexts)
            from massgen.utils import run_async_safely

            results = run_async_safely(
                manager.spawn_parallel(
                    tasks=tasks,
                    timeout_seconds=timeout_seconds or mcp.default_timeout,
                )
            )

            # Save registry to filesystem
            _save_subagents_to_filesystem()

            # Compute summary
            completed = sum(1 for r in results if r.status == "completed")
            failed = sum(1 for r in results if r.status == "error")
            timeout = sum(1 for r in results if r.status == "timeout")
            all_success = all(r.success for r in results)

            return {
                "success": all_success,
                "operation": "spawn_subagents_parallel",
                "results": [r.to_dict() for r in results],
                "summary": {
                    "total": len(results),
                    "completed": completed,
                    "failed": failed,
                    "timeout": timeout,
                },
            }

        except Exception as e:
            logger.error(f"[SubagentMCP] Error spawning parallel subagents: {e}")
            return {
                "success": False,
                "operation": "spawn_subagents_parallel",
                "error": str(e),
            }

    @mcp.tool()
    def list_subagents() -> Dict[str, Any]:
        """
        List all subagents spawned by this agent with their current status.

        Returns:
            Dictionary with:
            - success: bool
            - operation: str - "list_subagents"
            - subagents: list - List of subagent info with id, status, workspace, task
            - count: int - Total number of subagents

        Example:
            result = list_subagents()
            for sub in result['subagents']:
                print(f"{sub['subagent_id']}: {sub['status']}")
        """
        try:
            manager = _get_manager()
            subagents = manager.list_subagents()

            return {
                "success": True,
                "operation": "list_subagents",
                "subagents": subagents,
                "count": len(subagents),
            }

        except Exception as e:
            logger.error(f"[SubagentMCP] Error listing subagents: {e}")
            return {
                "success": False,
                "operation": "list_subagents",
                "error": str(e),
            }

    @mcp.tool()
    def get_subagent_result(subagent_id: str) -> Dict[str, Any]:
        """
        Get the result from a previously spawned subagent.

        Use this to retrieve results if you need to check on a subagent later.

        Args:
            subagent_id: ID of the subagent to get results for

        Returns:
            Dictionary with subagent result (same format as spawn_subagent)

        Example:
            result = get_subagent_result("research_oauth")
            if result['success']:
                print(result['answer'])
        """
        try:
            manager = _get_manager()
            result = manager.get_subagent_result(subagent_id)

            if result is None:
                return {
                    "success": False,
                    "operation": "get_subagent_result",
                    "error": f"Subagent not found: {subagent_id}",
                }

            return {
                "success": True,
                "operation": "get_subagent_result",
                **result.to_dict(),
            }

        except Exception as e:
            logger.error(f"[SubagentMCP] Error getting subagent result: {e}")
            return {
                "success": False,
                "operation": "get_subagent_result",
                "error": str(e),
            }

    return mcp


if __name__ == "__main__":
    import asyncio

    import fastmcp

    asyncio.run(fastmcp.run(create_server))
