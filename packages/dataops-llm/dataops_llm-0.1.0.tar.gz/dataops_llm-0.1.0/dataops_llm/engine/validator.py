"""Code validation module with AST-based security checks.

This module provides multi-layered validation to prevent execution of
dangerous or malicious code. It uses Abstract Syntax Tree (AST) inspection
to analyze code structure before execution.
"""

import ast
import re
from typing import Any

from dataops_llm.config import SandboxConfig
from dataops_llm.exceptions import UnsafeOperationError, ValidationError
from dataops_llm.llm.schemas import ValidationResult


class CodeValidator:
    """Validates generated Python code for security and correctness.

    This validator implements multiple layers of security checks:
    1. Import whitelisting
    2. Function call blacklisting
    3. Attribute access control
    4. DataFrame variable verification
    5. Syntax validation

    Attributes:
        config: Sandbox configuration with security rules
    """

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize the validator.

        Args:
            config: Sandbox configuration. Uses default if not provided.
        """
        self.config = config or SandboxConfig()

    def validate(self, code: str) -> ValidationResult:
        """Validate code against all security rules.

        Args:
            code: Python code to validate

        Returns:
            ValidationResult with validation outcome

        Raises:
            ValidationError: If code is fundamentally invalid
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {}

        # Layer 1: Syntax validation
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error: {e}"],
                warnings=[],
                metadata={}
            )

        # Layer 2: Import validation
        import_errors = self._check_imports(tree)
        errors.extend(import_errors)
        metadata["imports_checked"] = len(list(self._get_all_imports(tree)))

        # Layer 3: Forbidden call validation
        call_errors = self._check_forbidden_calls(tree)
        errors.extend(call_errors)
        metadata["calls_checked"] = len(list(self._get_all_calls(tree)))

        # Layer 4: Dangerous attribute access
        attr_errors = self._check_dangerous_attributes(tree)
        errors.extend(attr_errors)
        metadata["attributes_checked"] = len(list(self._get_all_attributes(tree)))

        # Layer 5: DataFrame variable validation
        df_warnings = self._check_dataframe_usage(tree)
        warnings.extend(df_warnings)

        # Layer 6: Pattern-based checks (regex)
        pattern_errors = self._check_dangerous_patterns(code)
        errors.extend(pattern_errors)

        # Layer 7: Check for infinite loops or suspicious constructs
        loop_warnings = self._check_loops(tree)
        warnings.extend(loop_warnings)

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )

    def _get_all_imports(self, tree: ast.AST) -> list[tuple[str, str]]:
        """Extract all import statements from AST.

        Args:
            tree: AST tree

        Yields:
            Tuples of (module_name, alias)
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield (alias.name, alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    yield (f"{module}.{alias.name}", alias.asname or alias.name)

    def _check_imports(self, tree: ast.AST) -> list[str]:
        """Check that all imports are whitelisted.

        Args:
            tree: AST tree

        Returns:
            List of error messages
        """
        errors = []
        allowed = self.config.allowed_imports

        for module_name, alias in self._get_all_imports(tree):
            # Check if the base module is allowed
            base_module = module_name.split(".")[0]
            if base_module not in allowed and module_name not in allowed:
                errors.append(
                    f"Forbidden import: '{module_name}'. "
                    f"Only {', '.join(allowed)} are allowed."
                )

        return errors

    def _get_all_calls(self, tree: ast.AST) -> list[str]:
        """Extract all function/method calls from AST.

        Args:
            tree: AST tree

        Yields:
            Function/method names
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    yield node.func.id
                elif isinstance(node.func, ast.Attribute):
                    yield node.func.attr

    def _check_forbidden_calls(self, tree: ast.AST) -> list[str]:
        """Check for forbidden function calls.

        Args:
            tree: AST tree

        Returns:
            List of error messages
        """
        errors = []
        forbidden = self.config.forbidden_calls

        for call_name in self._get_all_calls(tree):
            if call_name in forbidden:
                errors.append(
                    f"Forbidden function call: '{call_name}()'. "
                    f"This operation is not allowed for security reasons."
                )

        return errors

    def _get_all_attributes(self, tree: ast.AST) -> list[str]:
        """Extract all attribute accesses from AST.

        Args:
            tree: AST tree

        Yields:
            Attribute names
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                yield node.attr

    def _check_dangerous_attributes(self, tree: ast.AST) -> list[str]:
        """Check for dangerous attribute access (e.g., __class__, __globals__).

        Args:
            tree: AST tree

        Returns:
            List of error messages
        """
        errors = []
        forbidden = self.config.forbidden_attributes

        for attr_name in self._get_all_attributes(tree):
            if attr_name in forbidden or attr_name.startswith("__"):
                errors.append(
                    f"Forbidden attribute access: '{attr_name}'. "
                    f"Dunder attributes are not allowed for security reasons."
                )

        return errors

    def _check_dataframe_usage(self, tree: ast.AST) -> list[str]:
        """Check that DataFrame variable 'df' is used correctly.

        Args:
            tree: AST tree

        Returns:
            List of warning messages
        """
        warnings = []

        # Check if 'df' is assigned to
        has_df_assignment = False
        has_df_usage = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "df":
                has_df_usage = True
                if isinstance(node.ctx, ast.Store):
                    has_df_assignment = True

        if not has_df_usage:
            warnings.append(
                "DataFrame variable 'df' is not used in the code. "
                "The code may not operate on the input data."
            )

        if not has_df_assignment:
            warnings.append(
                "DataFrame variable 'df' is never reassigned. "
                "The code may not modify the data."
            )

        return warnings

    def _check_dangerous_patterns(self, code: str) -> list[str]:
        """Check for dangerous patterns using regex.

        This is an additional layer of defense against attacks that
        might bypass AST inspection.

        Args:
            code: Python code string

        Returns:
            List of error messages
        """
        errors = []

        # Pattern 1: Triple-quoted strings with suspicious content
        if re.search(r'""".*?(exec|eval|__import__).*?"""', code, re.DOTALL):
            errors.append("Suspicious content in multi-line string detected")

        # Pattern 2: Hex or base64 encoded strings (possible obfuscation)
        if re.search(r'\\x[0-9a-fA-F]{2}', code):
            errors.append("Hex-encoded strings detected - possible code obfuscation")

        # Pattern 3: fromkeys or other dict tricks to bypass checks
        if re.search(r'\.fromkeys\s*\(.*?__', code):
            errors.append("Suspicious dictionary manipulation detected")

        # Pattern 4: chr() or ord() which could be used for obfuscation
        if re.search(r'\bchr\s*\(|\bord\s*\(', code):
            errors.append("Character encoding/decoding detected - possible obfuscation")

        return errors

    def _check_loops(self, tree: ast.AST) -> list[str]:
        """Check for potentially dangerous loop constructs.

        Args:
            tree: AST tree

        Returns:
            List of warning messages
        """
        warnings = []

        for node in ast.walk(tree):
            # Check for while True loops (potential infinite loop)
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    warnings.append(
                        "Infinite 'while True' loop detected. "
                        "This may cause timeout issues."
                    )

            # Warn about nested loops (performance concern)
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        warnings.append(
                            "Nested loops detected. Consider using vectorized "
                            "pandas operations for better performance."
                        )
                        break  # Only warn once per outer loop

        return warnings

    def validate_and_raise(self, code: str) -> None:
        """Validate code and raise exception if invalid.

        Args:
            code: Python code to validate

        Raises:
            UnsafeOperationError: If dangerous operations detected
            ValidationError: If code is invalid
        """
        result = self.validate(code)

        if not result.is_valid:
            # Check if errors contain security violations
            has_security_error = any(
                keyword in error.lower()
                for error in result.errors
                for keyword in ["forbidden", "dangerous", "security"]
            )

            if has_security_error:
                raise UnsafeOperationError(
                    f"Code contains unsafe operations:\n" + "\n".join(result.errors)
                )
            else:
                raise ValidationError(
                    f"Code validation failed:\n" + "\n".join(result.errors)
                )
