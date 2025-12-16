"""DataOps LLM Engine - LLM-powered data operations for Excel/CSV files.

This package provides a simple SDK for performing data operations using
natural language instructions. It uses LLMs to generate and execute safe
Python code for data manipulation.

Basic Usage:
    >>> from dataops_llm import process
    >>> result = process(
    ...     file_path="data.csv",
    ...     instruction="Remove duplicates and normalize text"
    ... )
    >>> if result.success:
    ...     result.save("output.csv")
    ...     print(result.report)
"""

from dataops_llm.api import process, execute
from dataops_llm.config import LLMConfig, SandboxConfig, AppConfig
from dataops_llm.exceptions import (
    DataOpsError,
    LLMError,
    ValidationError,
    UnsafeOperationError,
    SandboxError,
    ExecutionTimeoutError,
    MemoryLimitError,
    FileLoadError,
    CodeGenerationError,
    IntentExtractionError,
    PlanGenerationError,
    DataFrameValidationError,
    ConfigurationError,
)
from dataops_llm.models.result import DataOpsResult

__version__ = "0.1.0"
__author__ = "Islam Abd-Elhady"
__license__ = "MIT"

__all__ = [
    # Main API
    "process",
    "execute",
    # Configuration
    "LLMConfig",
    "SandboxConfig",
    "AppConfig",
    # Models
    "DataOpsResult",
    # Exceptions
    "DataOpsError",
    "LLMError",
    "ValidationError",
    "UnsafeOperationError",
    "SandboxError",
    "ExecutionTimeoutError",
    "MemoryLimitError",
    "FileLoadError",
    "CodeGenerationError",
    "IntentExtractionError",
    "PlanGenerationError",
    "DataFrameValidationError",
    "ConfigurationError",
    # Metadata
    "__version__",
]