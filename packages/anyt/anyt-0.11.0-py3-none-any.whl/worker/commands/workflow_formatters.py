"""Formatters for workflow requirement check results."""

from __future__ import annotations

import platform

from cli.commands.console import console
from worker.services.workflow_requirements import WorkflowCheckResults


def display_check_results(results: WorkflowCheckResults) -> None:
    """Display workflow requirement check results in a user-friendly format.

    Args:
        results: The workflow check results to display
    """
    console.print()
    console.print(
        f"[cyan]Checking requirements for workflow:[/cyan] [bold]{results.workflow_name}[/bold]"
    )
    console.print()

    # Display each check result
    for req_name, check_result in results.results:
        if check_result.success:
            # Success: green checkmark
            console.print(f"[green]✓[/green] {req_name}: {check_result.message}")
        elif check_result.warning:
            # Warning: yellow warning symbol
            console.print(f"[yellow]⚠[/yellow]  {req_name}: {check_result.message}")
            if check_result.fix_instructions:
                console.print()
                _display_fix_instructions(check_result.fix_instructions)
                console.print()
        else:
            # Failure: red X
            console.print(f"[red]✗[/red] {req_name}: {check_result.message}")
            if check_result.fix_instructions:
                console.print()
                _display_fix_instructions(check_result.fix_instructions)
                console.print()

    # Display summary
    console.print()
    console.print("[bold]Summary:[/bold]")

    summary_parts = []
    if results.passed > 0:
        summary_parts.append(f"[green]{results.passed} passed[/green]")
    if results.failed > 0:
        summary_parts.append(f"[red]{results.failed} failed[/red]")
    if results.warnings > 0:
        summary_parts.append(f"[yellow]{results.warnings} warnings[/yellow]")

    console.print(", ".join(summary_parts))
    console.print()

    # Overall status
    if results.is_success():
        console.print(
            "[green]✓ All required checks passed! Workflow is ready to run.[/green]"
        )
    else:
        console.print(
            "[red]✗ Some required checks failed. Please fix the issues above before running the workflow.[/red]"
        )


def _display_fix_instructions(instructions: str) -> None:
    """Display fix instructions with OS-specific formatting.

    Args:
        instructions: The fix instructions to display
    """
    # Parse OS-specific instructions if they exist
    # Format: "OS_NAME: instruction\nOS_NAME: instruction"
    lines = instructions.strip().split("\n")
    os_specific_instructions: dict[str, list[str]] = {}
    general_instructions: list[str] = []

    current_os = platform.system().lower()
    os_map = {"darwin": "darwin", "linux": "linux", "windows": "windows"}
    normalized_os = os_map.get(current_os, current_os)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line starts with OS name
        if ":" in line and any(
            line.lower().startswith(os_name)
            for os_name in ["darwin", "linux", "windows", "macos"]
        ):
            parts = line.split(":", 1)
            os_name = parts[0].strip().lower()
            # Normalize "macos" to "darwin"
            if os_name == "macos":
                os_name = "darwin"
            instruction = parts[1].strip()
            if os_name not in os_specific_instructions:
                os_specific_instructions[os_name] = []
            os_specific_instructions[os_name].append(instruction)
        else:
            general_instructions.append(line)

    # Display relevant instructions
    console.print("  [yellow]Fix:[/yellow]")

    # Show general instructions first
    for instruction in general_instructions:
        console.print(f"    {instruction}")

    # Show OS-specific instructions
    if os_specific_instructions:
        # Prioritize current OS
        if normalized_os in os_specific_instructions:
            for instruction in os_specific_instructions[normalized_os]:
                console.print(f"    • {instruction}")
        else:
            # Show all OS-specific instructions if current OS not found
            for os_name, instructions_list in os_specific_instructions.items():
                os_display = os_name.capitalize()
                if os_name == "darwin":
                    os_display = "macOS"
                console.print(f"    [dim]{os_display}:[/dim]")
                for instruction in instructions_list:
                    console.print(f"      • {instruction}")


def format_check_results_json(results: WorkflowCheckResults) -> dict[str, object]:
    """Format workflow check results as JSON.

    Args:
        results: The workflow check results to format

    Returns:
        Dictionary suitable for JSON output
    """
    checks = []
    for req_name, check_result in results.results:
        check_dict = {
            "requirement": req_name,
            "success": check_result.success,
            "message": check_result.message,
            "warning": check_result.warning,
        }
        if check_result.fix_instructions:
            check_dict["fix_instructions"] = check_result.fix_instructions
        checks.append(check_dict)

    return {
        "success": results.is_success(),
        "data": {
            "workflow_name": results.workflow_name,
            "checks": checks,
            "summary": {
                "passed": results.passed,
                "failed": results.failed,
                "warnings": results.warnings,
                "total": results.passed + results.failed + results.warnings,
            },
        },
    }
