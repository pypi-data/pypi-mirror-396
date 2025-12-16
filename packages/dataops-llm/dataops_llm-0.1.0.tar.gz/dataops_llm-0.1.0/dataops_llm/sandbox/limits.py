"""Resource limits and monitoring for sandbox execution."""

import psutil
import pandas as pd

from dataops_llm.config import SandboxConfig
from dataops_llm.exceptions import DataFrameValidationError, MemoryLimitError


class ResourceMonitor:
    """Monitors and enforces resource limits during code execution.

    This class provides utilities to check memory usage, DataFrame sizes,
    and other resource constraints to prevent resource exhaustion.

    Attributes:
        config: Sandbox configuration with limit values
    """

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize the resource monitor.

        Args:
            config: Sandbox configuration. Uses default if not provided.
        """
        self.config = config or SandboxConfig()

    def check_memory_usage(self, raise_on_exceed: bool = True) -> float:
        """Check current process memory usage.

        Args:
            raise_on_exceed: Whether to raise exception if limit exceeded

        Returns:
            Current memory usage in MB

        Raises:
            MemoryLimitError: If memory exceeds limit and raise_on_exceed is True
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB

        if raise_on_exceed and memory_mb > self.config.memory_limit_mb:
            raise MemoryLimitError(
                f"Memory usage ({memory_mb:.1f}MB) exceeds limit "
                f"({self.config.memory_limit_mb}MB)"
            )

        return memory_mb

    def validate_dataframe_size(
        self,
        df: pd.DataFrame,
        raise_on_exceed: bool = True
    ) -> dict[str, any]:
        """Validate DataFrame size against configured limits.

        Args:
            df: DataFrame to validate
            raise_on_exceed: Whether to raise exception if limits exceeded

        Returns:
            Dictionary with size information

        Raises:
            DataFrameValidationError: If DataFrame exceeds size limits
        """
        rows, cols = df.shape

        # Check row limit
        if rows > self.config.max_dataframe_rows:
            message = (
                f"DataFrame has {rows} rows, exceeding limit of "
                f"{self.config.max_dataframe_rows} rows"
            )
            if raise_on_exceed:
                raise DataFrameValidationError(message)

        # Check column limit
        if cols > self.config.max_dataframe_cols:
            message = (
                f"DataFrame has {cols} columns, exceeding limit of "
                f"{self.config.max_dataframe_cols} columns"
            )
            if raise_on_exceed:
                raise DataFrameValidationError(message)

        # Calculate memory footprint
        memory_bytes = df.memory_usage(deep=True).sum()
        memory_mb = memory_bytes / (1024 * 1024)

        return {
            "rows": rows,
            "columns": cols,
            "memory_mb": memory_mb,
            "within_limits": (
                rows <= self.config.max_dataframe_rows and
                cols <= self.config.max_dataframe_cols
            )
        }

    def validate_output_size(
        self,
        size_bytes: int,
        raise_on_exceed: bool = True
    ) -> float:
        """Validate output file size.

        Args:
            size_bytes: Size in bytes
            raise_on_exceed: Whether to raise exception if limit exceeded

        Returns:
            Size in MB

        Raises:
            DataFrameValidationError: If size exceeds limit
        """
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > self.config.max_output_size_mb:
            message = (
                f"Output size ({size_mb:.1f}MB) exceeds limit of "
                f"{self.config.max_output_size_mb}MB"
            )
            if raise_on_exceed:
                raise DataFrameValidationError(message)

        return size_mb

    def get_system_resources(self) -> dict[str, any]:
        """Get current system resource usage.

        Returns:
            Dictionary with CPU, memory, and disk usage
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "disk_percent": psutil.disk_usage('/').percent,
        }

    def check_all_limits(self, df: pd.DataFrame) -> dict[str, any]:
        """Check all resource limits at once.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with all resource checks

        Raises:
            MemoryLimitError: If memory limit exceeded
            DataFrameValidationError: If DataFrame size limits exceeded
        """
        memory_mb = self.check_memory_usage(raise_on_exceed=True)
        df_info = self.validate_dataframe_size(df, raise_on_exceed=True)
        system_resources = self.get_system_resources()

        return {
            "process_memory_mb": memory_mb,
            "dataframe": df_info,
            "system": system_resources,
            "all_within_limits": True
        }
