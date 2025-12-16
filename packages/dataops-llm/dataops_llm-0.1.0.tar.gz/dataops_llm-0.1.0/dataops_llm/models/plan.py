"""Execution plan data models for DataOps LLM Engine."""

from typing import Any

from pydantic import BaseModel, Field


class ExecutionStep(BaseModel):
    """Represents a single step in the execution plan.

    Each step corresponds to a specific data operation that will be
    translated into pandas code.

    Attributes:
        step_id: Unique identifier for this step
        operation: Operation name (e.g., "filter_rows", "rename_column", "deduplicate")
        description: Human-readable description of what this step does
        parameters: Parameters needed to execute this operation
    """

    step_id: int = Field(
        ...,
        ge=0,
        description="Sequential step identifier"
    )
    operation: str = Field(
        ...,
        description="Operation to perform"
    )
    description: str = Field(
        ...,
        description="Human-readable step description"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation parameters"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "step_id": 1,
                "operation": "filter_rows",
                "description": "Filter rows where age > 25",
                "parameters": {"column": "age", "condition": "gt", "value": 25}
            }
        }


class ExecutionPlan(BaseModel):
    """Represents the complete execution plan for data operations.

    The execution plan is a sequence of steps that will be converted
    into Python code and executed.

    Attributes:
        steps: List of execution steps in sequential order
        estimated_complexity: Complexity estimate ("low", "medium", "high")
        requires_validation: Whether this plan needs additional validation
        metadata: Additional metadata about the plan
    """

    steps: list[ExecutionStep] = Field(
        ...,
        min_length=1,
        description="Ordered list of execution steps"
    )
    estimated_complexity: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Estimated complexity of the plan"
    )
    requires_validation: bool = Field(
        default=False,
        description="Whether plan needs extra validation"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "steps": [
                    {
                        "step_id": 0,
                        "operation": "filter_rows",
                        "description": "Filter rows where email is not null",
                        "parameters": {"column": "email", "condition": "not_null"}
                    },
                    {
                        "step_id": 1,
                        "operation": "normalize_text",
                        "description": "Normalize company names to lowercase",
                        "parameters": {"column": "company_name", "method": "lowercase"}
                    },
                    {
                        "step_id": 2,
                        "operation": "deduplicate",
                        "description": "Remove duplicates based on email",
                        "parameters": {"columns": ["email"]}
                    }
                ],
                "estimated_complexity": "medium",
                "requires_validation": False,
                "metadata": {}
            }
        }

    @property
    def step_count(self) -> int:
        """Return the number of steps in the plan."""
        return len(self.steps)

    def get_step(self, step_id: int) -> ExecutionStep | None:
        """Get a specific step by ID.

        Args:
            step_id: The step identifier

        Returns:
            The execution step if found, None otherwise
        """
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
