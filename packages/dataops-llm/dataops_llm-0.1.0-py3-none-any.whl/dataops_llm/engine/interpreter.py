"""Instruction interpreter module - converts natural language to structured intent."""

import pandas as pd

from dataops_llm.exceptions import IntentExtractionError
from dataops_llm.llm.client import LLMClient
from dataops_llm.llm.prompts import (
    INTERPRETER_SYSTEM_PROMPT,
    INTERPRETER_USER_TEMPLATE,
    format_dataframe_preview,
    format_dataframe_schema,
)
from dataops_llm.llm.schemas import IntentResponse
from dataops_llm.models.intent import Intent


class InstructionInterpreter:
    """Interprets natural language instructions into structured intent.

    This component uses an LLM to analyze user instructions and extract
    structured information about what operation should be performed on the data.

    Attributes:
        llm_client: LLM client for API calls
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the interpreter.

        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client

    async def interpret(
        self,
        instruction: str,
        dataframe: pd.DataFrame
    ) -> Intent:
        """Convert natural language instruction to structured intent.

        Args:
            instruction: Natural language instruction from user
            dataframe: Input DataFrame for context

        Returns:
            Intent object with extracted information

        Raises:
            IntentExtractionError: If intent extraction fails
        """
        try:
            # Generate DataFrame preview and schema
            data_preview = format_dataframe_preview(dataframe, max_rows=5)
            schema_info = format_dataframe_schema(dataframe)

            # Build user prompt
            user_prompt = INTERPRETER_USER_TEMPLATE.format(
                data_preview=data_preview,
                shape=schema_info.get("shape", "unknown"),
                columns=", ".join(schema_info.get("columns", [])),
                dtypes=schema_info.get("dtypes", {}),
                instruction=instruction
            )

            # Call LLM with structured output
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=INTERPRETER_SYSTEM_PROMPT,
                response_format=IntentResponse
            )

            # Convert IntentResponse to Intent model
            intent = Intent(
                operation_type=response.operation_type,
                target_columns=response.target_columns,
                conditions=response.conditions,
                confidence=response.confidence,
                raw_instruction=instruction,
                metadata={"reasoning": response.reasoning}
            )

            return intent

        except Exception as e:
            raise IntentExtractionError(
                f"Failed to extract intent from instruction: {e}"
            )

    def interpret_sync(
        self,
        instruction: str,
        dataframe: pd.DataFrame
    ) -> Intent:
        """Synchronous version of interpret.

        Args:
            instruction: Natural language instruction from user
            dataframe: Input DataFrame for context

        Returns:
            Intent object with extracted information

        Raises:
            IntentExtractionError: If intent extraction fails
        """
        import asyncio
        return asyncio.run(self.interpret(instruction, dataframe))
