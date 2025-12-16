"""Custom exceptions for DataOps LLM Engine."""


class DataOpsError(Exception):
    """Base exception for all DataOps LLM Engine errors."""

    pass


class LLMError(DataOpsError):
    """Raised when LLM client encounters an error.

    This includes:
    - API connection errors
    - Authentication failures
    - Rate limiting
    - Malformed responses
    - Timeout errors
    """

    pass


class ValidationError(DataOpsError):
    """Raised when code validation fails.

    This includes:
    - Forbidden imports detected
    - Forbidden function calls detected
    - Dangerous attribute access
    - Malformed code structure
    """

    pass


class UnsafeOperationError(ValidationError):
    """Raised when unsafe code operation is detected.

    This is a specialized validation error for operations
    that pose security risks.
    """

    pass


class SandboxError(DataOpsError):
    """Raised when sandbox execution encounters an error.

    This includes:
    - Execution timeout
    - Memory limit exceeded
    - Process crashed
    - Failed to serialize/deserialize data
    """

    pass


class ExecutionTimeoutError(SandboxError):
    """Raised when code execution exceeds time limit."""

    pass


class MemoryLimitError(SandboxError):
    """Raised when code execution exceeds memory limit."""

    pass


class FileLoadError(DataOpsError):
    """Raised when file loading fails.

    This includes:
    - File not found
    - Unsupported file format
    - Corrupted file
    - Encoding errors
    """

    pass


class CodeGenerationError(DataOpsError):
    """Raised when LLM fails to generate valid code.

    This includes:
    - Syntactically invalid code
    - Code that doesn't match execution plan
    - Failed to parse LLM response
    """

    pass


class IntentExtractionError(DataOpsError):
    """Raised when LLM fails to extract intent from instruction.

    This includes:
    - Ambiguous instructions
    - Unsupported operations
    - Failed to parse intent
    """

    pass


class PlanGenerationError(DataOpsError):
    """Raised when LLM fails to generate execution plan.

    This includes:
    - Invalid plan structure
    - Conflicting steps
    - Unsupported operations in plan
    """

    pass


class DataFrameValidationError(DataOpsError):
    """Raised when DataFrame validation fails.

    This includes:
    - DataFrame too large (rows/columns exceed limits)
    - Empty DataFrame
    - Invalid schema
    """

    pass


class ConfigurationError(DataOpsError):
    """Raised when configuration is invalid or missing.

    This includes:
    - Missing required environment variables
    - Invalid configuration values
    - Incompatible settings
    """

    pass
