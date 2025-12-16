"""
Base Evaluator Module.

This module defines the abstract base class for evaluation implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from flotorch_eval.llm_eval.core.schemas import EvaluationItem
from flotorch_eval.llm_eval.metrics.ragas_metrics.metric_keys import MetricKey

class BaseEvaluator(ABC):
    """
    Abstract base class for evaluation modules.
    """

    @abstractmethod
    def evaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the model output against the expected answers.

        Args:
            data (List[EvaluationItem]): List of evaluation inputs.
            metrics (Optional[List[MetricKey]]): The metrics to use for evaluation.

        Returns:
            Dict[str, Any]: Dictionary of evaluation results.
        """
        pass

    async def aevaluate(
        self,
        data: List[EvaluationItem],
        metrics: Optional[List[MetricKey]] = None,
        max_concurrent: int = 5,
        throttle: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously evaluate the model output against the expected answers.
        Default implementation falls back to synchronous evaluate.
        Subclasses should override for async support.

        Args:
            data (List[EvaluationItem]): List of evaluation inputs.
            metrics (Optional[List[MetricKey]]): The metrics to use for evaluation.
            max_concurrent (int): Maximum number of concurrent evaluation tasks.
            throttle (Optional[int]): Throttle value for async evaluation (delay between requests).
                Not used in default implementation, but available for subclasses.
            max_retries (Optional[int]): Maximum number of retry attempts.
                Not used in default implementation, but available for subclasses.

        Returns:
            Dict[str, Any]: Dictionary of evaluation results.
        """
        # Default implementation: fall back to sync evaluate
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.evaluate, data, metrics)
