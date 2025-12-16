"""Utility for executing multiple tool calls in parallel.

This module provides functionality to execute multiple async tool calls concurrently,
collecting and yielding their streaming chunks in real-time.
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from massgen.backend.base import StreamChunk

logger = logging.getLogger(__name__)


async def execute_tools_parallel(
    calls: List[Dict[str, Any]],
    execute_fn: Callable[..., AsyncGenerator["StreamChunk", None]],
    execute_args: tuple = (),
    execute_kwargs: dict = None,
    max_concurrency: int = 10,
) -> AsyncGenerator["StreamChunk", None]:
    """Execute multiple tool calls in parallel, yielding chunks as they arrive.

    Args:
        calls: List of tool call dictionaries (each with call_id, name, arguments)
        execute_fn: Async generator function to execute each tool call
        execute_args: Additional positional arguments to pass to execute_fn
        execute_kwargs: Additional keyword arguments to pass to execute_fn
        max_concurrency: Maximum number of concurrent tool executions (default: 10)

    Yields:
        StreamChunk objects from all parallel tool executions, as they are produced

    Example:
        >>> async for chunk in execute_tools_parallel(
        ...     calls=mcp_calls,
        ...     execute_fn=self._execute_tool_with_logging,
        ...     execute_args=(config, updated_messages, processed_call_ids)
        ... ):
        ...     yield chunk
    """
    if not calls:
        return

    if execute_kwargs is None:
        execute_kwargs = {}

    # If only one call, execute directly without parallelization overhead
    if len(calls) == 1:
        async for chunk in execute_fn(calls[0], *execute_args, **execute_kwargs):
            yield chunk
        return

    # Limit concurrency to avoid overwhelming the system
    actual_concurrency = min(len(calls), max_concurrency)

    logger.info(f"Executing {len(calls)} tool calls with concurrency limit of {actual_concurrency}")

    # Use a semaphore to limit concurrent executions
    semaphore = asyncio.Semaphore(actual_concurrency)

    # Queue to collect chunks from all parallel executions
    chunk_queue: "asyncio.Queue[StreamChunk | None]" = asyncio.Queue()

    async def execute_with_semaphore(call: Dict[str, Any]) -> None:
        """Execute a single tool call with semaphore limiting."""
        async with semaphore:
            try:
                async for chunk in execute_fn(call, *execute_args, **execute_kwargs):
                    await chunk_queue.put(chunk)
            except Exception as e:
                # Log the error but don't crash the whole parallel execution
                tool_name = call.get("name", "unknown")
                logger.error(f"Unexpected error in parallel tool execution for {tool_name}: {e}")
                # The execute_fn should handle errors internally, but catch any unexpected ones

    async def producer() -> None:
        """Create tasks for all tool calls and wait for completion."""
        tasks = [asyncio.create_task(execute_with_semaphore(call)) for call in calls]
        await asyncio.gather(*tasks, return_exceptions=True)
        # Signal completion by putting None sentinel
        await chunk_queue.put(None)

    # Start the producer task
    producer_task = asyncio.create_task(producer())

    # Yield chunks as they arrive in the queue
    chunks_received = 0
    try:
        while True:
            chunk = await chunk_queue.get()
            if chunk is None:
                # All tasks completed
                break
            chunks_received += 1
            yield chunk
    finally:
        # Ensure producer task completes even if consumer stops early
        if not producer_task.done():
            producer_task.cancel()
            try:
                await producer_task
            except asyncio.CancelledError:
                pass

    logger.info(f"Parallel execution completed: {len(calls)} tools, {chunks_received} chunks yielded")


async def execute_tools_parallel_buffered(
    calls: List[Dict[str, Any]],
    execute_fn: Callable[..., AsyncGenerator["StreamChunk", None]],
    execute_args: tuple = (),
    execute_kwargs: dict = None,
    max_concurrency: int = 10,
) -> AsyncGenerator["StreamChunk", None]:
    """Execute multiple tool calls in parallel, buffering chunks by tool for ordered output.

    This variant buffers all chunks for each tool and yields them in the original
    call order, ensuring clean, non-interleaved output at the cost of some latency.

    Args:
        calls: List of tool call dictionaries (each with call_id, name, arguments)
        execute_fn: Async generator function to execute each tool call
        execute_args: Additional positional arguments to pass to execute_fn
        execute_kwargs: Additional keyword arguments to pass to execute_fn
        max_concurrency: Maximum number of concurrent tool executions (default: 10)

    Yields:
        StreamChunk objects from all tool executions, grouped by tool in call order

    Example:
        >>> async for chunk in execute_tools_parallel_buffered(
        ...     calls=mcp_calls,
        ...     execute_fn=self._execute_tool_with_logging,
        ...     execute_args=(config, updated_messages, processed_call_ids)
        ... ):
        ...     yield chunk
    """
    if not calls:
        return

    if execute_kwargs is None:
        execute_kwargs = {}

    # If only one call, execute directly without parallelization overhead
    if len(calls) == 1:
        async for chunk in execute_fn(calls[0], *execute_args, **execute_kwargs):
            yield chunk
        return

    # Limit concurrency
    actual_concurrency = min(len(calls), max_concurrency)
    logger.info(f"Executing {len(calls)} tool calls (buffered mode) with concurrency limit of {actual_concurrency}")

    # Use a semaphore to limit concurrent executions
    semaphore = asyncio.Semaphore(actual_concurrency)

    # Store chunks for each call indexed by their position
    chunks_by_call: "Dict[int, List[StreamChunk]]" = {i: [] for i in range(len(calls))}

    async def execute_and_collect(call_index: int, call: Dict[str, Any]) -> None:
        """Execute a tool call and collect all its chunks."""
        async with semaphore:
            try:
                async for chunk in execute_fn(call, *execute_args, **execute_kwargs):
                    chunks_by_call[call_index].append(chunk)
            except Exception as e:
                tool_name = call.get("name", "unknown")
                logger.error(f"Unexpected error in buffered parallel tool execution for {tool_name}: {e}")

    # Execute all calls in parallel
    tasks = [
        asyncio.create_task(execute_and_collect(i, call))
        for i, call in enumerate(calls)
    ]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Yield chunks in original call order
    total_chunks = 0
    for i in range(len(calls)):
        for chunk in chunks_by_call[i]:
            total_chunks += 1
            yield chunk

    logger.info(f"Buffered parallel execution completed: {len(calls)} tools, {total_chunks} chunks yielded")
