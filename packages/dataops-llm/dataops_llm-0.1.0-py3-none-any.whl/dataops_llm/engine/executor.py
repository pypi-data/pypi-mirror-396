"""Pipeline executor - orchestrates the entire execution flow."""

import time
from typing import Optional

import pandas as pd

from dataops_llm.config import LLMConfig, SandboxConfig
from dataops_llm.engine.codegen import CodeGenerator
from dataops_llm.engine.interpreter import InstructionInterpreter
from dataops_llm.engine.planner import ExecutionPlanner
from dataops_llm.engine.validator import CodeValidator
from dataops_llm.exceptions import DataOpsError
from dataops_llm.llm.client import LLMClient
from dataops_llm.models.result import DataOpsResult
from dataops_llm.sandbox.runtime import SandboxRuntime


class PipelineExecutor:
    """Orchestrates the complete execution pipeline.

    This is the main coordinator that runs the entire process:
    1. Interpret instruction → Intent
    2. Generate execution plan → ExecutionPlan
    3. Generate code → Python code
    4. Validate code → Security checks
    5. Execute code → Result DataFrame
    6. Build report → DataOpsResult

    Attributes:
        llm_client: LLM client for API calls
        interpreter: Instruction interpreter
        planner: Execution planner
        code generator: Code generator
        validator: Code validator
        sandbox: Sandbox runtime
    """

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        sandbox_config: Optional[SandboxConfig] = None
    ):
        """Initialize the pipeline executor.

        Args:
            llm_config: LLM configuration. Uses default if not provided.
            sandbox_config: Sandbox configuration. Uses default if not provided.
        """
        # Initialize components
        self.llm_client = LLMClient(llm_config or LLMConfig())
        self.interpreter = InstructionInterpreter(self.llm_client)
        self.planner = ExecutionPlanner(self.llm_client)
        self.codegen = CodeGenerator(self.llm_client)
        self.validator = CodeValidator(sandbox_config)
        self.sandbox = SandboxRuntime(sandbox_config)

    async def execute(
        self,
        instruction: str,
        dataframe: pd.DataFrame,
        dry_run: bool = False,
        return_code: bool = False
    ) -> DataOpsResult:
        """Execute the complete pipeline.

        Args:
            instruction: Natural language instruction
            dataframe: Input DataFrame
            dry_run: If True, generate plan and code but don't execute
            return_code: If True, include generated code in result

        Returns:
            DataOpsResult with execution outcome
        """
        start_time = time.time()
        warnings: list[str] = []
        generated_code: Optional[str] = None
        result_df: Optional[pd.DataFrame] = None

        try:
            # Step 1: Interpret instruction
            intent = await self.interpreter.interpret(instruction, dataframe)

            # Check confidence
            if intent.confidence < 0.7:
                warnings.append(
                    f"Low confidence ({intent.confidence:.2f}) in intent interpretation. "
                    "Results may not match expectations."
                )

            # Step 2: Generate execution plan
            plan = await self.planner.plan(intent, dataframe)

            # Add plan warnings
            if plan.metadata.get("warnings"):
                warnings.extend(plan.metadata["warnings"])

            # Step 3: Generate code
            code, code_warnings = await self.codegen.generate(plan, dataframe)
            generated_code = code
            warnings.extend(code_warnings)

            # Step 4: Validate code
            validation_result = self.validator.validate(code)

            if not validation_result.is_valid:
                # Code failed validation
                error_msg = "\n".join(validation_result.errors)
                return DataOpsResult(
                    success=False,
                    dataframe=None,
                    generated_code=generated_code if return_code else None,
                    execution_plan=plan if return_code else None,
                    report=f"Code validation failed:\n{error_msg}",
                    execution_time=time.time() - start_time,
                    warnings=warnings,
                    metadata={"validation_errors": validation_result.errors}
                )

            # Add validation warnings
            warnings.extend(validation_result.warnings)

            # Step 5: Execute code (unless dry-run)
            if dry_run:
                report = self._build_dry_run_report(intent, plan, code)
                result_df = None
            else:
                result_df, exec_metadata = self.sandbox.execute(code, dataframe)
                warnings.extend(exec_metadata.get("warnings", []))
                report = self._build_execution_report(
                    intent, plan, code, dataframe, result_df, exec_metadata
                )

            # Build successful result
            return DataOpsResult(
                success=True,
                dataframe=result_df,
                generated_code=generated_code if return_code else None,
                execution_plan=plan if return_code else None,
                report=report,
                execution_time=time.time() - start_time,
                warnings=warnings,
                metadata={
                    "intent_confidence": intent.confidence,
                    "plan_complexity": plan.estimated_complexity,
                    "plan_steps": plan.step_count,
                    "dry_run": dry_run
                }
            )

        except DataOpsError as e:
            # Known error - return structured failure
            return DataOpsResult(
                success=False,
                dataframe=None,
                generated_code=generated_code if return_code else None,
                execution_plan=None,
                report=f"Operation failed: {str(e)}",
                execution_time=time.time() - start_time,
                warnings=warnings,
                metadata={"error_type": type(e).__name__}
            )

        except Exception as e:
            # Unexpected error
            return DataOpsResult(
                success=False,
                dataframe=None,
                generated_code=generated_code if return_code else None,
                execution_plan=None,
                report=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time,
                warnings=warnings,
                metadata={"error_type": type(e).__name__}
            )

    def execute_sync(
        self,
        instruction: str,
        dataframe: pd.DataFrame,
        dry_run: bool = False,
        return_code: bool = False
    ) -> DataOpsResult:
        """Synchronous version of execute.

        Args:
            instruction: Natural language instruction
            dataframe: Input DataFrame
            dry_run: If True, generate plan and code but don't execute
            return_code: If True, include generated code in result

        Returns:
            DataOpsResult with execution outcome
        """
        import asyncio
        return asyncio.run(self.execute(instruction, dataframe, dry_run, return_code))

    def _build_dry_run_report(
        self,
        intent,
        plan,
        code: str
    ) -> str:
        """Build report for dry-run mode.

        Args:
            intent: Extracted intent
            plan: Execution plan
            code: Generated code

        Returns:
            Formatted report string
        """
        lines = [
            "=== DRY RUN MODE ===",
            "",
            "Instruction interpreted successfully.",
            f"Operation type: {intent.operation_type}",
            f"Confidence: {intent.confidence:.2f}",
            "",
            f"Execution plan generated with {plan.step_count} step(s):",
        ]

        for step in plan.steps:
            lines.append(f"  {step.step_id + 1}. {step.description}")

        lines.extend([
            "",
            "Code generated and validated successfully.",
            "No execution performed (dry-run mode).",
            "",
            "Use dry_run=False to execute the operation."
        ])

        return "\n".join(lines)

    def _build_execution_report(
        self,
        intent,
        plan,
        code: str,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame,
        exec_metadata: dict
    ) -> str:
        """Build report for successful execution.

        Args:
            intent: Extracted intent
            plan: Execution plan
            code: Generated code
            input_df: Input DataFrame
            output_df: Output DataFrame
            exec_metadata: Execution metadata

        Returns:
            Formatted report string
        """
        rows_before = len(input_df)
        rows_after = len(output_df)
        cols_before = len(input_df.columns)
        cols_after = len(output_df.columns)

        lines = [
            "=== EXECUTION SUCCESSFUL ===",
            "",
            f"Operation: {intent.operation_type}",
            f"Steps executed: {plan.step_count}",
            "",
            "Changes:",
            f"  Rows: {rows_before} -> {rows_after} ({rows_after - rows_before:+d})",
            f"  Columns: {cols_before} -> {cols_after} ({cols_after - cols_before:+d})",
        ]

        # Add column changes if any
        cols_removed = set(input_df.columns) - set(output_df.columns)
        cols_added = set(output_df.columns) - set(input_df.columns)

        if cols_removed:
            lines.append(f"  Removed columns: {', '.join(cols_removed)}")
        if cols_added:
            lines.append(f"  Added columns: {', '.join(cols_added)}")

        lines.extend([
            "",
            f"Execution time: {exec_metadata.get('execution_time', 0):.3f}s"
        ])

        return "\n".join(lines)
