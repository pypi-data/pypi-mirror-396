"""
DeepEval Evaluator Module.

This module implements the DeepEval evaluator for LLM-based metrics.
"""

import json
import re
import time
import asyncio
import random
from collections import defaultdict
from typing import List, Dict, Any, Optional, Type, Union
from pydantic import BaseModel, ValidationError

# Import connection error types for retry logic
from httpx import ConnectError, ConnectTimeout, ReadTimeout
CONNECTION_ERRORS = (ConnectError, ConnectTimeout, ReadTimeout)

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.evaluate import ErrorConfig
from deepeval.config.settings import get_settings

from flotorch.sdk.llm import FlotorchLLM
from flotorch_eval.llm_eval.core.base_evaluator import BaseEvaluator
from flotorch_eval.llm_eval.core.schemas import EvaluationItem
from flotorch_eval.llm_eval.metrics.deepeval_metrics.deepeval_metrics import (
    DeepEvalEvaluationMetrics,
)
from flotorch_eval.llm_eval.metrics.metric_keys import MetricKey


# Default constants
DEFAULT_TIMEOUT_SECONDS = 350
DEFAULT_THROTTLE_VALUE = 2
DEFAULT_MAX_RETRIES = 3


class FloTorchLLMWrapper(DeepEvalBaseLLM):
    """
    Wrapper class for the FlotorchLLM.
    It is used to wrap the FlotorchLLM and make it compatible with the DeepEval framework.
    
    Args:
        inference_llm: The model ID of the underlying inference LLM.
        api_key: The API key for the FlotorchLLM.
        base_url: The base URL for the FlotorchLLM.
        max_retries: Maximum number of retry attempts for API calls.
        *args: Additional arguments to pass to the DeepEvalBaseLLM class.
        **kwargs: Additional keyword arguments to pass to the DeepEvalBaseLLM class.
    """
    
    def __init__(
        self, 
        inference_llm: str, 
        api_key: str, 
        base_url: str, 
        max_retries: int = DEFAULT_MAX_RETRIES,
        *args, 
        **kwargs
    ):
        """
        Initializes the FloTorchLLMWrapper.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.inference_llm = inference_llm
        self.max_retries = max_retries
        self.client = self.load_model()
        super().__init__(*args, **kwargs)

    def get_model_name(self, *args, **kwargs) -> str:
        """
        Returns the model ID of the underlying inference LLM.
        """
        return self.inference_llm

    def _extract_prompt_and_schema(self, *args, **kwargs):
        """Extract prompt and schema from args/kwargs."""
        prompt = args[0] if args else kwargs.get("prompt")
        schema = args[1] if len(args) > 1 else kwargs.get("schema", None)
        return prompt, schema

    def _extract_content(self, response):
        """Extract content from response, handling tuple responses."""
        if isinstance(response, tuple):
            response = response[0]
        return response.content

    def _is_connection_error(self, e: Exception) -> bool:
        """
        Return True if the exception looks like a connection/timeout error.
        """
        name = type(e).__name__.lower()
        msg = str(e).lower()

        type_keywords = (
            "connecterror",
            "connecttimeout",
            "readtimeout",
            "timeout",
        )
        msg_keywords = (
            "server disconnected",
            "connection",
            "timeout",
            "disconnected",
        )

        return (
            isinstance(e, CONNECTION_ERRORS)
            or any(k in name for k in type_keywords)
            or any(k in msg for k in msg_keywords)
        )

    def _is_rate_limit_error(self, e: Exception) -> bool:
        """
        Return True if the exception is a rate limit error.
        """
        error_str = str(e).lower()
        return (
            "rate_limit" in error_str
            or "too many requests" in error_str
            or "rate limit exceeded" in error_str
        )

    def _retry_with_backoff(self, func, max_retries: Optional[int] = None):
        """
        Retry a function with exponential backoff on connection/rate limit errors.
        
        Args:
            func: Callable to execute
            max_retries: Maximum number of retry attempts. If None, uses instance default.
        
        Returns:
            Result of func()
        """
        retries = max_retries if max_retries is not None else self.max_retries
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                if (self._is_connection_error(e) or self._is_rate_limit_error(e)) and attempt < retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 2)
                    time.sleep(wait_time)
                    continue
                raise

    async def _a_retry_with_backoff(self, func, max_retries: Optional[int] = None):
        """
        Retry an async function with exponential backoff on connection/rate limit errors.
        
        Args:
            func: Async callable to execute
            max_retries: Maximum number of retry attempts. If None, uses instance default.
        
        Returns:
            Result of await func()
        """
        retries = max_retries if max_retries is not None else self.max_retries
        for attempt in range(retries):
            try:
                return await func()
            except Exception as e:
                if (self._is_connection_error(e) or self._is_rate_limit_error(e)) and attempt < retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 2)
                    await asyncio.sleep(wait_time)
                    continue
                raise

    def _extract_json_from_text(self, text: str) -> Optional[Any]:
        """
        Extract JSON from text in a robust but simple way.

        Strategy:
            1. Try to parse the whole string as JSON.
            2. If fenced code blocks (``` or ```json) are present, try to parse their content.
            3. Otherwise, look for the first JSON object/array in the text and parse that.

        Returns:
            Parsed JSON object (dict / list / primitive) or None if parsing fails.
        """
        text = text.strip()
        if not text:
            return None

        # 1) Try direct JSON parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2) Try fenced code block content (``` or ```json)
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            fenced_content = fence_match.group(1).strip()
            if fenced_content:
                try:
                    return json.loads(fenced_content)
                except json.JSONDecodeError:
                    pass

        # 3) Try to find the first JSON object or array in the text
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if not match:
            return None

        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    def generate(self, *args, **kwargs):
        """
        Generates a response for a prompt and validates it against a schema if provided.

        Args:
            prompt (str): The prompt to generate from.
            schema (Optional[Type[BaseModel]]): Optional schema for validation.
        """
        prompt, schema = self._extract_prompt_and_schema(*args, **kwargs)
        
        def _invoke():
            response = self.client.invoke(
                messages=[{"role": "user", "content": prompt}]
            )
            completion = self._extract_content(response)
            return self._schema_validation(completion, schema)
        
        return self._retry_with_backoff(_invoke)

    async def a_generate(self, *args, **kwargs) -> str:
        """
        Asynchronously generates a response for a prompt and
        validates it against a schema if provided.

        Args:
            prompt (str): The prompt to generate from.
            schema (Optional[Type[BaseModel]]): Optional schema for validation.
        """
        prompt, schema = self._extract_prompt_and_schema(*args, **kwargs)
        
        async def _ainvoke():
            response = await self.client.ainvoke(
                messages=[{"role": "user", "content": prompt}]
            )
            completion = self._extract_content(response)
            return await self._a_schema_validation(completion, schema)
        
        return await self._a_retry_with_backoff(_ainvoke)

    def load_model(self, *args, **kwargs):
        """
        Loads and returns the inference LLM client.
        """
        return FlotorchLLM(
            model_id=self.inference_llm,
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _llm_fix_json_prompt(self, bad_json: str) -> str:
        """
        Builds a prompt for fixing malformed JSON.
        Args:
            bad_json (str): The malformed JSON to fix.
        Returns:
            str: The fixed JSON.
        """
        instructions = """The following is a malformed JSON (possibly incomplete or with syntax issues).
            Fix it so that it becomes **valid JSON**.

            CRITICAL RULES:
            1. Do NOT include Markdown formatting (no triple backticks, no ```json).
            2. Do NOT add or invent any new keys or values.
            3. Only fix unclosed strings, arrays, or braces.
            4. Remove any trailing commas at the end of JSON objects or arrays.
            5. Ensure all property names and string values are enclosed in double quotes.

            JSON ESCAPING RULES (VERY IMPORTANT):
            - Valid escape sequences in JSON strings: \\" (quote), \\\\ (backslash), \\/ (slash), \\n (newline), \\t (tab), \\r (carriage return), \\uXXXX (unicode)
            - DO NOT escape single quotes/apostrophes - they are valid as-is inside double-quoted strings
            * CORRECT: "agent's state" 
            * WRONG: "agent\\'s state" (this causes "Invalid \\escape" error)
            - Replace actual newline characters with \\n
            - Replace actual tab characters with \\t
            - Replace actual carriage return characters with \\r
            - All other control characters (0x00-0x1F) must be escaped as \\uXXXX
            - Only use valid escape sequences listed above - any other \\ followed by a character is INVALID

            Examples of VALID JSON strings:
            - "This is agent's text" (single quote is fine)
            - "Line 1\\nLine 2" (newline escaped)
            - "Tab\\tseparated" (tab escaped)
            - "Quote: \\"text\\"" (double quote escaped)

            Examples of INVALID JSON strings:
            - "agent\\'s text" (single quote should NOT be escaped)
            - "Line 1
            Line 2" (actual newline, should be \\n)
            - "Invalid\\x escape" (\\x is not a valid JSON escape)

            Preserve the original structure and values. If lists seem incomplete, close them properly.
            Output ONLY valid, raw JSON. No explanation, no surrounding text, no markdown.

            Malformed JSON to fix:
            """
        return f"{instructions}\n{bad_json}"

    def fix_common_truncation(self, json_str: str) -> str:
        """
        Fixes common truncation issues in JSON strings.
        """
        if not json_str.endswith("]") and not json_str.endswith("}"):
            json_str += '"}]}'
        return json_str

    def trim_json(self, completion: str, max_retries: Optional[int] = None) -> str:
        """
        Trims JSON strings to remove trailing commas and ensure they are valid JSON.
        """
        prompt = self._llm_fix_json_prompt(completion)
        
        def _invoke():
            response = self.client.invoke(
                messages=[{"role": "user", "content": prompt}]
            )
            return self._extract_content(response).strip()
        
        fixed_json = self._retry_with_backoff(_invoke, max_retries=max_retries)

        # Optional: Validate the output is valid JSON
        try:
            json.loads(fixed_json)
        except json.JSONDecodeError as e:
            fixed_json = self.fix_common_truncation(fixed_json)
            try:
                json.loads(fixed_json)
            except json.JSONDecodeError as e2:
                error_msg = (
                    f"Model returned invalid JSON (even after fix): {e2}"
                    f"\n\nReturned:\n{fixed_json}"
                )
                raise ValueError(error_msg) from e2
        return fixed_json

    async def a_trim_json(self, completion: str, max_retries: Optional[int] = None) -> str:
        """
        Asynchronously trims JSON strings to remove trailing commas and ensure they are valid JSON.
        """
        prompt = self._llm_fix_json_prompt(completion)
        
        async def _ainvoke():
            response = await self.client.ainvoke(
                messages=[{"role": "user", "content": prompt}]
            )
            return self._extract_content(response).strip()
        
        fixed_json = await self._a_retry_with_backoff(_ainvoke, max_retries=max_retries)

        # Optional: Validate the output is valid JSON
        try:
            json.loads(fixed_json)
        except json.JSONDecodeError as e:
            fixed_json = self.fix_common_truncation(fixed_json)
            try:
                json.loads(fixed_json)
            except json.JSONDecodeError as e2:
                error_msg = (
                    f"Model returned invalid JSON (even after fix): {e2}"
                    f"\n\nReturned:\n{fixed_json}"
                )
                raise ValueError(error_msg) from e2
        return fixed_json

    def _schema_validation(
        self, completion: str, schema: Optional[Type[BaseModel]] = None
    ) -> Any:
        if schema is None:
            # Try to extract and fix JSON even without schema
            parsed_json = self._extract_json_from_text(completion)
            if parsed_json is None:
                try:
                    fixed_json_str = self.trim_json(completion)
                    parsed_json = json.loads(fixed_json_str)
                except (ValueError, json.JSONDecodeError):
                    return completion.strip()
            return json.dumps(parsed_json) if isinstance(parsed_json, (dict, list)) else str(parsed_json)
        
        # First, try to extract JSON from text (handles markdown, etc.)
        parsed_json = self._extract_json_from_text(completion)
        
        # If extraction failed, try LLM-based fixing
        if parsed_json is None:
            try:
                json_output = self.trim_json(completion)
                return schema.model_validate(json.loads(json_output))
            except (json.JSONDecodeError, ValueError):
                # Fallback to old behavior
                return schema.model_validate(json.loads(completion))
        else:
            try:
                return schema.model_validate(parsed_json)
            except ValidationError:
                # If schema validation fails, try LLM fixing
                try:
                    json_output = self.trim_json(completion)
                    return schema.model_validate(json.loads(json_output))
                except (json.JSONDecodeError, ValueError):
                    raise

    async def _a_schema_validation(
        self, completion: str, schema: Optional[Type[BaseModel]] = None
    ) -> Any:
        if schema is None:
            # Try to extract and fix JSON even without schema
            parsed_json = self._extract_json_from_text(completion)
            if parsed_json is None:
                try:
                    fixed_json_str = await self.a_trim_json(completion)
                    parsed_json = json.loads(fixed_json_str)
                except (ValueError, json.JSONDecodeError):
                    return completion.strip()
            return json.dumps(parsed_json) if isinstance(parsed_json, (dict, list)) else str(parsed_json)
        
        # First, try to extract JSON from text (handles markdown, etc.)
        parsed_json = self._extract_json_from_text(completion)
        
        # If extraction failed, try async LLM-based fixing
        if parsed_json is None:
            try:
                json_output = await self.a_trim_json(completion)
                return schema.model_validate(json.loads(json_output))
            except (json.JSONDecodeError, ValueError):
                # Fallback to old behavior
                return schema.model_validate(json.loads(completion))
        else:
            try:
                return schema.model_validate(parsed_json)
            except ValidationError:
                # If schema validation fails, try async LLM fixing
                try:
                    json_output = await self.a_trim_json(completion)
                    return schema.model_validate(json.loads(json_output))
                except (json.JSONDecodeError, ValueError):
                    raise


class DeepEvalEvaluator(BaseEvaluator):
    """
    Evaluator that uses DeepEval metrics to evaluate LLM outputs with optional custom metrics
    and support for asynchronous evaluation.

    This evaluator computes both aggregated metrics (averaged across all questions) and
    question-level metrics (scores for each individual question) to provide comprehensive
    evaluation results.

    Initializes with an LLM inferencer and
    allows configuration of custom metrics, asynchronous execution,
    concurrency limits, and optional metric-specific arguments.

    Args:
        evaluator_llm: The LLM inferencer used for evaluation.
        api_key: The API key for the FlotorchLLM.
        base_url: The base URL for the FlotorchLLM.
        custom_metrics: A list of additional metric instances to include in
            evaluation beyond the default DeepEval metrics registry.
        async_run: Whether to run evaluation asynchronously.
            If True, evaluation can run concurrently up to `max_concurrent` tasks.
        max_concurrent: Maximum number of concurrent asynchronous evaluation tasks to run.
        throttle: Throttle value for async evaluation (delay between requests).
        max_retries: Maximum number of retry attempts for API calls.
        metric_args: Optional dictionary specifying per-metric configuration arguments.
        per_task_timeout_seconds: Optional timeout in seconds for each individual
            evaluation task (per test case/metric). This is NOT the total timeout for
            all tasks - each task gets this timeout budget. If None, uses DeepEval's
            default (180 seconds per task). This sets the
            DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE environment variable.

    Example:
        metric_args = {
            "contextual_recall": {
                "threshold": 0.6
            },
            "hallucination": {
                "threshold": 0.4
            }
        }

    The evaluate() method returns:
        - Aggregated metrics: Dictionary with metric names as keys and averaged scores as values
        - Question-level results: List of dictionaries, each containing question details and
          per-question metric scores (accessible via '_question_level_results' key)
    """

    # Mapping from DeepEval metric names to MetricKey enums
    _DEEPEVAL_TO_METRIC_KEY = {
        "Contextual Relevancy": MetricKey.CONTEXT_RELEVANCY,
        "Contextual Recall": MetricKey.CONTEXT_RECALL,
        "Hallucination": MetricKey.HALLUCINATION,
        "Faithfulness": MetricKey.FAITHFULNESS,
        "Answer Relevancy": MetricKey.ANSWER_RELEVANCE,
        "Contextual Precision": MetricKey.CONTEXT_PRECISION,
    }

    def __init__(
        self,
        evaluator_llm: str,
        api_key: str,
        base_url: str,
        custom_metrics: Optional[List[Any]] = None,
        async_run: bool = True,
        max_concurrent: int = 5,
        throttle: int = DEFAULT_THROTTLE_VALUE,
        max_retries: int = DEFAULT_MAX_RETRIES,
        metric_args: Optional[
            Dict[Union[str, MetricKey], Dict[str, Union[str, float, int]]]
        ] = None,
        per_task_timeout_seconds: Optional[float] = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.llm = FloTorchLLMWrapper(
            inference_llm=evaluator_llm, 
            api_key=api_key, 
            base_url=base_url,
            max_retries=max_retries
        )
        self.async_config = AsyncConfig(
            run_async=async_run, 
            max_concurrent=max_concurrent, 
            throttle_value=throttle
        )
        self.custom_metrics = custom_metrics or []
        self.metric_args = metric_args
        self.max_retries = max_retries
        self.per_task_timeout_seconds = per_task_timeout_seconds

        # Initialize DeepEval metrics from the registry
        DeepEvalEvaluationMetrics.initialize_metrics(
            llm=self.llm, metric_args=self.metric_args
        )

    def _build_test_cases(self, data: List[EvaluationItem]) -> List[LLMTestCase]:
        """
        Converts evaluation data into LLM test cases for DeepEval evaluation.
        """
        return [
            LLMTestCase(
                input=item.question,
                actual_output=item.generated_answer,
                expected_output=item.expected_answer,
                retrieval_context=item.context or [],
                context=item.context or [],
            )
            for item in data
        ]

    @staticmethod
    def _create_question_result(item: EvaluationItem) -> Dict[str, Any]:
        """Create a question result dictionary from an EvaluationItem."""
        return {
            "question": item.question,
            "generated_answer": item.generated_answer,
            "expected_answer": item.expected_answer,
            "context": item.context,
            "metrics": {},
        }

    @staticmethod
    def _round_score(score: Any) -> Any:
        """Round numeric scores to 2 decimal places, leave non-numeric as-is."""
        return round(score, 2) if isinstance(score, (int, float)) else score

    def _process_results(
        self, eval_results, data: List[EvaluationItem]
    ) -> Dict[str, Any]:
        """
        Processes the raw DeepEval results to calculate average scores
        for each metric across all test cases and extract question-level results.

        Args:
            eval_results: EvaluationResult object from deepeval.evaluate().
            data: Original list of EvaluationItem objects used for evaluation.

        Returns:
            Dictionary containing:
            - Aggregated metrics: Dictionary mapping metric keys to averaged scores
            - Question-level results: List of dictionaries with per-question metrics
        """
        metric_scores = defaultdict(list)
        question_level_results = []

        # Process each test result and map to original data items
        # Ensure we process all data items, even if some test results are missing
        num_results = len(eval_results.test_results)
        num_data_items = len(data)

        for i in range(max(num_results, num_data_items)):
            # Get corresponding data item
            if i < num_data_items:
                item = data[i]
                question_result = self._create_question_result(item)

                # Extract metrics for this question if test result exists
                if i < num_results:
                    test_result = eval_results.test_results[i]
                    for metric_data in test_result.metrics_data:
                        metric_key_enum = self._DEEPEVAL_TO_METRIC_KEY.get(
                            metric_data.name
                        )
                        if metric_key_enum and metric_data.score is not None:
                            metric_name = metric_key_enum.value
                            rounded_score = self._round_score(metric_data.score)
                            question_result["metrics"][metric_name] = rounded_score
                            metric_scores[metric_name].append(metric_data.score)

                question_level_results.append(question_result)

        # Calculate averaged results
        averaged_results = {
            metric_name: round(sum(scores) / len(scores), 2)
            for metric_name, scores in metric_scores.items()
            if scores
        }

        # Add question-level results to the return dict
        averaged_results["_question_level_results"] = question_level_results

        return averaged_results

    def evaluate(
        self, data: List[EvaluationItem], metrics: Optional[List[MetricKey]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the provided data using DeepEval metrics.

        Args:
            data: List of EvaluationItem objects containing questions, answers, and context.
            metrics: Optional list of MetricKey enums to evaluate. If None, uses all available metrics.

        Returns:
            Dictionary containing:
            - Aggregated metrics (averaged across all questions): metric names as keys,
              averaged scores as values (e.g., {'faithfulness': 0.95, 'answer_relevance': 0.88})
            - Question-level results: stored under '_question_level_results' key as a list of dicts,
              where each dict contains:
              - 'question': The input question
              - 'generated_answer': The model's generated answer
              - 'expected_answer': The expected/ground truth answer
              - 'context': List of context chunks used
              - 'metrics': Dictionary of metric scores for this specific question
                  (e.g., {'faithfulness': 0.98, 'answer_relevance': 0.92})
        """
        test_cases = self._build_test_cases(data)

        if metrics is None:
            # Get all available metrics as MetricKey enums
            available_metric_strings = DeepEvalEvaluationMetrics.available_metrics()
            # Create reverse mapping from metric string values to MetricKey enums
            metric_string_to_enum = {
                enum_val.value: enum_val
                for enum_val in self._DEEPEVAL_TO_METRIC_KEY.values()
            }
            metrics = [
                metric_string_to_enum[m]
                for m in available_metric_strings
                if m in metric_string_to_enum
            ]

        # Convert MetricKey enums to strings for DeepEval's get_metric method
        metric_strings = [m.value if isinstance(m, MetricKey) else m for m in metrics]
        selected_metrics = [
            DeepEvalEvaluationMetrics.get_metric(m) for m in metric_strings
        ]
        
        # Set timeout for sync evaluation
        settings = get_settings()
        with settings.edit(persist=False):
            settings.DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE = (
                self.per_task_timeout_seconds or DEFAULT_TIMEOUT_SECONDS
            )

        # Create sync config (run_async=False) using instance's async_config values
        sync_config = AsyncConfig(
            run_async=False,
            max_concurrent=self.async_config.max_concurrent,
            throttle_value=self.async_config.throttle_value
        )

        eval_results = evaluate(
            test_cases=test_cases,
            async_config=sync_config,
            metrics=selected_metrics + self.custom_metrics,
            error_config=ErrorConfig(ignore_errors=True),
        )
        # Process results to get averaged scores and question-level results
        processed_results = self._process_results(eval_results, data)
        return processed_results

    async def aevaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None,
        max_concurrent: Optional[int] = None,
        throttle: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously evaluate the data using DeepEval with concurrent processing.
        
        Args:
            data: The data to evaluate.
            metrics: Optional list of MetricKey enums to evaluate. If None, uses all available metrics.
            max_concurrent: Maximum number of concurrent workers.
                If None, uses the instance's async_config.max_concurrent.
            throttle: Throttle value for async evaluation. If None, uses instance's async_config.throttle_value.
            max_retries: Maximum number of retry attempts. If None, uses instance's max_retries.
        
        Returns:
            Dictionary containing:
            - Aggregated metrics (averaged across all questions): metric names as keys,
              averaged scores as values
            - Question-level results: stored under '_question_level_results' key as a list of dicts
        """
        test_cases = self._build_test_cases(data)
        
        if metrics is None:
            # Get all available metrics as MetricKey enums
            available_metric_strings = DeepEvalEvaluationMetrics.available_metrics()
            # Create reverse mapping from metric string values to MetricKey enums
            metric_string_to_enum = {
                enum_val.value: enum_val
                for enum_val in self._DEEPEVAL_TO_METRIC_KEY.values()
            }
            metrics = [
                metric_string_to_enum[m]
                for m in available_metric_strings
                if m in metric_string_to_enum
            ]

        # Convert MetricKey enums to strings for DeepEval's get_metric method
        metric_strings = [m.value if isinstance(m, MetricKey) else m for m in metrics]
        selected_metrics = [
            DeepEvalEvaluationMetrics.get_metric(m) for m in metric_strings
        ]
        
        # Use provided parameters or fall back to instance defaults
        effective_max_concurrent = max_concurrent if max_concurrent is not None else self.async_config.max_concurrent
        effective_throttle = throttle if throttle is not None else self.async_config.throttle_value
        effective_max_retries = max_retries if max_retries is not None else self.max_retries
        
        async_config = AsyncConfig(
            run_async=True,
            max_concurrent=effective_max_concurrent,
            throttle_value=effective_throttle
        )
        
        settings = get_settings()
        with settings.edit(persist=False):
            settings.DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE = (
                self.per_task_timeout_seconds or DEFAULT_TIMEOUT_SECONDS
            )
            settings.DEEPEVAL_RETRY_MAX_ATTEMPTS = effective_max_retries
            settings.DEEPEVAL_VERBOSE_MODE = False
        
        eval_results = evaluate(
            test_cases=test_cases,
            async_config=async_config,
            metrics=selected_metrics + self.custom_metrics,
            error_config=ErrorConfig(ignore_errors=True),
        )
        
        # Process results to get averaged scores and question-level results
        processed_results = self._process_results(eval_results, data)
        return processed_results
