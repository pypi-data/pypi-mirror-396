"""
Agent evaluation package.
"""

from flotorch_eval.agent_eval.core.schemas import (
    EvaluationResult,
    Message,
    MetricResult,
    Span,
    SpanEvent,
    ToolCall,
    Trajectory,
)
from flotorch_eval.agent_eval.core.converter import TraceConverter
from flotorch_eval.agent_eval.core.client import AgentEvaluator
from flotorch_eval.agent_eval.metrics.llm_evaluators import LLMBaseEval
from flotorch_eval.agent_eval.metrics.llm_evaluators import (
    TrajectoryEvalWithLLM,
    TrajectoryEvalWithLLMWithReference,
)

from flotorch_eval.common.display_utils import display_agent_evaluation_results

__all__ = [
    "AgentEvaluator",
    "LLMBaseEval",
    "EvaluationResult",
    "Message",
    "MetricResult",
    "Span",
    "SpanEvent",
    "ToolCall",
    "Trajectory",
    "TraceConverter",
    "TrajectoryEvalWithLLM",
    "TrajectoryEvalWithLLMWithReference",
    "display_agent_evaluation_results",
]