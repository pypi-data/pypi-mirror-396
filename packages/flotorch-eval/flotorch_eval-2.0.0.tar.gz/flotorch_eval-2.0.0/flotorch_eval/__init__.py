"""
FlotorchEval - A comprehensive evaluation framework for AI systems.
"""

__version__ = "0.2.2"

from flotorch_eval.common.metrics import BaseMetric, MetricConfig
from flotorch_eval.common.display_utils import (
    display_agent_evaluation_results,
    display_llm_evaluation_results,
)

__all__ = [
    "BaseMetric",
    "MetricConfig",
    "display_agent_evaluation_results",
    "display_llm_evaluation_results",
]
