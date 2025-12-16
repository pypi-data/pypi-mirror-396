"""File loading utilities for CSV and Excel files."""

from pathlib import Path
from typing import Union

import pandas as pd

from dataops_llm.exceptions import FileLoadError


class FileLoader:
    """Loads tabular data files into pandas DataFrames.

    Supports CSV and Excel formats with automatic format detection
    and error handling.

    Attributes:
        SUPPORTED_FORMATS: Set of supported file extensions
    """

    SUPPORTED_FORMATS = {".csv", ".xlsx", ".xls"}

    @staticmethod
    def load(file_path: Union[str, Path]) -> pd.DataFrame:
        """Load file into DataFrame.

        Args:
            file_path: Path to the file

        Returns:
            Loaded DataFrame

        Raises:
            FileLoadError: If file cannot be loaded
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise FileLoadError(f"File not found: {path}")

        # Check file format
        suffix = path.suffix.lower()
        if suffix not in FileLoader.SUPPORTED_FORMATS:
            raise FileLoadError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: {', '.join(FileLoader.SUPPORTED_FORMATS)}"
            )

        try:
            if suffix == ".csv":
                return FileLoader._load_csv(path)
            else:  # Excel (.xlsx or .xls)
                return FileLoader._load_excel(path)

        except FileLoadError:
            raise
        except Exception as e:
            raise FileLoadError(f"Failed to load file {path}: {e}")

    @staticmethod
    def _load_csv(path: Path) -> pd.DataFrame:
        """Load CSV file with encoding detection.

        Args:
            path: Path to CSV file

        Returns:
            Loaded DataFrame

        Raises:
            FileLoadError: If loading fails
        """
        try:
            # Try UTF-8 first (most common)
            return pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                # Try latin-1 as fallback
                return pd.read_csv(path, encoding="latin-1")
            except Exception as e:
                raise FileLoadError(f"Failed to decode CSV file: {e}")
        except pd.errors.EmptyDataError:
            raise FileLoadError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise FileLoadError(f"Failed to parse CSV file: {e}")

    @staticmethod
    def _load_excel(path: Path) -> pd.DataFrame:
        """Load Excel file.

        Args:
            path: Path to Excel file

        Returns:
            Loaded DataFrame

        Raises:
            FileLoadError: If loading fails
        """
        try:
            # Load first sheet by default
            df = pd.read_excel(path, engine="openpyxl")

            if df.empty:
                raise FileLoadError("Excel file is empty")

            return df

        except FileLoadError:
            raise
        except Exception as e:
            raise FileLoadError(f"Failed to load Excel file: {e}")

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """Validate that DataFrame has required properties.

        Args:
            df: DataFrame to validate

        Raises:
            FileLoadError: If DataFrame is invalid
        """
        if df.empty:
            raise FileLoadError("Loaded DataFrame is empty")

        if len(df.columns) == 0:
            raise FileLoadError("Loaded DataFrame has no columns")

    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> dict[str, any]:
        """Get information about a file without loading it.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information

        Raises:
            FileLoadError: If file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileLoadError(f"File not found: {path}")

        return {
            "path": str(path.absolute()),
            "name": path.name,
            "extension": path.suffix,
            "size_bytes": path.stat().st_size,
            "size_mb": path.stat().st_size / (1024 * 1024),
            "is_supported": path.suffix.lower() in FileLoader.SUPPORTED_FORMATS
        }
