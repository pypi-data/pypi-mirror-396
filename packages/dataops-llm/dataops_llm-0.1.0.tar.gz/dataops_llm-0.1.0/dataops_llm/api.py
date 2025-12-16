"""Main SDK API - primary entry point for users."""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from dataops_llm.config import LLMConfig, SandboxConfig
from dataops_llm.engine.executor import PipelineExecutor
from dataops_llm.models.result import DataOpsResult
from dataops_llm.utils.file_loader import FileLoader


def process(
    file_path: Union[str, Path, pd.DataFrame],
    instruction: str,
    llm_config: Optional[dict] = None,
    sandbox_config: Optional[dict] = None,
    dry_run: bool = False,
    return_code: bool = False
) -> DataOpsResult:
    """Process data with natural language instructions.

    This is the main entry point for the DataOps LLM Engine. It takes a file
    or DataFrame and a natural language instruction, then uses an LLM to
    generate and execute safe Python code to perform the requested operation.

    Args:
        file_path: Path to CSV/Excel file, or a pandas DataFrame
        instruction: Natural language instruction describing the operation
        llm_config: Optional LLM configuration dictionary with keys:
            - api_key: LLM provider API key
            - model: Model name (default: "gpt-4")
            - temperature: Sampling temperature (default: 0.1)
            - max_tokens: Maximum tokens in response (default: 2000)
        sandbox_config: Optional sandbox configuration dictionary with keys:
            - timeout: Maximum execution time in seconds (default: 60)
            - memory_limit_mb: Maximum memory in MB (default: 512)
        dry_run: If True, generate plan and code but don't execute
        return_code: If True, include generated code in result

    Returns:
        DataOpsResult object containing:
            - success: Whether the operation succeeded
            - dataframe: Resulting DataFrame (None if dry-run or error)
            - generated_code: Python code that was generated (if return_code=True)
            - execution_plan: Execution plan used (if return_code=True)
            - report: Human-readable execution report
            - execution_time: Time taken in seconds
            - warnings: List of warning messages

    Raises:
        FileLoadError: If file cannot be loaded
        ConfigurationError: If configuration is invalid
        DataOpsError: For other processing errors

    Examples:
        >>> # Basic usage with file path
        >>> result = process(
        ...     file_path="data.csv",
        ...     instruction="Remove duplicates and filter rows where age > 25"
        ... )
        >>> if result.success:
        ...     result.save("output.csv")
        ...     print(result.report)

        >>> # Using with DataFrame
        >>> import pandas as pd
        >>> df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        >>> result = process(
        ...     file_path=df,
        ...     instruction="Add a column 'age_group' categorizing age"
        ... )

        >>> # Dry-run mode to see what code would be executed
        >>> result = process(
        ...     file_path="data.csv",
        ...     instruction="Normalize all text columns to lowercase",
        ...     dry_run=True,
        ...     return_code=True
        ... )
        >>> print(result.generated_code)

        >>> # Custom LLM configuration
        >>> result = process(
        ...     file_path="data.csv",
        ...     instruction="Group by category and sum sales",
        ...     llm_config={
        ...         "api_key": "sk-...",
        ...         "model": "claude-3-5-sonnet-20241022",
        ...         "temperature": 0.0
        ...     }
        ... )
    """
    # Load data
    if isinstance(file_path, pd.DataFrame):
        df = file_path
    else:
        df = FileLoader.load(file_path)
        FileLoader.validate_dataframe(df)

    # Initialize configurations
    llm_cfg = LLMConfig(**llm_config) if llm_config else LLMConfig()
    sandbox_cfg = SandboxConfig(**sandbox_config) if sandbox_config else SandboxConfig()

    # Create executor and run pipeline
    executor = PipelineExecutor(llm_config=llm_cfg, sandbox_config=sandbox_cfg)

    # Execute pipeline synchronously
    result = executor.execute_sync(
        instruction=instruction,
        dataframe=df,
        dry_run=dry_run,
        return_code=return_code
    )

    return result


# Convenience alias
execute = process
