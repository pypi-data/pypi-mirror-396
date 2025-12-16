"""Execution context management for sandbox."""

from typing import Any


class ExecutionContext:
    """Manages execution context for sandbox runtime.

    This class provides a structured way to pass additional context
    to the execution environment, such as user preferences, debug flags,
    or custom variables.

    Attributes:
        variables: Custom variables to inject into execution
        debug: Whether to enable debug mode
        strict_mode: Whether to enable strict validation
        metadata: Additional metadata
    """

    def __init__(
        self,
        variables: dict[str, Any] | None = None,
        debug: bool = False,
        strict_mode: bool = True,
        metadata: dict[str, Any] | None = None
    ):
        """Initialize execution context.

        Args:
            variables: Custom variables (currently unused for security)
            debug: Enable debug mode (adds verbose logging)
            strict_mode: Enable strict validation (recommended)
            metadata: Additional metadata to pass through
        """
        self.variables = variables or {}
        self.debug = debug
        self.strict_mode = strict_mode
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary.

        Returns:
            Dictionary representation of context
        """
        return {
            "variables": self.variables,
            "debug": self.debug,
            "strict_mode": self.strict_mode,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionContext":
        """Create context from dictionary.

        Args:
            data: Dictionary with context data

        Returns:
            ExecutionContext instance
        """
        return cls(
            variables=data.get("variables"),
            debug=data.get("debug", False),
            strict_mode=data.get("strict_mode", True),
            metadata=data.get("metadata")
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ExecutionContext(debug={self.debug}, "
            f"strict_mode={self.strict_mode}, "
            f"variables={len(self.variables)})"
        )
