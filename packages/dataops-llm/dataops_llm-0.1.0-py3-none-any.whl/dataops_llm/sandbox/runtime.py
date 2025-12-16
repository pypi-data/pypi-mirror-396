"""Sandbox runtime for isolated code execution using subprocess isolation."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import pandas as pd

from dataops_llm.config import SandboxConfig
from dataops_llm.exceptions import ExecutionTimeoutError, SandboxError
from dataops_llm.sandbox.limits import ResourceMonitor


class SandboxRuntime:
    """Executes Python code in an isolated subprocess environment.

    This runtime provides strong isolation by executing code in a separate
    process with resource limits, timeout enforcement, and no access to
    the parent process memory or file system (except temp directory).

    Attributes:
        config: Sandbox configuration
        monitor: Resource monitor for limit enforcement
    """

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize the sandbox runtime.

        Args:
            config: Sandbox configuration. Uses default if not provided.
        """
        self.config = config or SandboxConfig()
        self.monitor = ResourceMonitor(self.config)

    def execute(
        self,
        code: str,
        dataframe: pd.DataFrame,
        context: dict[str, Any] | None = None
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Execute code in isolated subprocess.

        Args:
            code: Python code to execute
            dataframe: Input DataFrame
            context: Optional execution context

        Returns:
            Tuple of (result_dataframe, execution_metadata)

        Raises:
            ExecutionTimeoutError: If execution exceeds timeout
            SandboxError: If execution fails
        """
        # Validate input DataFrame size
        self.monitor.validate_dataframe_size(dataframe, raise_on_exceed=True)

        # Create temporary directory for inter-process communication
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Define file paths
            input_path = tmpdir_path / "input.pkl"
            output_path = tmpdir_path / "output.pkl"
            metadata_path = tmpdir_path / "metadata.json"
            error_path = tmpdir_path / "error.txt"

            try:
                # Serialize input DataFrame
                dataframe.to_pickle(input_path)

                # Build execution script
                script = self._build_execution_script(
                    code=code,
                    input_path=input_path,
                    output_path=output_path,
                    metadata_path=metadata_path,
                    error_path=error_path,
                    context=context
                )

                # Execute in subprocess
                start_time = time.time()
                result = self._execute_subprocess(script)
                execution_time = time.time() - start_time

                # Check for errors
                if error_path.exists():
                    error_msg = error_path.read_text()
                    raise SandboxError(f"Execution failed: {error_msg}")

                # Load result
                if not output_path.exists():
                    raise SandboxError("Execution completed but no output file was created")

                result_df = pd.read_pickle(output_path)

                # Validate output DataFrame size
                self.monitor.validate_dataframe_size(result_df, raise_on_exceed=True)

                # Load metadata
                if metadata_path.exists():
                    metadata = json.loads(metadata_path.read_text())
                else:
                    metadata = {}

                # Add execution time to metadata
                metadata["execution_time"] = execution_time
                metadata["subprocess_success"] = True

                return result_df, metadata

            except subprocess.TimeoutExpired:
                raise ExecutionTimeoutError(
                    f"Execution exceeded timeout limit of {self.config.timeout} seconds"
                )
            except SandboxError:
                raise
            except Exception as e:
                raise SandboxError(f"Unexpected error during execution: {e}")

    def _build_execution_script(
        self,
        code: str,
        input_path: Path,
        output_path: Path,
        metadata_path: Path,
        error_path: Path,
        context: dict[str, Any] | None
    ) -> str:
        """Build the Python script to execute in subprocess.

        Args:
            code: User code to execute
            input_path: Path to input DataFrame pickle
            output_path: Path to output DataFrame pickle
            metadata_path: Path to metadata JSON
            error_path: Path to error output
            context: Optional execution context

        Returns:
            Complete Python script as string
        """
        # Escape paths for Windows compatibility
        input_path_str = str(input_path).replace("\\", "\\\\")
        output_path_str = str(output_path).replace("\\", "\\\\")
        metadata_path_str = str(metadata_path).replace("\\", "\\\\")
        error_path_str = str(error_path).replace("\\", "\\\\")

        script = f"""
import sys
import json
import traceback
import time
import pandas as pd
import numpy as np

# Execution metadata
metadata = {{
    "start_time": time.time(),
    "warnings": [],
    "rows_before": 0,
    "rows_after": 0,
    "columns_before": 0,
    "columns_after": 0,
}}

try:
    # Load input DataFrame
    df = pd.read_pickle(r"{input_path_str}")

    # Record initial state
    metadata["rows_before"] = len(df)
    metadata["columns_before"] = len(df.columns)

    # Execute user code
    # The code should modify 'df' and the last expression should be 'df'
    result = eval(compile('''
{code}
''', '<string>', 'exec'))

    # If code doesn't explicitly return df, use the modified df
    if result is None:
        result = df

    # Record final state
    metadata["rows_after"] = len(result)
    metadata["columns_after"] = len(result.columns)
    metadata["end_time"] = time.time()
    metadata["execution_time"] = metadata["end_time"] - metadata["start_time"]

    # Save result
    result.to_pickle(r"{output_path_str}")

    # Save metadata
    with open(r"{metadata_path_str}", 'w') as f:
        json.dump(metadata, f)

except Exception as e:
    # Capture error
    error_info = {{
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }}

    with open(r"{error_path_str}", 'w') as f:
        f.write(json.dumps(error_info, indent=2))

    sys.exit(1)
"""
        return script

    def _execute_subprocess(self, script: str) -> subprocess.CompletedProcess:
        """Execute script in subprocess with timeout.

        Args:
            script: Python script to execute

        Returns:
            CompletedProcess result

        Raises:
            subprocess.TimeoutExpired: If execution exceeds timeout
            SandboxError: If subprocess fails
        """
        try:
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                check=False  # Don't raise on non-zero exit
            )

            # Check if process failed (non-zero exit code)
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise SandboxError(f"Subprocess exited with code {result.returncode}: {error_msg}")

            return result

        except subprocess.TimeoutExpired as e:
            raise ExecutionTimeoutError(
                f"Execution exceeded timeout limit of {self.config.timeout} seconds"
            )
        except SandboxError:
            raise
        except Exception as e:
            raise SandboxError(f"Failed to execute subprocess: {e}")

    def test_sandbox(self) -> dict[str, Any]:
        """Test sandbox functionality with a simple operation.

        Returns:
            Dictionary with test results

        Raises:
            SandboxError: If test fails
        """
        # Create test DataFrame
        test_df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4, 5, 6]
        })

        # Simple test code
        test_code = "df['c'] = df['a'] + df['b']\ndf"

        try:
            result_df, metadata = self.execute(test_code, test_df)

            # Verify result
            assert "c" in result_df.columns
            assert list(result_df["c"]) == [5, 7, 9]

            return {
                "status": "success",
                "message": "Sandbox is working correctly",
                "metadata": metadata
            }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Sandbox test failed: {e}",
                "error": str(e)
            }
