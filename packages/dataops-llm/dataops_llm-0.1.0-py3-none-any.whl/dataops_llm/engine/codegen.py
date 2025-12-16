"""Code generator module - converts execution plan to Python code."""

import pandas as pd

from dataops_llm.exceptions import CodeGenerationError
from dataops_llm.llm.client import LLMClient
from dataops_llm.llm.prompts import (
    CODEGEN_SYSTEM_PROMPT,
    CODEGEN_USER_TEMPLATE,
    format_dataframe_schema,
)
from dataops_llm.llm.schemas import CodeResponse
from dataops_llm.models.plan import ExecutionPlan


class CodeGenerator:
    """Generates Python code from execution plans.

    This component uses an LLM to translate high-level execution plans
    into secure, efficient pandas code.

    Attributes:
        llm_client: LLM client for API calls
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the code generator.

        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client

    async def generate(
        self,
        plan: ExecutionPlan,
        dataframe: pd.DataFrame
    ) -> tuple[str, list[str]]:
        """Generate Python code from execution plan.

        Args:
            plan: Execution plan to convert to code
            dataframe: Input DataFrame for context

        Returns:
            Tuple of (generated_code, warnings)

        Raises:
            CodeGenerationError: If code generation fails
        """
        try:
            # Get DataFrame schema and sample
            schema_info = format_dataframe_schema(dataframe)

            # Get sample data
            sample_data = dataframe.head(3).to_string()

            # Build user prompt
            user_prompt = CODEGEN_USER_TEMPLATE.format(
                plan_json=plan.model_dump_json(indent=2),
                columns=", ".join(schema_info.get("columns", [])),
                shape=schema_info.get("shape", "unknown"),
                dtypes=schema_info.get("dtypes", {}),
                sample_data=sample_data
            )

            # Call LLM with structured output
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=CODEGEN_SYSTEM_PROMPT,
                response_format=CodeResponse
            )

            return response.code, response.warnings

        except Exception as e:
            raise CodeGenerationError(
                f"Failed to generate code from execution plan: {e}"
            )

    def generate_sync(
        self,
        plan: ExecutionPlan,
        dataframe: pd.DataFrame
    ) -> tuple[str, list[str]]:
        """Synchronous version of generate.

        Args:
            plan: Execution plan to convert to code
            dataframe: Input DataFrame for context

        Returns:
            Tuple of (generated_code, warnings)

        Raises:
            CodeGenerationError: If code generation fails
        """
        import asyncio
        return asyncio.run(self.generate(plan, dataframe))
