"""
Context handling mixin for workflow executor.
"""

import re
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from jinja2 import Environment, BaseLoader
from jinja2.exceptions import TemplateSyntaxError, UndefinedError


if TYPE_CHECKING:
    from ..context import ExecutionContext
    from ..workflow_models import WorkflowStep


class ContextHandlerMixin:
    """Mixin for handling execution context and variable interpolation."""

    # Type hints for attributes that will be provided by WorkflowExecutor
    secrets_manager: Any

    def _get_cache_key(
        self, step: "WorkflowStep", ctx: "ExecutionContext"
    ) -> Optional[str]:
        """Generate cache key for a step if caching is enabled."""
        if not step.uses or "cache" not in (step.with_ or {}):
            return None

        # For now, simple key based on step and task
        task_id = ctx.task.get("id")
        task_updated = ctx.task.get("updated_at", "")
        return f"step:{step.uses}:task:{task_id}:updated:{task_updated}"

    def _build_evaluation_context(self, ctx: "ExecutionContext") -> Dict[str, Any]:
        """
        Build context dictionary for expression evaluation.

        Returns:
            Dictionary containing steps, env, task, and other variables
        """
        # Convert step outputs to nested structure
        steps = {}
        for step_id, output in ctx.outputs.items():
            steps[step_id] = {
                "outputs": output if isinstance(output, dict) else {"value": output}
            }

        return {
            "steps": steps,
            "env": ctx.env,
            "task": ctx.task,
        }

    def _interpolate_vars(self, value: Any, ctx: "ExecutionContext") -> Any:
        """Interpolate variables in strings using Jinja2 templating.

        Supports:
        - GitHub Actions style: ${{ task.field }}, ${{ steps.x.outputs.y }}
        - Jinja2 style: {{ task.field }}, {% if expr %}...{% endif %}
        - Filters: {{ task.field | lower }}, {{ task.field | upper }}
        - Fallback (OR) operator: ${{ expr1 || expr2 }}
        - Secrets: ${{ secrets.NAME }}
        """
        if isinstance(value, str):
            result = value

            # Step 1: Temporarily replace ${{ secrets.* }} with placeholders
            # so Jinja2 doesn't try to process them
            secrets_placeholders: Dict[str, str] = {}
            secret_pattern = r"\$\{\{\s*(secrets\.[^}]+)\s*\}\}"

            def save_secret(match: re.Match[str]) -> str:
                placeholder = f"__SECRET_PLACEHOLDER_{len(secrets_placeholders)}__"
                secrets_placeholders[placeholder] = match.group(0)
                return placeholder

            result = re.sub(secret_pattern, save_secret, result)

            # Step 2: Convert ${{ expr }} to Jinja2 {{ expr }} syntax
            def convert_github_style(match: re.Match[str]) -> str:
                expr = match.group(1).strip()
                if "||" in expr:
                    # Convert: a || b -> (a or b)
                    parts = [p.strip() for p in expr.split("||")]
                    jinja_expr = parts[0]
                    for part in parts[1:]:
                        jinja_expr = f"({jinja_expr} or {part})"
                    return "{{ " + jinja_expr + " }}"
                return "{{ " + expr + " }}"

            result = re.sub(r"\$\{\{\s*(.+?)\s*\}\}", convert_github_style, result)

            # Step 3: Build Jinja2 context
            jinja_context = self._build_jinja_context(ctx)

            # Step 4: Process with Jinja2 if there are any patterns
            if "{{" in result or "{%" in result:
                try:
                    env = Environment(
                        loader=BaseLoader(),
                        autoescape=False,
                    )
                    template = env.from_string(result)
                    result = template.render(**jinja_context)
                except (TemplateSyntaxError, UndefinedError) as e:
                    # Log warning but don't fail - return partially processed result
                    import logging

                    logging.getLogger(__name__).warning(
                        f"Template processing error: {e}"
                    )

            # Step 5: Restore secrets placeholders
            for placeholder, original in secrets_placeholders.items():
                result = result.replace(placeholder, original)

            # Step 6: Replace secrets via secrets_manager
            try:
                result = self.secrets_manager.interpolate_secrets(result)
            except ValueError as e:
                # Re-raise with better context
                raise ValueError(f"Secret interpolation failed: {e}") from e

            return result

        elif isinstance(value, dict):
            value_dict: dict[str, Any] = cast(dict[str, Any], value)
            return {k: self._interpolate_vars(v, ctx) for k, v in value_dict.items()}

        elif isinstance(value, list):
            value_list: list[Any] = cast(list[Any], value)  # type: ignore[redundant-cast]
            return [self._interpolate_vars(item, ctx) for item in value_list]

        return value

    def _build_jinja_context(self, ctx: "ExecutionContext") -> Dict[str, Any]:
        """Build context dictionary for Jinja2 template rendering.

        Returns:
            Dictionary with steps, task, env available for templates
        """
        # Build steps context with outputs accessible
        steps: Dict[str, Any] = {}
        for step_id, output in ctx.outputs.items():
            if isinstance(output, dict):
                steps[step_id] = {"outputs": output}
            else:
                steps[step_id] = {"outputs": {"value": output}}

        return {
            "steps": steps,
            "task": ctx.task,
            "env": ctx.env,
        }
