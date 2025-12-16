"""Result data model for DataOps LLM Engine."""

from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_serializer

from dataops_llm.models.plan import ExecutionPlan


class DataOpsResult(BaseModel):
    """Represents the result of a data operation.

    This is the primary output object returned to users after processing
    their data with natural language instructions.

    Attributes:
        success: Whether the operation completed successfully
        dataframe: The resulting DataFrame (None if dry-run or error)
        generated_code: Python code that was generated (if requested)
        execution_plan: The execution plan used (if requested)
        report: Human-readable report of what was done
        execution_time: Time taken to execute in seconds
        warnings: List of warning messages
        metadata: Additional metadata about the execution
    """

    model_config = {"arbitrary_types_allowed": True}

    success: bool = Field(
        ...,
        description="Whether the operation succeeded"
    )
    dataframe: Optional[pd.DataFrame] = Field(
        default=None,
        description="Resulting DataFrame"
    )
    generated_code: Optional[str] = Field(
        default=None,
        description="Generated Python code"
    )
    execution_plan: Optional[ExecutionPlan] = Field(
        default=None,
        description="Execution plan used"
    )
    report: str = Field(
        ...,
        description="Human-readable execution report"
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

    @field_serializer("dataframe")
    def serialize_dataframe(self, df: Optional[pd.DataFrame]) -> Optional[dict]:
        """Serialize DataFrame for JSON output.

        Args:
            df: The DataFrame to serialize

        Returns:
            Dictionary representation of DataFrame or None
        """
        if df is None:
            return None
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "head": df.head().to_dict()
        }

    def save(self, path: str | Path, format: Optional[str] = None, **kwargs) -> None:
        """Save the resulting DataFrame to a file.

        Args:
            path: Output file path
            format: File format ("csv" or "excel"). Auto-detected from path if not specified
            **kwargs: Additional arguments passed to pandas save function

        Raises:
            ValueError: If no DataFrame available or unsupported format
        """
        if self.dataframe is None:
            raise ValueError("No DataFrame available to save (operation may have failed or was dry-run)")

        path = Path(path)

        # Auto-detect format from file extension
        if format is None:
            suffix = path.suffix.lower()
            if suffix == ".csv":
                format = "csv"
            elif suffix in (".xlsx", ".xls"):
                format = "excel"
            else:
                raise ValueError(f"Cannot auto-detect format from extension: {suffix}")

        # Save based on format
        if format == "csv":
            self.dataframe.to_csv(path, index=False, **kwargs)
        elif format == "excel":
            self.dataframe.to_excel(path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'excel'")

    def to_dict(self, include_dataframe: bool = False) -> dict[str, Any]:
        """Convert result to dictionary.

        Args:
            include_dataframe: Whether to include full DataFrame data

        Returns:
            Dictionary representation of the result
        """
        result = {
            "success": self.success,
            "report": self.report,
            "execution_time": self.execution_time,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }

        if self.generated_code is not None:
            result["generated_code"] = self.generated_code

        if self.execution_plan is not None:
            result["execution_plan"] = self.execution_plan.model_dump()

        if include_dataframe and self.dataframe is not None:
            result["dataframe"] = {
                "shape": self.dataframe.shape,
                "columns": self.dataframe.columns.tolist(),
                "dtypes": self.dataframe.dtypes.to_dict(),
                "data": self.dataframe.to_dict(orient="records")
            }

        return result

    def __str__(self) -> str:
        """String representation of the result."""
        status = "SUCCESS" if self.success else "FAILED"
        lines = [
            f"DataOpsResult ({status})",
            f"Execution Time: {self.execution_time:.2f}s",
            f"Report: {self.report}",
        ]

        if self.dataframe is not None:
            lines.append(f"DataFrame Shape: {self.dataframe.shape}")

        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)
