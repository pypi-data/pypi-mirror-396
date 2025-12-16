#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent simulation and testing utilities for MassGen.

This module provides functions to simulate agent responses in specific contexts,
useful for testing voting sensitivity, answer novelty requirements, and other
hyperparameters without running full multi-agent coordination.
"""

import json
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..chat_agent import SingleAgent
from ..message_templates import MessageTemplates


async def simulate_agent_response(
    backend,  # LLMBackend
    current_task: str,
    existing_answers: Optional[Dict[str, str]] = None,
    conversation_history: Optional[List[Dict]] = None,
    voting_sensitivity: str = "lenient",
    answer_novelty_requirement: str = "lenient",
    base_system_message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Simulate an agent's response given a specific coordination context.

    This function builds the exact context an agent would see during MassGen
    coordination (using MessageTemplates) and returns the agent's tool choice
    and response. Useful for testing how voting_sensitivity and
    answer_novelty_requirement affect agent behavior.

    Args:
        backend: LLM backend to use (e.g., ResponseBackend, GeminiBackend)
        current_task: The user's question or task
        existing_answers: Dict of {agent_id: answer_text} from other agents
        conversation_history: Previous user/agent exchanges (for multi-turn testing)
        voting_sensitivity: "lenient", "balanced", or "strict"
        answer_novelty_requirement: "lenient", "balanced", or "strict"
        base_system_message: Optional custom system message to prepend

    Returns:
        Dict containing:
            - tool_choice: "vote", "new_answer", or None (if unclear)
            - response_text: Full text response from agent
            - tool_calls: List of tool calls made by agent
            - metadata: Context information (message lengths, parameters)

    Example:
        >>> from massgen import ResponseBackend
        >>> backend = ResponseBackend(model="gpt-4o")
        >>> result = await simulate_agent_response(
        ...     backend,
        ...     current_task="What is Python?",
        ...     existing_answers={"agent1": "Python is a programming language"},
        ...     voting_sensitivity="strict"
        ... )
        >>> print(result["tool_choice"])  # "vote" or "new_answer"
        >>> print(result["response_text"])  # Full agent response

    Note:
        This is an async function. Use `asyncio.run()` if calling from sync code:
        >>> import asyncio
        >>> result = asyncio.run(simulate_agent_response(...))
    """
    # Build context using MessageTemplates (same as orchestrator)
    templates = MessageTemplates(
        voting_sensitivity=voting_sensitivity,
        answer_novelty_requirement=answer_novelty_requirement,
    )

    valid_agent_ids = list((existing_answers or {}).keys())

    conversation = templates.build_conversation_with_context(
        current_task=current_task,
        conversation_history=conversation_history or [],
        agent_summaries=existing_answers or {},
        valid_agent_ids=valid_agent_ids,
        base_system_message=base_system_message,
    )

    # Extract components
    system_msg = conversation["system_message"]
    user_msg = conversation["user_message"]
    tools = conversation["tools"]

    # Build messages (include system message)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    # Create agent and call chat() - exactly like orchestrator does (line 1478)
    agent = SingleAgent(backend=backend, system_message=system_msg)
    response_text = ""
    tool_calls = []

    async for chunk in agent.chat(messages, tools, reset_chat=True):
        # Accumulate text content from chunks
        if hasattr(chunk, "content") and chunk.content:
            response_text += chunk.content
        # Capture tool calls
        if hasattr(chunk, "tool_calls") and chunk.tool_calls:
            tool_calls.extend(chunk.tool_calls)

    # Parse tool choice from response
    tool_choice = parse_tool_choice(response_text, tool_calls)

    return {
        "tool_choice": tool_choice,
        "response_text": response_text,
        "tool_calls": tool_calls,
        "metadata": {
            "system_message_length": len(system_msg),
            "user_message_length": len(user_msg),
            "tools_count": len(tools),
            "voting_sensitivity": voting_sensitivity,
            "answer_novelty_requirement": answer_novelty_requirement,
            "existing_answers_count": len(existing_answers or {}),
        },
    }


async def test_scenario_distribution(
    backend,  # LLMBackend
    scenario: Dict[str, Any],
    n_runs: int = 10,
    voting_sensitivity: str = "lenient",
    answer_novelty_requirement: str = "lenient",
) -> Dict[str, Any]:
    """
    Run a scenario multiple times and compute distribution statistics.

    Useful for measuring consistency and understanding how often agents
    choose to vote vs provide new answers under the same conditions.

    Args:
        backend: LLM backend to use
        scenario: Scenario dict with 'original_message' and 'existing_answers'
        n_runs: Number of times to run the scenario (default: 10)
        voting_sensitivity: "lenient", "balanced", or "strict"
        answer_novelty_requirement: "lenient", "balanced", or "strict"

    Returns:
        Dict containing:
            - vote_count: Number of times agent chose "vote"
            - new_answer_count: Number of times agent chose "new_answer"
            - unclear_count: Number of times tool choice was unclear
            - vote_rate: Percentage of clear responses that were votes
            - new_answer_rate: Percentage of clear responses that were new answers
            - consistency_score: 0-1 score measuring consistency (1 = always same choice)
            - runs: List of individual run results

    Example:
        >>> scenario = {
        ...     "original_message": "What is Python?",
        ...     "existing_answers": {
        ...         "agent1": "Python is a programming language"
        ...     }
        ... }
        >>> stats = await test_scenario_distribution(
        ...     backend, scenario, n_runs=20, voting_sensitivity="balanced"
        ... )
        >>> print(f"Voted {stats['vote_rate']:.1%} of the time")
        >>> print(f"Consistency: {stats['consistency_score']:.2f}")
    """
    results = []

    for i in range(n_runs):
        result = await simulate_agent_response(
            backend=backend,
            current_task=scenario["original_message"],
            existing_answers=scenario.get("existing_answers", {}),
            conversation_history=scenario.get("conversation_history", []),
            voting_sensitivity=voting_sensitivity,
            answer_novelty_requirement=answer_novelty_requirement,
        )
        results.append(result)

    # Compute statistics
    vote_count = sum(1 for r in results if r["tool_choice"] == "vote")
    new_answer_count = sum(1 for r in results if r["tool_choice"] == "new_answer")
    unclear_count = sum(1 for r in results if r["tool_choice"] is None)

    clear_count = vote_count + new_answer_count
    vote_rate = vote_count / clear_count if clear_count > 0 else 0
    new_answer_rate = new_answer_count / clear_count if clear_count > 0 else 0

    # Consistency score: 1 if all responses are the same, closer to 0 if mixed
    if clear_count > 0:
        max_count = max(vote_count, new_answer_count)
        consistency_score = max_count / clear_count
    else:
        consistency_score = 0

    return {
        "vote_count": vote_count,
        "new_answer_count": new_answer_count,
        "unclear_count": unclear_count,
        "vote_rate": vote_rate,
        "new_answer_rate": new_answer_rate,
        "consistency_score": consistency_score,
        "runs": results,
    }


def parse_tool_choice(response_text: str, tool_calls: List = None) -> Optional[str]:
    """
    Parse agent response to determine if it chose 'vote' or 'new_answer'.

    Checks both structured tool_calls and response text patterns to handle
    different backend formats.

    Args:
        response_text: Raw text response from agent
        tool_calls: List of structured tool calls (if available)

    Returns:
        "vote", "new_answer", or None if unclear

    Example:
        >>> parse_tool_choice("I will vote...", [{"name": "vote"}])
        'vote'
        >>> parse_tool_choice('{"tool_calls": [{"name": "new_answer"}]}', [])
        'new_answer'
    """
    # First check structured tool_calls
    if tool_calls:
        first_tool = tool_calls[0]
        if isinstance(first_tool, dict):
            tool_name = first_tool.get("name") or first_tool.get("function", {}).get("name")
            if tool_name == "vote":
                return "vote"
            elif tool_name == "new_answer":
                return "new_answer"

    # Check for JSON tool_calls format in response text
    try:
        if '"tool_calls":' in response_text:
            json_start = response_text.find('{"tool_calls":')
            if json_start != -1:
                json_data = json.loads(response_text[json_start:])
                tool_calls_from_json = json_data.get("tool_calls", [])
                if tool_calls_from_json:
                    first_tool = tool_calls_from_json[0]
                    if isinstance(first_tool, dict):
                        tool_name = first_tool.get("name") or first_tool.get("function", {}).get("name")
                        if tool_name == "vote":
                            return "vote"
                        elif tool_name == "new_answer":
                            return "new_answer"
    except (json.JSONDecodeError, KeyError, IndexError):
        pass

    # Look for tool use patterns in response text
    if '"name": "vote"' in response_text or '"name":"vote"' in response_text:
        return "vote"
    if '"name": "new_answer"' in response_text or '"name":"new_answer"' in response_text:
        return "new_answer"

    # Gemini structured output format
    if "vote" in response_text.lower() and "new_answer" not in response_text.lower():
        # Check if actually voting (not just mentioning it)
        if re.search(r"<tool.*?vote.*?>", response_text, re.IGNORECASE | re.DOTALL):
            return "vote"
        if re.search(r'"tool".*?:.*?"vote"', response_text, re.IGNORECASE):
            return "vote"
        if "i will vote" in response_text.lower() or "i'll vote" in response_text.lower():
            return "vote"

    if "new_answer" in response_text.lower() or "new answer" in response_text.lower():
        if re.search(r"<tool.*?new_answer.*?>", response_text, re.IGNORECASE | re.DOTALL):
            return "new_answer"
        if re.search(r'"tool".*?:.*?"new_answer"', response_text, re.IGNORECASE):
            return "new_answer"
        if "provide a new answer" in response_text.lower() or "i'll provide a new" in response_text.lower():
            return "new_answer"

    return None
