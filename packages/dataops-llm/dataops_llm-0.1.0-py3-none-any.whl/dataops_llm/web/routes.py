"""FastAPI routes for the DataOps LLM Engine API."""

import base64
import io

import pandas as pd
from fastapi import APIRouter, HTTPException

from dataops_llm import __version__, process
from dataops_llm.exceptions import DataOpsError
from dataops_llm.sandbox.runtime import SandboxRuntime
from dataops_llm.web.models import HealthResponse, ProcessRequest, ProcessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.

    Returns:
        Health status information
    """
    # Test sandbox
    sandbox = SandboxRuntime()
    sandbox_test = sandbox.test_sandbox()
    sandbox_available = sandbox_test["status"] == "success"

    return HealthResponse(
        status="healthy" if sandbox_available else "degraded",
        version=__version__,
        sandbox_available=sandbox_available
    )


@router.post("/process", response_model=ProcessResponse)
async def process_data(request: ProcessRequest):
    """Process data with natural language instruction.

    Args:
        request: Process request with instruction and file

    Returns:
        ProcessResponse with results

    Raises:
        HTTPException: If processing fails
    """
    try:
        # Decode file from base64
        try:
            file_bytes = base64.b64decode(request.file_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode base64 file: {e}"
            )

        # Load DataFrame based on format
        try:
            if request.file_format == "csv":
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:  # excel
                df = pd.read_excel(io.BytesIO(file_bytes))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to load {request.file_format} file: {e}"
            )

        # Process the data
        result = process(
            file_path=df,
            instruction=request.instruction,
            llm_config=request.llm_config,
            sandbox_config=request.sandbox_config,
            dry_run=request.dry_run,
            return_code=request.return_code
        )

        # Encode result DataFrame to base64 if available
        result_base64 = None
        if result.dataframe is not None:
            buffer = io.BytesIO()
            if request.file_format == "csv":
                result.dataframe.to_csv(buffer, index=False)
            else:  # excel
                result.dataframe.to_excel(buffer, index=False, engine="openpyxl")

            buffer.seek(0)
            result_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        # Build response
        return ProcessResponse(
            success=result.success,
            result_base64=result_base64,
            report=result.report,
            generated_code=result.generated_code,
            execution_time=result.execution_time,
            warnings=result.warnings,
            metadata=result.metadata
        )

    except DataOpsError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Data processing error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
