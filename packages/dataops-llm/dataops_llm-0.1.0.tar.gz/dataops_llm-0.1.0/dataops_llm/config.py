"""Configuration management for DataOps LLM Engine."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """Configuration for LLM client (LiteLLM).

    Attributes:
        api_key: API key for the LLM provider
        model: Model name (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in LLM response
        timeout: Request timeout in seconds
        base_url: Optional custom API base URL
    """

    model_config = SettingsConfigDict(
        env_prefix="LITELLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    api_key: str = Field(
        ...,
        description="LLM provider API key"
    )
    model: str = Field(
        default="gpt-4",
        description="LLM model name"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for LLM"
    )
    max_tokens: int = Field(
        default=2000,
        gt=0,
        description="Maximum tokens in response"
    )
    timeout: int = Field(
        default=60,
        gt=0,
        description="Request timeout in seconds"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom API base URL"
    )


class SandboxConfig(BaseSettings):
    """Configuration for sandbox execution environment.

    Attributes:
        timeout: Maximum execution time in seconds
        memory_limit_mb: Maximum memory usage in megabytes
        max_dataframe_rows: Maximum allowed DataFrame rows
        max_dataframe_cols: Maximum allowed DataFrame columns
        max_output_size_mb: Maximum output file size in megabytes
        allowed_imports: Tuple of allowed Python modules for code execution
    """

    model_config = SettingsConfigDict(
        env_prefix="SANDBOX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    timeout: int = Field(
        default=60,
        gt=0,
        le=600,
        description="Maximum execution time in seconds"
    )
    memory_limit_mb: int = Field(
        default=512,
        gt=0,
        le=4096,
        description="Maximum memory usage in MB"
    )
    max_dataframe_rows: int = Field(
        default=1_000_000,
        gt=0,
        description="Maximum DataFrame rows"
    )
    max_dataframe_cols: int = Field(
        default=1_000,
        gt=0,
        description="Maximum DataFrame columns"
    )
    max_output_size_mb: int = Field(
        default=100,
        gt=0,
        description="Maximum output file size in MB"
    )

    # Immutable security settings (not configurable via env)
    allowed_imports: tuple[str, ...] = (
        "pandas",
        "pd",
        "numpy",
        "np",
        "datetime",
        "date",
        "time",
        "timedelta",
        "re",
        "math",
    )

    forbidden_calls: tuple[str, ...] = (
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "read",
        "write",
        "system",
        "popen",
        "subprocess",
        "requests",
        "urllib",
        "socket",
        "pickle",
        "shelve",
        "input",
        "raw_input",
    )

    forbidden_attributes: tuple[str, ...] = (
        "__class__",
        "__globals__",
        "__code__",
        "__dict__",
        "__builtins__",
        "__import__",
        "__loader__",
        "__spec__",
    )


class AppConfig(BaseSettings):
    """Global application configuration.

    Attributes:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_dry_run_by_default: Whether to enable dry-run mode by default
        enable_code_caching: Whether to cache generated code for identical requests
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    enable_dry_run_by_default: bool = Field(
        default=False,
        description="Enable dry-run mode by default"
    )
    enable_code_caching: bool = Field(
        default=False,
        description="Enable code caching"
    )
