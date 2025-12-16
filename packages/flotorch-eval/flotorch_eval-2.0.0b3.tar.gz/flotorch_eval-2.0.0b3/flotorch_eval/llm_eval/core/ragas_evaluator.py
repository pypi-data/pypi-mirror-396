"""
Ragas Evaluator Module.

This module implements the Ragas evaluator for RAG-based metrics evaluation.
"""
from typing import Any, Dict, List, Optional, Union
from itertools import chain
from ragas.evaluation import evaluate, aevaluate
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from flotorch_eval.llm_eval.core.base_evaluator import BaseEvaluator
from flotorch_eval.llm_eval.core.schemas import EvaluationItem
from flotorch_eval.llm_eval.metrics.ragas_metrics.ragas_metrics import RagasEvaluationMetrics
from flotorch_eval.llm_eval.metrics.ragas_metrics.metric_keys import MetricKey

# Default constants
DEFAULT_TIMEOUT_SECONDS = 180.0
DEFAULT_MAX_RETRIES = 10

class RagasEvaluator(BaseEvaluator):
    """
    Evaluator that uses RAGAS metrics to score RAG-based QA performance.
    
    This evaluator computes both aggregated metrics (averaged across all questions) and
    question-level metrics (scores for each individual question) to provide comprehensive
    evaluation results.

    Args:
        base_url: Base URL for the Flotorch gateway API.
        api_key: API key for authentication.
        embedding_model: The embedding model to be used by RAGAS metrics
            (wrapped in LangchainEmbeddingsWrapper).
        inferencer_model: The LLM to be used by RAGAS metrics (wrapped in LangchainLLMWrapper).
        metric_args: Optional configuration for metrics requiring per-instance arguments.

            Example:
            {
                MetricKey.ASPECT_CRITIC: {
                    "maliciousness": {
                        "name": "maliciousness",
                        "definition": "Is the response harmful?"
                    },
                    "bias": {
                        "name": "bias",
                        "definition": "Is the response biased or discriminatory?"
                    }
                }
            }
    
    The evaluate() method returns:
        - Aggregated metrics: Dictionary with metric names as keys and averaged scores as values
        - Question-level results: List of dictionaries, each containing question details and
          per-question metric scores (accessible via '_question_level_results' key)
    """
    def __init__(
        self,
        base_url: str,
        api_key: str,
        embedding_model: str,
        inferencer_model: str,
        metric_args: Optional[
            Dict[Union[str, MetricKey], Dict[str, Dict[str, str]]]
        ] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        base_url = base_url + "/openai/v1"
        self._configure_models(
            base_url=base_url,
            api_key=api_key,
            embedding_model=embedding_model,
            inferencer_model=inferencer_model
        )
        self.metric_args = metric_args
        self.timeout = timeout
        self.max_retries = max_retries

        RagasEvaluationMetrics.initialize_metrics(
            llm=self.llm_model,
            embeddings=self.embedding_model,
            metric_args=self.metric_args
        )

    def _configure_models(
        self,
        base_url: str,
        api_key: str,
        embedding_model: str=None,
        inferencer_model: str=None
    ) -> None:
        """
        Configure the models for the RagasEvaluator.
        """
        # If both embedding_model and inferencer_model are None, raise an error
        if embedding_model is None and inferencer_model is None:
            raise ValueError("Either embedding_model or inferencer_model must be provided")

        # If inferencer_model is provided, configure the inferencer model
        if inferencer_model is not None:
            inferencer_llm_args = {
                "openai_api_base": base_url,
                "openai_api_key": api_key,
                "model": inferencer_model,
            }
            llm = ChatOpenAI(**inferencer_llm_args)

             # bypassing n as gateway currently does not support it.
            self.llm_model = LangchainLLMWrapper(llm, bypass_n=True)

        # If embedding_model is provided, configure the embedding model
        if embedding_model is not None:
            embedding_args = {
                "openai_api_base": base_url,
                "openai_api_key": api_key,
                "model": embedding_model,
                "check_embedding_ctx_length": False
            }
            embeddings = OpenAIEmbeddings(**embedding_args)
            self.embedding_model = LangchainEmbeddingsWrapper(embeddings=embeddings)

    def _resolve_metrics(
        self, metrics: Optional[List[MetricKey]]
    ) -> List[Any]:
        """
        Resolve metrics to use and convert them to Ragas metric objects.
        
        Args:
            metrics: Optional list of MetricKey enums provided by caller
            
        Returns:
            List of Ragas metric objects
            
        Raises:
            ValueError: If a metric is not a Ragas metric or not initialized
        """
        if metrics is None:
            # Get all registered Ragas metrics as MetricKey enums
            registered_metric_keys = RagasEvaluationMetrics.registered_metrics()
            # Filter to only include metrics that are actually initialized
            available_metric_strings = RagasEvaluationMetrics.available_metrics()
            metrics = [
                metric_key for metric_key in registered_metric_keys
                if metric_key.value in available_metric_strings
            ]
        else:
            # Validate that all metrics are Ragas metrics and initialized
            registered_metric_keys = RagasEvaluationMetrics.registered_metrics()
            available_metric_strings = RagasEvaluationMetrics.available_metrics()
            
            # Check for non-Ragas metrics first
            non_ragas_metrics = [
                metric for metric in metrics
                if metric not in registered_metric_keys
            ]
            if non_ragas_metrics:
                metric_names = [m.value for m in non_ragas_metrics]
                raise ValueError(
                    f"Metrics {metric_names} are not Ragas metrics. "
                    "Use the 'auto' evaluation engine to automatically route metrics to the correct engine, "
                    "or use only Ragas metrics with the 'ragas' engine."
                )
            
            # Validate that all Ragas metrics are initialized
            for metric in metrics:
                if metric.value not in available_metric_strings:
                    raise ValueError(
                        f"Metric '{metric.value}' is not initialized for the 'ragas' evaluation engine. "
                        "Make sure to call `initialize_metrics()` before evaluation, "
                        "or verify that you're using the correct evaluation engine."
                    )

        selected_metrics = list(chain.from_iterable(
            RagasEvaluationMetrics.get_metric(m).values() for m in metrics
        ))
        return selected_metrics

    def _configure_run(
        self,
        max_concurrent: int,
        timeout: Optional[int],
        max_retries: Optional[int],
    ) -> RunConfig:
        """
        Build a RunConfig with provided overrides and apply it to the LLM wrapper.
        """
        effective_timeout = timeout if timeout is not None else self.timeout
        effective_max_retries = max_retries if max_retries is not None else self.max_retries

        run_config = RunConfig(
            max_workers=max_concurrent,
            timeout=effective_timeout,
            max_retries=effective_max_retries,
        )

        if self.llm_model is not None:
            self.llm_model.set_run_config(run_config)

        return run_config

    def _prepare_dataset(self, data: List[EvaluationItem]) -> EvaluationDataset:
        """
        Convert EvaluationItems to Ragas EvaluationDataset.
        
        Args:
            data: List of EvaluationItems to convert
            
        Returns:
            EvaluationDataset for Ragas evaluation
        """
        answer_samples = []
        for item in data:
            sample_params = {
                "user_input": item.question,
                "response": item.generated_answer,
                "reference": item.expected_answer,
                "retrieved_contexts": item.context
            }
            answer_samples.append(SingleTurnSample(**sample_params))

        return EvaluationDataset(answer_samples)

    def _round_results(self, results_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Round result values to 2 decimal places.
        
        Args:
            results_dict: Dictionary of evaluation results
            
        Returns:
            Dictionary with rounded values
        """
        return {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in results_dict.items()}

    def _extract_question_level_results(
        self, result: Any, data: List[EvaluationItem]
    ) -> List[Dict[str, Any]]:
        """
        Extract question-level results from Ragas evaluation result.
        
        Args:
            result: Ragas evaluation result object
            data: Original list of EvaluationItem objects
            
        Returns:
            List of question-level result dictionaries
        """
        question_level_results = []
        results_dict = result._repr_dict
        
        for i, item in enumerate(data):
            question_result = {
                "question": item.question,
                "generated_answer": item.generated_answer,
                "expected_answer": item.expected_answer,
                "context": item.context,
                "metrics": {}
            }
            # Add metric scores for this question
            if hasattr(result, 'scores') and i < len(result.scores):
                for metric_name in results_dict.keys():
                    if metric_name in result.scores[i]:
                        score = result.scores[i][metric_name]
                        question_result["metrics"][metric_name] = (
                            round(score, 2) if isinstance(score, (int, float)) else score
                        )
            
            question_level_results.append(question_result)
        
        return question_level_results

    def evaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None,
        max_concurrent: int = 5,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the data using Ragas metrics.
        
        Args:
            data: List of EvaluationItems to evaluate
            metrics: Optional list of metrics to use. If None, uses all available metrics.
            max_concurrent: Maximum number of concurrent workers (RunConfig.max_workers).
            timeout: Timeout in seconds for each evaluation task. If None, uses instance default.
            max_retries: Maximum number of retry attempts. If None, uses instance default.
            
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
        selected_metrics = self._resolve_metrics(metrics)
        evaluation_dataset = self._prepare_dataset(data)

        run_config = self._configure_run(
            max_concurrent=max_concurrent,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Pass llm, embeddings, and run_config explicitly   
        result = evaluate(
            evaluation_dataset, 
            selected_metrics,
            llm=self.llm_model,
            embeddings=self.embedding_model,
            run_config=run_config,
        )
        rounded_results = self._round_results(result._repr_dict)
        
        # Extract question-level results
        question_level_results = self._extract_question_level_results(result, data)
        rounded_results["_question_level_results"] = question_level_results
        
        return rounded_results

    async def aevaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None,
        max_concurrent: int = 5,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously evaluate the data using Ragas native aevaluate with concurrent processing.
        
        Args:
            data: The data to evaluate.
            metrics: Optional list of MetricKey enums to evaluate. If None, uses all available metrics.
            max_concurrent: Maximum number of concurrent workers.
                This maps to RunConfig.max_workers in Ragas.
            timeout: Timeout in seconds for each evaluation task. If None, uses instance default.
            max_retries: Maximum number of retry attempts. If None, uses instance default.
        
        Returns:
            Dictionary containing:
            - Aggregated metrics (averaged across all questions): metric names as keys, 
              averaged scores as values
            - Question-level results: stored under '_question_level_results' key as a list of dicts
        """
        selected_metrics = self._resolve_metrics(metrics)
        evaluation_dataset = self._prepare_dataset(data)

        # Configure RunConfig consistently with sync evaluate
        run_config = self._configure_run(
            max_concurrent=max_concurrent,
            timeout=timeout,
            max_retries=max_retries,
        )
    
        result = await aevaluate(
            dataset=evaluation_dataset,
            metrics=selected_metrics,
            llm=self.llm_model,
            embeddings=self.embedding_model,
            run_config=run_config,
        )

        rounded_results = self._round_results(result._repr_dict)
        
        # Extract question-level results
        question_level_results = self._extract_question_level_results(result, data)
        rounded_results["_question_level_results"] = question_level_results

        return rounded_results
