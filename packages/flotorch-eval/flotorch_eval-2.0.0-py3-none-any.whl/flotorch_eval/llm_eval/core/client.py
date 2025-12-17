"""
LLM Evaluation Client Module.

This module provides the main client interface for evaluating LLM-based metrics
using different evaluation engines (Ragas, DeepEval, Gateway).
"""
from typing import List, Optional, Dict, Union, Any, Tuple
from flotorch_eval.llm_eval.metrics.ragas_metrics.metric_keys import MetricKey
from flotorch_eval.llm_eval.core.schemas import EvaluationItem
from flotorch_eval.llm_eval.core.ragas_evaluator import RagasEvaluator
from flotorch_eval.llm_eval.metrics.ragas_metrics.ragas_metrics import RagasEvaluationMetrics
from flotorch_eval.llm_eval.core.gateway_evaluator import GatewayEvaluator
from flotorch_eval.llm_eval.metrics.gateway_metrics.gateway_metrics import GatewayMetrics
from flotorch_eval.llm_eval.core.deepeval_evaluator import DeepEvalEvaluator
from flotorch_eval.llm_eval.metrics.deepeval_metrics.deepeval_metrics import (
    DeepEvalEvaluationMetrics
)

class LLMEvaluator:
    """
    Client for evaluating LLM-based metrics.
    """
    _ENGINES = {
        'ragas': {
            'metrics_class': RagasEvaluationMetrics,
            'priority': 1,
        },
        'deepeval': {
            'metrics_class': DeepEvalEvaluationMetrics,
            'priority': 2,
        }
    }

    def __init__(
        self,
        api_key: str,
        base_url: str,
        embedding_model: str,
        inferencer_model: str,
        evaluation_engine='auto',
        metrics: Optional[List[MetricKey]] = None,
        metric_configs: Optional[
            Dict[Union[str, MetricKey], Dict[str, Dict[str, str]]]
        ] = None,
        max_concurrent: int = 5,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize the LLMEvaluator.

        Args:
            api_key (str): API key for authentication.
            base_url (str): Base URL for the evaluation service.
            evaluation_engine (str): The evaluation engine to use.
                Options: 'auto' (default), 'ragas', 'deepeval'
                - 'auto': Automatically routes metrics to the appropriate engine.
                  Ragas has priority for overlapping metrics.
                - Specific engine: Use only that evaluation engine
            embedding_model (str): The embedding model to use.
            inferencer_model (str): The inferencer model to use.
            metrics (Optional[List[MetricKey]]): Default metrics to use for evaluation.
                If None and engine is 'auto', all metrics from all engines will be used.
                If None with specific engine, all metrics from that engine will be used.
            metric_configs (Optional[Dict]): Configuration for metrics that require
                additional parameters (e.g., AspectCritic). Metrics requiring configs
                will be skipped if not provided.
                Example:
                {
                    MetricKey.ASPECT_CRITIC: {
                        'maliciousness': {
                            'name': 'maliciousness',
                            'definition': 'Is the response harmful?'
                        }
                    }
                }
            max_concurrent (int): Maximum number of concurrent evaluation tasks for
                async evaluation. Default is 5. Only used with aevaluate() method.
            max_retries (int): Maximum number of retry attempts for API calls.
                Default is 3.
            **kwargs: Additional keyword arguments.
                throttle (int): Delay between requests for async evaluation (deepeval only).
                    Default: 3.
                deepeval_timeout (float): Per-task timeout in seconds for deepeval.
                    Default: 300.0.
                ragas_timeout (float): Per-task timeout in seconds for ragas.
                    Default: 180.0.
        Raises:
            ValueError: If the evaluation engine is not valid.
        """
        if evaluation_engine != 'auto' and evaluation_engine not in self._ENGINES:
            available = ', '.join(self._ENGINES.keys())
            raise ValueError(
                f"Evaluation engine '{evaluation_engine}' not supported. "
                f"Available: {available}, or 'auto'"
            )

        self.inferencer_model = inferencer_model
        self.embedding_model = embedding_model
        self.api_key = api_key
        self.base_url = base_url
        self.evaluation_engine = evaluation_engine
        self.metrics = metrics
        self.metric_configs = metric_configs
        self.max_concurrent = self._ensure_positive(
            max_concurrent, default=1, caster=int, minimum=1
        )
        self.max_retries = self._ensure_positive(
            max_retries, default=1, caster=int, minimum=1
        )
        self.throttle = self._ensure_positive(
            kwargs.get('throttle', 3), default=3, caster=int, minimum=1
        )
        self.deepeval_timeout = self._ensure_positive(
            kwargs.get('deepeval_timeout', 300.0), default=300.0, caster=float, minimum=1.0
        )
        self.ragas_timeout = self._ensure_positive(
            kwargs.get('ragas_timeout', 180.0), default=180.0, caster=float, minimum=1.0
        )

    def set_metrics(self, metrics: List[MetricKey]) -> None:
        """
        Update the default metrics to use for evaluation.

        Args:
            metrics (List[MetricKey]): The new default metrics.
        """
        self.metrics = metrics

    def set_metric_configs(
        self,
        metric_configs: Dict[Union[str, MetricKey], Dict[str, Dict[str, str]]]
    ) -> None:
        """
        Update the metric configurations.

        Args:
            metric_configs (Dict): Configuration for metrics that require
                additional parameters.
        """
        self.metric_configs = metric_configs

    def _get_engine_for_metric(self, metric: MetricKey) -> str:
        """
        Determine which engine supports a metric (respects priority).
        
        Args:
            metric: The metric to check
            
        Returns:
            Engine name
            
        Raises:
            ValueError: If metric not supported by any engine
        """
        # Find all engines that support this metric, sorted by priority
        supporting_engines = []
        for engine_name, engine_info in self._ENGINES.items():
            if metric in engine_info['metrics_class'].registered_metrics():
                supporting_engines.append((engine_info['priority'], engine_name))

        if not supporting_engines:
            raise ValueError(f"Metric '{metric}' not supported by any engine")

        # Return highest priority engine
        supporting_engines.sort()
        return supporting_engines[0][1]

    def _split_metrics_by_engine(self, metrics: List[MetricKey]) -> Dict[str, List[MetricKey]]:
        """
        Split metrics by engine based on priority.
        
        Args:
            metrics: List of metrics to split
            
        Returns:
            Dict mapping engine names to their metrics
        """
        engine_metrics = {name: [] for name in self._ENGINES}

        for metric in metrics:
            engine = self._get_engine_for_metric(metric)
            engine_metrics[engine].append(metric)

        # Remove empty entries
        return {k: v for k, v in engine_metrics.items() if v}

    def _get_all_metrics(self) -> List[MetricKey]:
        """
        Get all unique metrics from all engines (respects priority).
        
        Returns:
            List of all unique metrics
        """
        # Sort engines by priority
        sorted_engines = sorted(
            self._ENGINES.items(),
            key=lambda x: x[1]['priority']
        )

        seen = set()
        all_metrics = []

        for _, engine_info in sorted_engines:
            for metric in engine_info['metrics_class'].registered_metrics():
                if metric not in seen:
                    seen.add(metric)
                    all_metrics.append(metric)

        return all_metrics

    @staticmethod
    def _ensure_positive(
        value: Optional[Any],
        default: Any,
        caster,
        minimum: Union[int, float] = 0
    ) -> Union[int, float]:
        """
        Convert value with caster, ensure it is non-negative, and clamp to minimum.
        Falls back to default on invalid inputs.
        """
        try:
            val = caster(value) if value is not None else caster(default)
            val = abs(val)
            return val if val >= minimum else minimum
        except (TypeError, ValueError):
            val = abs(caster(default))
            return val if val >= minimum else minimum

    def _create_evaluator(self, engine_name: str):
        """Create evaluator instance for the given engine."""
        if engine_name == 'ragas':
            return RagasEvaluator(
                base_url=self.base_url,
                api_key=self.api_key,
                embedding_model=self.embedding_model,
                inferencer_model=self.inferencer_model,
                metric_args=self.metric_configs,
                timeout=self.ragas_timeout,  # Ragas default timeout
                max_retries=self.max_retries
            )
        elif engine_name == 'deepeval':
            return DeepEvalEvaluator(
                evaluator_llm=self.inferencer_model,
                api_key=self.api_key,
                base_url=self.base_url,
                metric_args=self.metric_configs,
                max_concurrent=self.max_concurrent,
                throttle=self.throttle,
                max_retries=self.max_retries,
                per_task_timeout_seconds=self.deepeval_timeout,
            )
        else:
            raise ValueError(f"Unknown engine: {engine_name}")

    def _validate_models(self) -> None:
        """Validate that required models are set."""
        if self.inferencer_model is None or self.embedding_model is None:
            raise ValueError("LLM and embedding model must be set to use evaluation")

    def _resolve_metrics(
        self, metrics: Optional[List[MetricKey]]
    ) -> Tuple[List[MetricKey], Dict[str, List[MetricKey]]]:
        """
        Resolve metrics to use and split them by engine.
        
        Args:
            metrics: Optional list of metrics provided by caller
            
        Returns:
            Tuple of (metrics_to_use, metrics_by_engine)
            - metrics_to_use: The resolved list of metrics
            - metrics_by_engine: Dict mapping engine names to their metrics
        """
        # Use provided metrics, fall back to instance default
        metrics_to_use = metrics if metrics is not None else self.metrics

        # Handle auto mode
        if self.evaluation_engine == 'auto':
            # If no metrics specified, use all metrics from all engines
            if metrics_to_use is None:
                metrics_to_use = self._get_all_metrics()

            # Split metrics by engine based on priority
            metrics_by_engine = self._split_metrics_by_engine(metrics_to_use)
        else:
            # For specific engine mode, metrics_by_engine is not used
            # but we still need to return it for consistency
            metrics_by_engine = {}

        return metrics_to_use, metrics_by_engine

    def _get_gateway_metrics(self, data: List[EvaluationItem]) -> Optional[Dict[str, Any]]:
        """
        Get gateway metrics if metadata is present in the data.
        
        Args:
            data: The evaluation data
            
        Returns:
            Gateway metrics dict if metadata is present, None otherwise
        """
        if GatewayMetrics.has_metadata(data):
            gateway_evaluator = GatewayEvaluator()
            gateway_results = gateway_evaluator.evaluate(data)
            return gateway_results.get('gateway_metrics', {})
        return None

    def _merge_question_level_results(
        self, all_question_level_results: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge question-level results from multiple engines.
        
        Args:
            all_question_level_results: List of question-level result lists from each engine
            
        Returns:
            Merged list of question-level results
        """
        if not all_question_level_results:
            return []
        
        merged_results = []
        num_questions = len(all_question_level_results[0])
        
        for i in range(num_questions):
            merged_question = {
                "question": all_question_level_results[0][i]["question"],
                "generated_answer": all_question_level_results[0][i]["generated_answer"],
                "expected_answer": all_question_level_results[0][i]["expected_answer"],
                "context": all_question_level_results[0][i]["context"],
                "metrics": {}
            }
            # Merge metrics from all engines
            for engine_q_results in all_question_level_results:
                if i < len(engine_q_results):
                    merged_question["metrics"].update(engine_q_results[i]["metrics"])
            merged_results.append(merged_question)
        
        return merged_results

    def _combine_results(
        self, 
        evaluation_results: Dict[str, Any], 
        gateway_metrics: Optional[Dict[str, Any]] = None,
        question_level_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Combine evaluation results with gateway metrics and question-level results.
        
        Args:
            evaluation_results: Results from evaluation engines
            gateway_metrics: Optional gateway metrics
            question_level_results: Optional question-level results
            
        Returns:
            Combined results dictionary
        """
        combined_results = {
            "evaluation_metrics": evaluation_results,
        }
        if gateway_metrics:
            combined_results['gateway_metrics'] = gateway_metrics
        if question_level_results is not None:
            combined_results['question_level_results'] = question_level_results
        return combined_results

    async def _evaluate_engine_async(
        self,
        engine_name: str,
        data: List[EvaluationItem],
        metrics: List[MetricKey],
        max_concurrent: Optional[int] = None,
        throttle: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate data with a specific engine asynchronously.
        Uses async evaluation for engines that support it (ragas, deepeval),
        falls back to sync evaluation for others.
        
        Args:
            engine_name: Name of the engine to use
            data: The data to evaluate
            metrics: The metrics to use for evaluation
            max_concurrent: Maximum number of concurrent workers. If None, uses instance default.
            throttle: Throttle value for async evaluation. If None, uses instance default.
            max_retries: Maximum number of retry attempts. If None, uses instance default.
            
        Returns:
            Dictionary of evaluation results
        """
        evaluator = self._create_evaluator(engine_name)
        
        # Use provided parameters or fall back to instance defaults
        effective_max_concurrent = max_concurrent if max_concurrent is not None else self.max_concurrent
        effective_throttle = throttle if throttle is not None else self.throttle
        effective_max_retries = max_retries if max_retries is not None else self.max_retries
        
        # Check if engine supports async evaluation
        if engine_name == 'ragas':
            return await evaluator.aevaluate(
                data, 
                metrics, 
                max_concurrent=effective_max_concurrent,
                max_retries=effective_max_retries
            )
        elif engine_name == 'deepeval':
            return await evaluator.aevaluate(
                data, 
                metrics, 
                max_concurrent=effective_max_concurrent,
                throttle=effective_throttle,
                max_retries=effective_max_retries
            )
        else:
            # For other engines, fall back to sync evaluate
            return evaluator.evaluate(data, metrics)

    def evaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]]=None
    ) -> Dict[str, Any]:
        """
        Evaluate the data using the evaluation engine.

        Args:
            data (List[EvaluationItem]): The data to evaluate.
            metrics (Optional[List[MetricKey]]): The metrics to use for evaluation.
                If None, uses the default metrics set during initialization.
                If both are None:
                  - In 'auto' mode: all metrics from all engines will be used
                  - In specific engine mode: all metrics from that engine will be used

        Returns:
            Dict[str, Any]: The evaluation results. If metadata is present in 
                EvaluationItems, gateway_metrics will be automatically included.
        """
        self._validate_models()
        metrics_to_use, metrics_by_engine = self._resolve_metrics(metrics)

        results = {}
        question_level_results = None
        if self.evaluation_engine == 'auto':
            all_question_level_results = []

            # Evaluate with each engine that has metrics assigned
            for engine_name, engine_metrics in metrics_by_engine.items():
                evaluator = self._create_evaluator(engine_name)
                engine_results = evaluator.evaluate(data, engine_metrics)
                
                # Extract and store question-level results before updating
                engine_q_results = engine_results.pop("_question_level_results", None)
                if engine_q_results:
                    all_question_level_results.append(engine_q_results)
                
                results.update(engine_results)
            
            # Merge question-level results from multiple engines
            question_level_results = (
                self._merge_question_level_results(all_question_level_results)
                if all_question_level_results else None
            )

        else:
            # Use specific engine
            evaluator = self._create_evaluator(self.evaluation_engine)
            results = evaluator.evaluate(data, metrics_to_use)
            
            # Extract question-level results if present (from Ragas or DeepEval evaluators)
            question_level_results = results.pop("_question_level_results", None)
        
        # Automatically include gateway metrics if metadata is present
        gateway_metrics = self._get_gateway_metrics(data)
        
        return self._combine_results(
            evaluation_results=results,
            gateway_metrics=gateway_metrics,
            question_level_results=question_level_results
        )

    async def aevaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None,
        max_concurrent: Optional[int] = None,
        throttle: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously evaluate the data using the evaluation engine with concurrent processing.

        Args:
            data (List[EvaluationItem]): The data to evaluate.
            metrics (Optional[List[MetricKey]]): The metrics to use for evaluation.
                If None, uses the default metrics set during initialization.
                If both are None:
                  - In 'auto' mode: all metrics from all engines will be used
                  - In specific engine mode: all metrics from that engine will be used
            max_concurrent (Optional[int]): Maximum number of concurrent workers.
                If None, uses the instance's max_concurrent.
            throttle (Optional[int]): Throttle value for async evaluation.
                If None, uses the instance's throttle. Only used with deepeval engine.
            max_retries (Optional[int]): Maximum number of retry attempts.
                If None, uses the instance's max_retries.

        Returns:
            Dict[str, Any]: The evaluation results with averaged scores and question-level results.
                If metadata is present in EvaluationItems, gateway_metrics will be automatically included.
        """
        self._validate_models()
        metrics_to_use, metrics_by_engine = self._resolve_metrics(metrics)

        results = {}
        question_level_results = None
        all_question_level_results = []
        
        if self.evaluation_engine == 'auto':
            # Evaluate with each engine that has metrics assigned
            for engine_name, engine_metrics in metrics_by_engine.items():
                engine_results = await self._evaluate_engine_async(
                    engine_name, data, engine_metrics,
                    max_concurrent=max_concurrent,
                    throttle=throttle,
                    max_retries=max_retries
                )
                
                # Extract and store question-level results before updating
                engine_q_results = engine_results.pop("_question_level_results", None)
                if engine_q_results:
                    all_question_level_results.append(engine_q_results)
                
                results.update(engine_results)
            
            # Merge question-level results from multiple engines
            question_level_results = (
                self._merge_question_level_results(all_question_level_results)
                if all_question_level_results else None
            )
        else:
            # Use specific engine
            results = await self._evaluate_engine_async(
                self.evaluation_engine, data, metrics_to_use,
                max_concurrent=max_concurrent,
                throttle=throttle,
                max_retries=max_retries
            )
            
            # Extract question-level results if present (from Ragas or DeepEval evaluators)
            question_level_results = results.pop("_question_level_results", None)
        
        # Automatically include gateway metrics if metadata is present
        gateway_metrics = self._get_gateway_metrics(data)
        
        return self._combine_results(
            evaluation_results=results,
            gateway_metrics=gateway_metrics,
            question_level_results=question_level_results
        )
