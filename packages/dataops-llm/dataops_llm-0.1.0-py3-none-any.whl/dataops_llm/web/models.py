"""FastAPI request/response models."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """Request model for the /process endpoint.

    Attributes:
        instruction: Natural language instruction
        file_base64: Base64-encoded file content
        file_format: File format ("csv" or "excel")
        llm_config: Optional LLM configuration
        sandbox_config: Optional sandbox configuration
        dry_run: Whether to run in dry-run mode
        return_code: Whether to include generated code in response
    """

    instruction: str = Field(
        ...,
        min_length=1,
        description="Natural language instruction for data operation"
    )
    file_base64: str = Field(
        ...,
        description="Base64-encoded file content"
    )
    file_format: str = Field(
        default="csv",
        pattern="^(csv|excel)$",
        description="File format: 'csv' or 'excel'"
    )
    llm_config: Optional[dict[str, Any]] = Field(
        default=None,
        description="LLM configuration (api_key, model, etc.)"
    )
    sandbox_config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Sandbox configuration (timeout, memory_limit, etc.)"
    )
    dry_run: bool = Field(
        default=False,
        description="If true, generate plan/code but don't execute"
    )
    return_code: bool = Field(
        default=True,
        description="If true, include generated code in response"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "instruction": "Remove duplicates by email and normalize company names",
                "file_base64": "Y29tcGFueSxlbWFpbA==...",
                "file_format": "csv",
                "dry_run": False,
                "return_code": True
            }
        }


class ProcessResponse(BaseModel):
    """Response model for the /process endpoint.

    Attributes:
        success: Whether the operation succeeded
        result_base64: Base64-encoded result file (None if dry-run or error)
        report: Human-readable execution report
        generated_code: Generated Python code (if return_code=True)
        execution_time: Execution time in seconds
        warnings: List of warning messages
        metadata: Additional metadata
    """

    success: bool = Field(
        ...,
        description="Whether the operation succeeded"
    )
    result_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded result file"
    )
    report: str = Field(
        ...,
        description="Human-readable execution report"
    )
    generated_code: Optional[str] = Field(
        default=None,
        description="Generated Python code"
    )
    execution_time: float = Field(
        ...,
        ge=0.0,
        description="Execution time in seconds"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warning messages"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "success": True,
                "result_base64": "Y29tcGFueSxlbWFpbA==...",
                "report": "Operation completed successfully. Rows: 100 → 85",
                "generated_code": "import pandas as pd\n...",
                "execution_time": 2.5,
                "warnings": [],
                "metadata": {"plan_steps": 3}
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint.

    Attributes:
        status: Health status
        version: API version
        sandbox_available: Whether sandbox is functional
    """

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    sandbox_available: bool = Field(..., description="Sandbox availability")
