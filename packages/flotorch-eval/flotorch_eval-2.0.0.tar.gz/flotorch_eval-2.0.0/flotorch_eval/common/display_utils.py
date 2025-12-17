"""
Display utilities for evaluation results.

This module provides functions to display evaluation results in a clean,
formatted way for both agent evaluation and LLM evaluation.
"""

import pandas as pd
from typing import List, Any, Dict
import textwrap

# Try to import IPython display, fallback to None if not available
try:
    from IPython.display import display
    _HAS_IPYTHON = True
except ImportError:
    _HAS_IPYTHON = False
    display = None


def _is_notebook() -> bool:
    """Check if running in a Jupyter notebook."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None and hasattr(get_ipython(), 'kernel')
    except ImportError:
        return False


def _format_latency_breakdown_recursive(items: List[Dict], level: int) -> List[str]:
    """A helper function to recursively format the nested latency breakdown."""
    lines = []
    
    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * level
    for item in items:
        step_name = item.get('step_name', 'Unknown Step')
        latency = item.get('latency_ms', 'N/A')
        lines.append(f"{indent}- {step_name}: {latency} ms")
        
        # If there are children, recurse
        if item.get('children'):
            lines.extend(_format_latency_breakdown_recursive(item['children'], level + 1))
    return lines


def display_agent_evaluation_results(results: Any) -> None:
    """
    Displays agent evaluation results as a clean, styled HTML table,
    correctly rendering newlines and hierarchical indentation in the details column.
    
    This function is designed for agent evaluation results (EvaluationResult objects).
    
    Args:
        results: EvaluationResult object with a 'scores' attribute containing metric results
    """
    if not results or not getattr(results, 'scores', None):
        print("No evaluation results were generated.")
        return

    data = []
    for metric in results.scores:
        details_dict = metric.details.copy() if metric.details else {}
        display_parts = []

        if 'error' in details_dict:
            error_message = f"Error: {details_dict.pop('error')}"
            display_parts.append(textwrap.fill(error_message, width=80))

        elif 'comment' in details_dict:
            comment = details_dict.pop('comment')
            display_parts.append(textwrap.fill(comment, width=80))

        elif 'total_latency_ms' in details_dict and 'latency_breakdown' in details_dict:
            latency_summary = []
            
            breakdown_data = details_dict.pop('latency_breakdown', [])
            total_latency = details_dict.pop('total_latency_ms')
            avg_latency = details_dict.pop('average_step_latency_ms', None)
            
            latency_summary.append(f"Total Latency (Root Steps): {total_latency} ms")
            if avg_latency is not None:
                latency_summary.append(f"Average Root Step Latency: {avg_latency} ms")
            
            if breakdown_data:
                latency_summary.append("Latency Breakdown:")
                formatted_lines = _format_latency_breakdown_recursive(breakdown_data, level=1)
                latency_summary.extend(formatted_lines)
            
            display_parts.append("\n".join(latency_summary))
        
        other_details = []
        if details_dict:
            if 'cost_breakdown' in details_dict and isinstance(details_dict['cost_breakdown'], list):
                details_dict['cost_breakdown'] = "\n" + "\n".join([f"    - {item}" for item in details_dict['cost_breakdown']])
            for key, value in details_dict.items():
                other_details.append(f"- {key}: {value}")

        if other_details:
            if display_parts:
                display_parts.append("\n" + "-"*20)
            display_parts.append("\n".join(other_details))
        
        score_display = f"{metric.score:.2f}" if isinstance(metric.score, (int, float)) else "N/A"

        data.append({
            "Metric": metric.name,
            "Score": score_display,
            "Details": "\n".join(display_parts)
        })

    df = pd.DataFrame(data)
    pd.set_option('display.max_colwidth', None)

    if _is_notebook() and _HAS_IPYTHON:
        styled_df = df.style.set_properties(
            subset=['Details'],
            **{'white-space': 'pre-wrap', 'text-align': 'left'}
        ).set_table_styles(
            [dict(selector="th", props=[("text-align", "left")])]
        ).hide(axis="index")
        display(styled_df)
    else:
        # Terminal mode: print as plain text table
        pd.set_option('display.max_colwidth', 100)
        print(df.to_string(index=False))


def display_llm_evaluation_results(eval_result: Dict[str, Any], show_question_details: bool = True, show_gateway_metrics: bool = True) -> None:
    """
    Displays LLM evaluation metric results in a clean tabular format.
    
    This function is designed for LLM evaluation results (dictionaries with evaluation metrics).
    
    Args:
        eval_result: Dictionary containing evaluation results with keys:
            - 'evaluation_metrics': Dict of metric names to aggregated scores
            - 'question_level_results': List of dicts with per-question metrics
            - 'gateway_metrics': Optional dict with latency, cost, token info
        show_question_details: If True, displays per-question metric breakdown
        show_gateway_metrics: If True, displays gateway metrics (latency, cost, tokens)
    """
    if not eval_result:
        print("No evaluation results provided.")
        return
    
    # Display aggregated metrics
    evaluation_metrics = eval_result.get('evaluation_metrics', {})
    if evaluation_metrics:
        print("=" * 80)
        print("AGGREGATED EVALUATION METRICS")
        print("=" * 80)
        
        metrics_data = []
        for metric_name, score in sorted(evaluation_metrics.items()):
            score_str = f"{score:.4f}" if isinstance(score, (int, float)) else str(score)
            metrics_data.append({
                "Metric": metric_name.replace("_", " ").title(),
                "Score": score_str
            })
        
        df_agg = pd.DataFrame(metrics_data)
        
        if _is_notebook() and _HAS_IPYTHON:
            styled_agg = df_agg.style.set_properties(
                **{'text-align': 'left'}
            ).set_table_styles([
                dict(selector="th", props=[("text-align", "left"), ("font-weight", "bold")]),
                dict(selector="td", props=[("padding", "8px")])
            ]).hide(axis="index")
            display(styled_agg)
        else:
            # Terminal mode: print as plain text table
            print(df_agg.to_string(index=False))
        print()
    
    # Display per-question metrics
    question_results = eval_result.get('question_level_results', [])
    if question_results and show_question_details:
        print("=" * 80)
        print("PER-QUESTION METRIC RESULTS")
        print("=" * 80)
        
        # Collect all unique metric names across all questions
        all_metric_names = set()
        for result in question_results:
            metrics = result.get('metrics', {})
            all_metric_names.update(metrics.keys())
        
        # Create table data
        question_data = []
        for idx, result in enumerate(question_results, 1):
            question = result.get('question', 'N/A')
            # Truncate long questions for display
            question_display = question[:80] + "..." if len(question) > 80 else question
            
            row = {"Question #": idx, "Question": question_display}
            
            # Add metric scores
            metrics = result.get('metrics', {})
            for metric_name in sorted(all_metric_names):
                score = metrics.get(metric_name)
                if score is not None:
                    score_str = f"{score:.4f}" if isinstance(score, (int, float)) else str(score)
                else:
                    score_str = "N/A"
                row[metric_name.replace("_", " ").title()] = score_str
            
            question_data.append(row)
        
        if question_data:
            df_questions = pd.DataFrame(question_data)
            
            if _is_notebook() and _HAS_IPYTHON:
                styled_questions = df_questions.style.set_properties(
                    **{'text-align': 'left'}
                ).set_properties(
                    subset=['Question'],
                    **{'white-space': 'pre-wrap', 'max-width': '400px'}
                ).set_table_styles([
                    dict(selector="th", props=[("text-align", "left"), ("font-weight", "bold")]),
                    dict(selector="td", props=[("padding", "8px")])
                ]).hide(axis="index")
                display(styled_questions)
            else:
                # Terminal mode: print as plain text table
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', 80)
                print(df_questions.to_string(index=False))
            print()
    
    # Display gateway metrics (latency, cost, tokens)
    gateway_metrics = eval_result.get('gateway_metrics', {})
    if gateway_metrics and show_gateway_metrics:
        print("=" * 80)
        print("GATEWAY METRICS (Latency, Cost, Tokens)")
        print("=" * 80)
        
        gateway_data = []
        
        # Format latency metrics
        if 'total_latency_ms' in gateway_metrics:
            gateway_data.append({
                "Metric": "Total Latency",
                "Value": f"{gateway_metrics['total_latency_ms']:.2f} ms"
            })
        if 'average_latency_ms' in gateway_metrics:
            gateway_data.append({
                "Metric": "Average Latency",
                "Value": f"{gateway_metrics['average_latency_ms']:.2f} ms"
            })
        
        # Format cost metrics
        if 'total_cost' in gateway_metrics:
            gateway_data.append({
                "Metric": "Total Cost",
                "Value": f"${gateway_metrics['total_cost']:.6f}"
            })
        if 'average_cost' in gateway_metrics:
            gateway_data.append({
                "Metric": "Average Cost",
                "Value": f"${gateway_metrics['average_cost']:.6f}"
            })
        
        # Format token metrics
        if 'total_tokens' in gateway_metrics:
            gateway_data.append({
                "Metric": "Total Tokens",
                "Value": f"{gateway_metrics['total_tokens']:,}"
            })
        
        # Format item counts
        if 'total_items' in gateway_metrics:
            gateway_data.append({
                "Metric": "Total Items",
                "Value": f"{gateway_metrics['total_items']}"
            })
        if 'items_with_metadata' in gateway_metrics:
            gateway_data.append({
                "Metric": "Items with Metadata",
                "Value": f"{gateway_metrics['items_with_metadata']}"
            })
        
        if gateway_data:
            df_gateway = pd.DataFrame(gateway_data)
            
            if _is_notebook() and _HAS_IPYTHON:
                styled_gateway = df_gateway.style.set_properties(
                    **{'text-align': 'left'}
                ).set_table_styles([
                    dict(selector="th", props=[("text-align", "left"), ("font-weight", "bold")]),
                    dict(selector="td", props=[("padding", "8px")])
                ]).hide(axis="index")
                display(styled_gateway)
            else:
                # Terminal mode: print as plain text table
                print(df_gateway.to_string(index=False))
            print()

