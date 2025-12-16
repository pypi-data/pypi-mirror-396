"""Intent data model for DataOps LLM Engine."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Intent(BaseModel):
    """Represents the extracted user intent from natural language instruction.

    This model captures what the user wants to do with their data,
    extracted by the LLM from the natural language instruction.

    Attributes:
        operation_type: Type of operation (e.g., "filter", "transform", "aggregate", "sort", "deduplicate")
        target_columns: List of column names that the operation targets
        conditions: Dictionary of conditions or parameters for the operation
        confidence: Confidence score (0.0-1.0) of the intent extraction
        raw_instruction: Original instruction provided by the user
        metadata: Additional metadata about the intent
    """

    operation_type: str = Field(
        ...,
        description="Type of data operation to perform"
    )
    target_columns: Optional[list[str]] = Field(
        default=None,
        description="Target columns for the operation"
    )
    conditions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Conditions or parameters for the operation"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of intent extraction"
    )
    raw_instruction: str = Field(
        ...,
        description="Original user instruction"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "operation_type": "filter",
                "target_columns": ["age", "email"],
                "conditions": {"age": {"gt": 25}, "email": {"not_null": True}},
                "confidence": 0.95,
                "raw_instruction": "Keep only people over 25 with valid emails",
                "metadata": {}
            }
        }
