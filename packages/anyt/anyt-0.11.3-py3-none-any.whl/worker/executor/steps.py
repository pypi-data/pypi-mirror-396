"""
Step execution mixin for workflow executor.
"""

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, cast

from rich.markup import escape

from cli.commands.console import console
from cli.utils.errors import is_debug_mode
from ..workflow_models import StepResult, StepStatus, WorkflowStep

if TYPE_CHECKING:
    from ..context import ExecutionContext


def _debug(message: str) -> None:
    """Print debug message if ANYT_DEBUG is enabled."""
    if is_debug_mode():
        console.print(f"  [dim]DEBUG: {message}[/dim]")


class StepExecutorMixin:
    """Mixin for executing workflow steps."""

    # Type hints for attributes that will be provided by WorkflowExecutor
    secrets_manager: Any
    action_registry: Any
    cache_manager: Any

    async def _execute_step(
        self, step: WorkflowStep, ctx: "ExecutionContext"
    ) -> StepResult:
        """Execute a single workflow step."""
        step_id = step.id or step.name.lower().replace(" ", "_")
        console.print(f"\n[cyan]▶[/cyan] {escape(step.name)}")

        result = StepResult(
            step_id=step_id,
            step_name=step.name,
            status=StepStatus.RUNNING,
            started_at=datetime.now(),
        )

        # Check conditional execution
        if step.if_:
            try:
                # Build context for expression evaluation
                eval_context = self._build_evaluation_context(ctx)  # type: ignore[attr-defined]
                from ..conditions import ExpressionEvaluator

                evaluator = ExpressionEvaluator(eval_context)
                should_run = evaluator.evaluate(step.if_)

                if not should_run:
                    console.print(
                        "  [dim yellow]⊘ Skipped (condition not met)[/dim yellow]"
                    )
                    result.status = StepStatus.SKIPPED
                    result.completed_at = datetime.now()
                    return result
            except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle condition evaluation failures to allow workflow to continue with appropriate error status
                console.print(
                    f"  [red]✗ Condition evaluation failed:[/red] {escape(str(e))}"
                )
                result.status = StepStatus.FAILURE
                result.error = f"Condition evaluation failed: {e}"
                result.completed_at = datetime.now()
                return result

        # Handle parallel execution
        if step.parallel is not None:
            return await self._execute_parallel_steps(step, step.parallel, ctx)

        try:
            # Check cache if applicable
            cache_key = self._get_cache_key(step, ctx)  # type: ignore[attr-defined]
            if cache_key:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    console.print("  [dim]✓ Using cached result[/dim]")
                    result.status = StepStatus.SUCCESS
                    result.output = cached_result
                    result.completed_at = datetime.now()
                    return result

            # Execute based on step type
            if step.uses:
                # Action-based step
                output = await self._execute_action(step, ctx)
            elif step.run:
                # Command-based step
                output = await self._execute_command(step, ctx)
            elif step.parallel:
                # Parallel steps - should never reach here as handled above
                raise ValueError(
                    f"Internal error: parallel step should have been handled: {step.name}"
                )
            else:
                raise ValueError(
                    f"Step must have either 'uses', 'run', or 'parallel': {step.name}"
                )

            result.status = StepStatus.SUCCESS
            result.output = output

            # Cache result if applicable
            if cache_key:
                await self.cache_manager.set(cache_key, output)

            # Check if action indicated it was skipped
            if isinstance(output, dict) and output.get("skipped"):
                reason = output.get("reason", "Action skipped")
                console.print(f"  [dim yellow]⊘ Skipped:[/dim yellow] {reason}")
            else:
                console.print("  [dim green]✓ Completed[/dim green]")

        except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle step execution failures to allow workflow to continue with appropriate error status
            result.status = StepStatus.FAILURE
            result.error = str(e)

            # Enhanced error logging with context
            error_details: list[str] = []
            error_details.append(f"[red]✗ Failed:[/red] {e}")

            # Add action/command context
            if step.uses:
                error_details.append(f"  [dim]Action: {step.uses}[/dim]")
            elif step.run:
                error_details.append(
                    f"  [dim]Command: {step.run[:100]}{'...' if len(step.run) > 100 else ''}[/dim]"
                )

            # Add step parameters if available (helps debug configuration issues)
            if step.with_:
                # Don't log sensitive data like full auth tokens, just indicate what params were used
                param_keys = list(step.with_.keys())
                error_details.append(
                    f"  [dim]Parameters: {', '.join(param_keys)}[/dim]"
                )

            # Print all error details
            console.print("\n".join(error_details))

        finally:
            result.completed_at = datetime.now()
            if result.started_at and result.completed_at:
                result.duration_seconds = (
                    result.completed_at - result.started_at
                ).total_seconds()

        return result

    async def _execute_parallel_steps(
        self,
        parent_step: WorkflowStep,
        parallel_steps: "list[WorkflowStep]",
        ctx: "ExecutionContext",
    ) -> StepResult:
        """
        Execute multiple steps in parallel.

        Args:
            parent_step: The parent step containing parallel configuration
            parallel_steps: List of steps to execute in parallel
            ctx: Execution context

        Returns:
            StepResult with aggregated outputs and status
        """
        step_id = parent_step.id or parent_step.name.lower().replace(" ", "_")
        parent_result = StepResult(
            step_id=step_id,
            step_name=parent_step.name,
            status=StepStatus.RUNNING,
            started_at=datetime.now(),
        )

        console.print(
            f"  [dim]Running {len(parallel_steps)} steps in parallel...[/dim]"
        )

        try:
            # Create tasks for parallel execution
            tasks: list[Any] = []
            for i, sub_step in enumerate(parallel_steps):
                # Ensure sub-step has an ID for tracking
                if not sub_step.id:
                    sub_step.id = f"{step_id}_parallel_{i}"
                tasks.append(self._execute_step(sub_step, ctx))

            # Execute all steps in parallel and gather results
            # Use return_exceptions=True to handle partial failures
            results: list[Any] = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            aggregated_outputs: dict[str, Any] = {}
            failed_steps: list[dict[str, Any]] = []
            successful_steps: list[str] = []
            skipped_steps: list[str] = []

            for i, result_or_exception in enumerate(results):
                sub_step = parallel_steps[i]
                sub_step_id = sub_step.id or f"{step_id}_parallel_{i}"

                if isinstance(result_or_exception, Exception):
                    # Handle exception
                    failed_steps.append(
                        {
                            "name": sub_step.name,
                            "error": str(result_or_exception),
                        }
                    )
                    console.print(
                        f"  [red]✗ {sub_step.name} failed:[/red] {result_or_exception}"
                    )
                elif isinstance(result_or_exception, StepResult):
                    step_result = result_or_exception
                    # Add to context outputs
                    if step_result.output:
                        ctx.outputs[sub_step_id] = step_result.output
                        aggregated_outputs[sub_step_id] = step_result.output

                    # Track status
                    if step_result.status == StepStatus.SUCCESS:
                        successful_steps.append(sub_step.name)
                    elif step_result.status == StepStatus.FAILURE:
                        failed_steps.append(
                            {
                                "name": sub_step.name,
                                "error": step_result.error or "Unknown error",
                            }
                        )
                    elif step_result.status == StepStatus.SKIPPED:
                        skipped_steps.append(sub_step.name)

            # Determine overall status
            if failed_steps and not parent_step.continue_on_error:
                parent_result.status = StepStatus.FAILURE
                parent_result.error = (
                    f"{len(failed_steps)} step(s) failed: "
                    + ", ".join(f["name"] for f in failed_steps)
                )
                console.print(
                    f"  [red]✗ {len(failed_steps)} parallel step(s) failed[/red]"
                )
            else:
                parent_result.status = StepStatus.SUCCESS
                console.print(
                    f"  [dim green]✓ {len(successful_steps)} step(s) succeeded"
                    + (
                        f", {len(failed_steps)} failed (ignored)"
                        if failed_steps
                        else ""
                    )
                    + (f", {len(skipped_steps)} skipped" if skipped_steps else "")
                    + "[/dim green]"
                )

            # Set aggregated output
            parent_result.output = {
                "parallel_results": aggregated_outputs,
                "summary": {
                    "total": len(parallel_steps),
                    "successful": len(successful_steps),
                    "failed": len(failed_steps),
                    "skipped": len(skipped_steps),
                },
                "failed_steps": failed_steps if failed_steps else None,
            }

        except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle parallel execution failures to allow workflow to continue with appropriate error status
            parent_result.status = StepStatus.FAILURE
            parent_result.error = f"Parallel execution failed: {e}"
            console.print(f"  [red]✗ Parallel execution failed:[/red] {escape(str(e))}")

        finally:
            parent_result.completed_at = datetime.now()
            if parent_result.started_at and parent_result.completed_at:
                parent_result.duration_seconds = (
                    parent_result.completed_at - parent_result.started_at
                ).total_seconds()

        return parent_result

    async def _execute_action(
        self, step: WorkflowStep, ctx: "ExecutionContext"
    ) -> Dict[str, Any]:
        """Execute an action-based step."""
        if not step.uses:
            raise ValueError("Step must have 'uses' field for action execution")

        _debug(f"Looking up action: {step.uses}")

        action = self.action_registry.get_action(step.uses)
        if not action:
            raise ValueError(f"Unknown action: {step.uses}")

        _debug(f"Found action: {type(action).__name__}")

        # Interpolate variables in step parameters
        raw_params = step.with_ or {}
        _debug(f"Raw params before interpolation: {raw_params}")

        params = self._interpolate_vars(raw_params, ctx)  # type: ignore[attr-defined]
        _debug(f"Params after interpolation: {params}")

        _debug("Calling action.execute()...")
        result = await action.execute(params, ctx)
        _debug(f"action.execute() returned: {result}")

        return cast(Dict[str, Any], result)

    async def _execute_command(
        self, step: WorkflowStep, ctx: "ExecutionContext"
    ) -> Dict[str, Any]:
        """Execute a command-based step."""
        command = self._interpolate_vars(step.run, ctx)  # type: ignore[attr-defined]

        # Prepare environment with secrets interpolation
        env = {**ctx.env, **(step.env or {})}
        # Interpolate secrets in environment variables
        env = self.secrets_manager.interpolate_dict(env)

        # Execute command
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
            env=env,
        )

        # Wait with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=step.timeout_minutes * 60
            )
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Step timed out after {step.timeout_minutes} minutes")

        # Check exit code
        if process.returncode != 0:
            raise RuntimeError(
                f"Command failed with exit code {process.returncode}\n{stderr.decode()}"
            )

        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "exit_code": process.returncode,
        }

    async def _execute_failure_handlers(
        self,
        failure_steps: "list[WorkflowStep]",
        ctx: "ExecutionContext",
        failed_step: StepResult,
    ) -> None:
        """Execute failure handler steps."""
        console.print("\n[yellow]Running failure handlers...[/yellow]")

        # Add failure info to context
        ctx.outputs["failure"] = {
            "step": failed_step.step_name,
            "message": failed_step.error,
        }

        for step in failure_steps:
            try:
                await self._execute_step(step, ctx)
            except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle failure handler execution errors to avoid masking original failure
                console.print(f"[red]Failure handler error:[/red] {escape(str(e))}")
