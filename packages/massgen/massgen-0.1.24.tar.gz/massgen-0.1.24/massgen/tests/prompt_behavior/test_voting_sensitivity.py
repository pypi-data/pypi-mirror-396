#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test voting sensitivity prompt behavior in isolation.

This script loads context scenarios and sends them to models with different
voting_sensitivity levels to verify that the prompts actually affect behavior.

Usage:
    # Test all scenarios with default model (gemini-2.5-flash)
    uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py

    # Test with specific model
    uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py --model gpt-4o

    # Test specific scenario
    uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py --scenario scenario_1_good_answer

    # Run multiple times for distribution analysis
    uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py --runs 10

    # Save results to file
    uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py --output results.json
"""

import argparse
import json
import os
import warnings
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from massgen.backend.gemini import GeminiBackend
from massgen.backend.response import ResponseBackend
from massgen.tests.simulation import simulate_agent_response, test_scenario_distribution

# Suppress Gemini SDK cleanup warnings (harmless, happen during garbage collection)
warnings.filterwarnings("ignore", message=".*'BaseApiClient' object has no attribute.*")
warnings.filterwarnings("ignore", message=".*'Client' object has no attribute.*")

# Load environment variables from .env file
load_dotenv(verbose=True)

console = Console()


def load_scenario(scenario_path: Path) -> Dict:
    """Load a context scenario from JSON file."""
    with open(scenario_path, "r") as f:
        return json.load(f)


def get_backend(model: str):
    """Create backend for the specified model.

    Args:
        model: Model name (e.g., "gemini-2.5-flash", "gpt-4o")

    Returns:
        Backend instance

    Raises:
        ValueError: If model type is not supported or API key is missing
    """
    if model.startswith("gemini"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Add to .env file or export it.")
        return GeminiBackend(api_key=api_key, model=model)
    elif model.startswith("gpt") or model.startswith("o"):  # o1, o3, etc.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Add to .env file or export it.")
        return ResponseBackend(model=model, api_key=api_key)
    else:
        raise ValueError(f"Unsupported model: {model}. Use gemini-* or gpt-* models.")


async def test_scenario_async(scenario: Dict, model: str = "gemini-2.5-flash") -> Dict:
    """Test a scenario with all three voting sensitivity levels (async version).

    Args:
        scenario: Scenario dict
        model: Model to use for testing

    Returns:
        Results dict with choices for each sensitivity level
    """
    # Create backend once for all sensitivity levels
    backend = get_backend(model)

    results = {
        "scenario_name": scenario["name"],
        "model": model,
        "sensitivity_results": {},
    }

    for sensitivity in ["lenient", "balanced", "strict"]:
        console.print(f"  Testing [yellow]{sensitivity}[/yellow] sensitivity...")

        # Use new simulation API
        try:
            console.print(f"    [cyan]Calling {model}...[/cyan]", end=" ")

            result = await simulate_agent_response(
                backend=backend,
                current_task=scenario["original_message"],
                existing_answers=scenario.get("existing_answers", {}),
                conversation_history=scenario.get("conversation_history", []),
                voting_sensitivity=sensitivity,
                answer_novelty_requirement=scenario.get("answer_novelty_requirement", "lenient"),
            )

            choice = result["tool_choice"]
            metadata = result["metadata"]
            response = result["response_text"]

            console.print(f"    [dim]System message: {metadata['system_message_length']} chars[/dim]")
            console.print(f"    [dim]User message: {metadata['user_message_length']} chars[/dim]")
            console.print(f"    [dim]Tools: {metadata['tools_count']} provided[/dim]")
            console.print(f"    [dim]DEBUG: response length={len(response)}, tool_calls={len(result['tool_calls'])}[/dim]")

            if choice:
                console.print(f"[green]✓ {choice}[/green]")
            else:
                console.print("[yellow]? unclear response[/yellow]")
                # Debug: show what we got
                console.print(f"    [dim]Response preview: '{response[:200]}'...[/dim]")
                console.print(f"    [dim]Tool calls: {result['tool_calls']}[/dim]")

        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)[:50]}...[/red]")
            choice = None
            response = str(e)
            metadata = {
                "system_message_length": 0,
                "user_message_length": 0,
                "tools_count": 0,
            }

        results["sensitivity_results"][sensitivity] = {
            "system_message_length": metadata["system_message_length"],
            "user_message_length": metadata["user_message_length"],
            "tools_count": metadata["tools_count"],
            "choice": choice,
            "expected": scenario["expected_behavior"].get(sensitivity, "unknown"),
            "response_preview": response[:200] if isinstance(response, str) else str(response)[:200],
        }

    return results


def test_scenario(scenario: Dict, model: str = "gemini-2.5-flash") -> Dict:
    """Test a scenario with all three voting sensitivity levels.

    Args:
        scenario: Scenario dict
        model: Model to use for testing

    Returns:
        Results dict with choices for each sensitivity level
    """
    import asyncio

    console.print(f"\n[bold cyan]Testing: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]{scenario['description']}[/dim]\n")

    return asyncio.run(test_scenario_async(scenario, model))


def test_scenario_with_distribution(scenario: Dict, model: str, n_runs: int = 1) -> Dict:
    """Test scenario with multiple runs and distribution analysis.

    Args:
        scenario: Scenario dict
        model: Model to use for testing
        n_runs: Number of runs per sensitivity level (default: 1 for single run)

    Returns:
        Results dict with choices and distribution stats for each sensitivity level
    """
    import asyncio

    if n_runs == 1:
        # Use simple single-run test
        return test_scenario(scenario, model)

    console.print(f"\n[bold cyan]Testing: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]{scenario['description']}[/dim]")
    console.print(f"[dim]Running {n_runs} times per sensitivity level[/dim]\n")

    backend = get_backend(model)

    results = {
        "scenario_name": scenario["name"],
        "model": model,
        "n_runs": n_runs,
        "sensitivity_results": {},
    }

    for sensitivity in ["lenient", "balanced", "strict"]:
        console.print(f"  Testing [yellow]{sensitivity}[/yellow] sensitivity ({n_runs} runs)...")

        try:
            dist_result = asyncio.run(
                test_scenario_distribution(
                    backend=backend,
                    scenario=scenario,
                    n_runs=n_runs,
                    voting_sensitivity=sensitivity,
                    answer_novelty_requirement=scenario.get("answer_novelty_requirement", "lenient"),
                )
            )

            # Display distribution results
            vote_pct = dist_result["vote_rate"] * 100
            new_answer_pct = dist_result["new_answer_rate"] * 100
            consistency = dist_result["consistency_score"] * 100

            console.print(f"    [cyan]Vote: {dist_result['vote_count']}/{n_runs} ({vote_pct:.1f}%)[/cyan]")
            console.print(f"    [cyan]New answer: {dist_result['new_answer_count']}/{n_runs} ({new_answer_pct:.1f}%)[/cyan]")
            if dist_result["unclear_count"] > 0:
                console.print(f"    [yellow]Unclear: {dist_result['unclear_count']}/{n_runs}[/yellow]")
            console.print(f"    [dim]Consistency: {consistency:.1f}%[/dim]")

            # Get first run's metadata for display
            first_run = dist_result["runs"][0]
            metadata = first_run["metadata"]

            results["sensitivity_results"][sensitivity] = {
                "vote_count": dist_result["vote_count"],
                "new_answer_count": dist_result["new_answer_count"],
                "unclear_count": dist_result["unclear_count"],
                "vote_rate": dist_result["vote_rate"],
                "new_answer_rate": dist_result["new_answer_rate"],
                "consistency_score": dist_result["consistency_score"],
                "expected": scenario["expected_behavior"].get(sensitivity, "unknown"),
                "system_message_length": metadata["system_message_length"],
                "user_message_length": metadata["user_message_length"],
                "tools_count": metadata["tools_count"],
            }

        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)[:50]}...[/red]")
            results["sensitivity_results"][sensitivity] = {
                "error": str(e),
                "expected": scenario["expected_behavior"].get(sensitivity, "unknown"),
            }

    return results


def main():
    parser = argparse.ArgumentParser(description="Test voting sensitivity prompt behavior")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Model to test with")
    parser.add_argument("--scenario", help="Specific scenario file to test")
    parser.add_argument("--output", help="Save results to JSON file")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs per scenario/sensitivity (default: 1)")
    args = parser.parse_args()

    # Find contexts directory
    contexts_dir = Path(__file__).parent / "contexts"

    if not contexts_dir.exists():
        console.print(f"[red]Error: Contexts directory not found at {contexts_dir}[/red]")
        return 1

    # Load scenarios
    if args.scenario:
        scenario_files = [contexts_dir / f"{args.scenario}.json"]
    else:
        scenario_files = sorted(contexts_dir.glob("scenario_*.json"))

    if not scenario_files:
        console.print(f"[red]No scenario files found in {contexts_dir}[/red]")
        return 1

    console.print("\n[bold]Testing Voting Sensitivity Prompts[/bold]")
    console.print(f"Model: {args.model}")
    console.print(f"Scenarios: {len(scenario_files)}")
    if args.runs > 1:
        console.print(f"Runs per sensitivity: {args.runs}")
    console.print()

    all_results = []

    for scenario_file in scenario_files:
        scenario = load_scenario(scenario_file)
        results = test_scenario_with_distribution(scenario, args.model, args.runs)
        all_results.append(results)

    # Display summary table
    console.print("\n[bold]Summary of Results[/bold]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Scenario", style="cyan", width=20)
    table.add_column("Lenient", justify="center", width=25)
    table.add_column("Balanced", justify="center", width=25)
    table.add_column("Strict", justify="center", width=25)

    for result in all_results:
        row = [result["scenario_name"]]
        is_multi_run = result.get("n_runs", 1) > 1

        for sensitivity in ["lenient", "balanced", "strict"]:
            sens_result = result["sensitivity_results"][sensitivity]
            expected = sens_result.get("expected", "unknown")

            if "error" in sens_result:
                cell = f"[dim]error[/dim]\n[dim](exp: {expected})[/dim]"
            elif is_multi_run:
                # Multi-run: show distribution
                vote_rate = sens_result.get("vote_rate", 0) * 100
                new_answer_rate = sens_result.get("new_answer_rate", 0) * 100
                consistency = sens_result.get("consistency_score", 0) * 100

                # Determine primary choice (majority)
                if vote_rate > new_answer_rate:
                    primary = "vote"
                elif new_answer_rate > vote_rate:
                    primary = "new_answer"
                else:
                    primary = "mixed"

                # Check if matches expected
                if "or" in expected:
                    match = primary in expected
                    color = "green" if match else "yellow"
                else:
                    match = primary in expected
                    color = "green" if match else "red"

                cell = f"[{color}]{primary} ({consistency:.0f}% consistent)[/{color}]\n"
                cell += f"[dim]V:{vote_rate:.0f}% NA:{new_answer_rate:.0f}%[/dim]\n"
                cell += f"[dim](exp: {expected})[/dim]"
            else:
                # Single run: show tool choice
                actual = sens_result.get("choice")
                if actual:
                    # Determine if it matches expectations
                    if "or" in expected:
                        match = actual in expected
                        color = "green" if match else "yellow"
                    else:
                        match = actual in expected
                        color = "green" if match else "red"

                    cell = f"[{color}]{actual}[/{color}]\n[dim](exp: {expected})[/dim]"
                else:
                    cell = f"[dim]unclear[/dim]\n[dim](exp: {expected})[/dim]"

            row.append(cell)
        table.add_row(*row)

    console.print(table)

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2)
        console.print(f"\n[green]Results saved to {output_path}[/green]")

    # Print statistics
    total_tests = len(all_results) * 3  # 3 sensitivity levels per scenario
    successful_tests = sum(1 for result in all_results for sensitivity in ["lenient", "balanced", "strict"] if result["sensitivity_results"][sensitivity]["choice"] is not None)

    console.print("\n[bold]Test Statistics:[/bold]")
    console.print(f"  Total tests run: {total_tests}")
    console.print(f"  Successful: {successful_tests}")
    console.print(f"  Failed/unclear: {total_tests - successful_tests}")

    if successful_tests == total_tests:
        console.print("\n[green]✓ All tests completed successfully![/green]")
    else:
        console.print(f"\n[yellow]⚠ {total_tests - successful_tests} test(s) had issues[/yellow]")

    console.print("\n[dim]Tip: Use --output results.json to save detailed results for analysis[/dim]\n")

    return 0


if __name__ == "__main__":
    exit(main())
