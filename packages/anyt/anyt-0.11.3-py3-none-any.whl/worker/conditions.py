"""
Conditional expression evaluator for workflow steps.

Supports GitHub Actions-style conditional expressions:
- Boolean literals: true, false
- Comparison operators: ==, !=, <, >, <=, >=
- Logical operators: &&, ||, !
- Variable interpolation: ${{ steps.test.outputs.passed }}
- String literals: 'text', "text"
"""

import re
from typing import Any, Dict, cast


class ExpressionError(Exception):
    """Error evaluating conditional expression."""

    pass


class ExpressionEvaluator:
    """Evaluates conditional expressions for workflow steps."""

    def __init__(self, context: Dict[str, Any]):
        """
        Initialize evaluator with execution context.

        Args:
            context: Execution context containing steps, outputs, etc.
        """
        self.context = context

    def evaluate(self, expression: str) -> bool:
        """
        Evaluate a conditional expression.

        Args:
            expression: Expression to evaluate (e.g., "${{ steps.test.outputs.passed == 'true' }}")

        Returns:
            Boolean result of the expression

        Raises:
            ExpressionError: If expression is invalid or evaluation fails
        """
        if not expression or not expression.strip():
            return True  # Empty expression is always true

        # Remove ${{ }} wrapper if present
        expr = expression.strip()
        if expr.startswith("${{") and expr.endswith("}}"):
            expr = expr[3:-2].strip()

        # Interpolate variables
        expr = self._interpolate_variables(expr)

        # Evaluate the expression
        try:
            return self._evaluate_expression(expr)
        except Exception as e:  # noqa: BLE001 - Intentionally broad: wrap any evaluation error
            # Wrap any evaluation error in ExpressionError with context
            raise ExpressionError(f"Failed to evaluate expression '{expression}': {e}")

    def _interpolate_variables(self, expr: str) -> str:
        """
        Replace variable references with their values.

        Supports:
        - steps.step_id.outputs.key
        - env.VAR_NAME
        - vars.key

        Args:
            expr: Expression with variable references

        Returns:
            Expression with variables replaced by values
        """

        def replace_var(match: re.Match[str]) -> str:
            var_path = match.group(1)
            parts = var_path.split(".")

            # Navigate context to find value
            current_value: Any = self.context
            for part in parts:
                if isinstance(current_value, dict):
                    current_dict: dict[str, Any] = cast(dict[str, Any], current_value)
                    current_value = current_dict.get(part)
                else:
                    raise ExpressionError(f"Cannot access '{part}' in non-dict value")

                if current_value is None:
                    # Variable not found - return empty string
                    return "''"

            # Convert value to string representation
            if isinstance(current_value, bool):
                return "true" if current_value else "false"
            elif isinstance(current_value, str):
                # Escape quotes in string
                escaped = current_value.replace("'", "\\'")
                return f"'{escaped}'"
            elif current_value is None:
                return "''"
            else:
                return str(current_value)

        # Match variable references (steps.id.outputs.key, env.VAR, etc.)
        pattern = r"([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)"
        return re.sub(pattern, replace_var, expr)

    def _evaluate_expression(self, expr: str) -> bool:
        """
        Evaluate a boolean expression.

        Supports:
        - Comparison: ==, !=, <, >, <=, >=
        - Logical: &&, ||, !
        - Literals: true, false, 'string', numbers

        Args:
            expr: Expression to evaluate

        Returns:
            Boolean result
        """
        expr = expr.strip()

        # Handle boolean literals
        if expr == "true":
            return True
        if expr == "false":
            return False

        # Handle logical NOT
        if expr.startswith("!"):
            return not self._evaluate_expression(expr[1:].strip())

        # Handle logical OR (lowest precedence)
        if "||" in expr:
            parts = self._split_by_operator(expr, "||")
            return any(self._evaluate_expression(part) for part in parts)

        # Handle logical AND
        if "&&" in expr:
            parts = self._split_by_operator(expr, "&&")
            return all(self._evaluate_expression(part) for part in parts)

        # Handle comparisons
        for op in ["==", "!=", "<=", ">=", "<", ">"]:
            if op in expr:
                parts = self._split_by_operator(expr, op, max_split=1)
                if len(parts) == 2:
                    left = self._parse_value(parts[0].strip())
                    right = self._parse_value(parts[1].strip())
                    return self._compare(left, right, op)

        # If no operators, try to parse as value
        value = self._parse_value(expr)
        if isinstance(value, bool):
            return value

        raise ExpressionError(f"Invalid expression: {expr}")

    def _split_by_operator(
        self, expr: str, operator: str, max_split: int = -1
    ) -> list[str]:
        """
        Split expression by operator, respecting string literals.

        Args:
            expr: Expression to split
            operator: Operator to split by
            max_split: Maximum number of splits (-1 for unlimited)

        Returns:
            List of expression parts
        """
        parts: list[str] = []
        current: list[str] = []
        in_string = False
        quote_char = None
        i = 0

        while i < len(expr):
            char = expr[i]

            # Handle string literals
            if char in ("'", '"'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
                current.append(char)
                i += 1
                continue

            # Check for operator (only outside strings)
            if not in_string and expr[i : i + len(operator)] == operator:
                if max_split == -1 or len(parts) < max_split:
                    parts.append("".join(current))
                    current = []
                    i += len(operator)
                    continue

            current.append(char)
            i += 1

        parts.append("".join(current))
        return parts

    def _parse_value(self, value: str) -> Any:
        """
        Parse a value from string representation.

        Args:
            value: String representation of value

        Returns:
            Parsed value (bool, int, float, or str)
        """
        value = value.strip()

        # Boolean
        if value == "true":
            return True
        if value == "false":
            return False

        # String literal
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            return value[1:-1]

        # Number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as-is if can't parse
        return value

    def _compare(self, left: Any, right: Any, operator: str) -> bool:
        """
        Compare two values using the given operator.

        Args:
            left: Left operand
            right: Right operand
            operator: Comparison operator (==, !=, <, >, <=, >=)

        Returns:
            Boolean result of comparison
        """
        if operator == "==":
            return bool(left == right)
        elif operator == "!=":
            return bool(left != right)
        elif operator == "<":
            return bool(left < right)
        elif operator == ">":
            return bool(left > right)
        elif operator == "<=":
            return bool(left <= right)
        elif operator == ">=":
            return bool(left >= right)
        else:
            raise ExpressionError(f"Unknown operator: {operator}")
