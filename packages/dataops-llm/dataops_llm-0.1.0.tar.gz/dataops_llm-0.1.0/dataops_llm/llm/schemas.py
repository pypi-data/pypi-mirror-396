"""LLM response schemas for structured outputs."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class IntentResponse(BaseModel):
    """Schema for LLM response when extracting intent from natural language.

    This schema enforces structured output from the LLM when interpreting
    user instructions.

    Attributes:
        operation_type: Type of operation identified
        target_columns: Columns that will be affected
        conditions: Conditions or parameters for the operation
        confidence: Confidence score of the interpretation
        reasoning: Brief explanation of the interpretation
    """

    operation_type: str = Field(
        ...,
        description="Type of data operation (filter, transform, aggregate, sort, deduplicate, join, etc.)"
    )
    target_columns: Optional[list[str]] = Field(
        default=None,
        description="List of column names affected by the operation"
    )
    conditions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Conditions or parameters for the operation"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the intent extraction (0.0-1.0)"
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of how the intent was interpreted"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "operation_type": "filter",
                "target_columns": ["age", "email"],
                "conditions": {
                    "age": {"operator": "gt", "value": 25},
                    "email": {"operator": "not_null"}
                },
                "confidence": 0.95,
                "reasoning": "User wants to filter rows based on age and email validity"
            }
        }


class PlanResponse(BaseModel):
    """Schema for LLM response when generating execution plan.

    This schema enforces structured output from the LLM when creating
    a step-by-step execution plan.

    Attributes:
        steps: List of execution steps
        complexity: Estimated complexity of the plan
        warnings: Any warnings about the plan
        reasoning: Brief explanation of the plan
    """

    steps: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Ordered list of execution steps"
    )
    complexity: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Estimated complexity (low, medium, high)"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about potential issues with the plan"
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the plan approach"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "steps": [
                    {
                        "step_id": 0,
                        "operation": "filter_rows",
                        "description": "Remove rows with null emails",
                        "parameters": {"column": "email", "condition": "not_null"}
                    },
                    {
                        "step_id": 1,
                        "operation": "normalize_text",
                        "description": "Convert company names to lowercase",
                        "parameters": {"column": "company_name", "method": "lowercase"}
                    },
                    {
                        "step_id": 2,
                        "operation": "deduplicate",
                        "description": "Remove duplicate rows based on email",
                        "parameters": {"columns": ["email"], "keep": "first"}
                    }
                ],
                "complexity": "medium",
                "warnings": [],
                "reasoning": "Plan performs data cleaning in logical order: filter nulls, normalize, deduplicate"
            }
        }


class CodeResponse(BaseModel):
    """Schema for LLM response when generating Python code.

    This schema enforces structured output from the LLM when translating
    an execution plan into Python code.

    Attributes:
        code: Generated Python code
        imports: List of required imports
        explanation: Explanation of what the code does
        warnings: Any warnings about the generated code
    """

    code: str = Field(
        ...,
        min_length=1,
        description="Generated Python code (pandas operations)"
    )
    imports: list[str] = Field(
        default_factory=list,
        description="List of required import statements"
    )
    explanation: str = Field(
        ...,
        description="Step-by-step explanation of the code"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about potential issues"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "code": "import pandas as pd\nimport numpy as np\n\n# Step 1: Filter rows where email is not null\ndf = df[df['email'].notna()]\n\n# Step 2: Normalize company names to lowercase\ndf['company_name'] = df['company_name'].str.lower()\n\n# Step 3: Remove duplicates based on email\ndf = df.drop_duplicates(subset=['email'], keep='first')\n\n# Return result\ndf",
                "imports": ["pandas", "numpy"],
                "explanation": "1. Filter rows to keep only those with valid emails\n2. Normalize company names by converting to lowercase\n3. Remove duplicate entries based on email column, keeping first occurrence",
                "warnings": []
            }
        }


class ValidationResult(BaseModel):
    """Schema for code validation results.

    This is used internally to communicate validation outcomes.

    Attributes:
        is_valid: Whether the code passed validation
        errors: List of validation errors
        warnings: List of validation warnings
        metadata: Additional validation metadata
    """

    is_valid: bool = Field(
        ...,
        description="Whether code passed all validation checks"
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of validation warnings"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional validation metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": ["Using str.lower() on potentially null values"],
                "metadata": {
                    "imports_checked": ["pandas", "numpy"],
                    "calls_checked": 5,
                    "attributes_checked": 3
                }
            }
        }
