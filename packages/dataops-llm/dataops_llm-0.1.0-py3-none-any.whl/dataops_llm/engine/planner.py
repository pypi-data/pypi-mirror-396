"""Execution planner module - converts intent to execution plan."""

import pandas as pd

from dataops_llm.exceptions import PlanGenerationError
from dataops_llm.llm.client import LLMClient
from dataops_llm.llm.prompts import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_USER_TEMPLATE,
    format_dataframe_schema,
)
from dataops_llm.llm.schemas import PlanResponse
from dataops_llm.models.intent import Intent
from dataops_llm.models.plan import ExecutionPlan, ExecutionStep


class ExecutionPlanner:
    """Creates detailed execution plans from user intent.

    This component uses an LLM to break down high-level intent into
    specific, sequential steps that can be translated into code.

    Attributes:
        llm_client: LLM client for API calls
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the planner.

        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client

    async def plan(
        self,
        intent: Intent,
        dataframe: pd.DataFrame
    ) -> ExecutionPlan:
        """Create execution plan from intent.

        Args:
            intent: Extracted user intent
            dataframe: Input DataFrame for context

        Returns:
            ExecutionPlan with sequential steps

        Raises:
            PlanGenerationError: If plan generation fails
        """
        try:
            # Get DataFrame schema
            schema_info = format_dataframe_schema(dataframe)

            # Build user prompt
            user_prompt = PLANNER_USER_TEMPLATE.format(
                intent_json=intent.model_dump_json(indent=2),
                columns=", ".join(schema_info.get("columns", [])),
                dtypes=schema_info.get("dtypes", {}),
                row_count=schema_info.get("row_count", 0),
                column_count=schema_info.get("column_count", 0)
            )

            # Call LLM with structured output
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                response_format=PlanResponse
            )

            # Convert PlanResponse to ExecutionPlan
            steps = [
                ExecutionStep(**step_data)
                for step_data in response.steps
            ]

            plan = ExecutionPlan(
                steps=steps,
                estimated_complexity=response.complexity,
                requires_validation=len(response.warnings) > 0,
                metadata={
                    "warnings": response.warnings,
                    "reasoning": response.reasoning
                }
            )

            return plan

        except Exception as e:
            raise PlanGenerationError(
                f"Failed to generate execution plan: {e}"
            )

    def plan_sync(
        self,
        intent: Intent,
        dataframe: pd.DataFrame
    ) -> ExecutionPlan:
        """Synchronous version of plan.

        Args:
            intent: Extracted user intent
            dataframe: Input DataFrame for context

        Returns:
            ExecutionPlan with sequential steps

        Raises:
            PlanGenerationError: If plan generation fails
        """
        import asyncio
        return asyncio.run(self.plan(intent, dataframe))
