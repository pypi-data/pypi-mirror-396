"""
Main entry point for the ``pytest-texts-score`` public API.

This module exposes the primary functions for text-based scoring and assertions
within pytest. It includes functions for single-run evaluations
(``texts_expect_*``) and multi-run, aggregated evaluations (``texts_agg_*``) for
metrics like F1, precision, and recall.

It also provides aliases like "completeness" for precision and "correctness"
for recall, which can be more intuitive in certain testing contexts.
"""

from pytest_texts_score.api import (
    texts_agg_f1_max,
    texts_agg_f1_mean,
    texts_agg_f1_median,
    texts_agg_f1_min,
    texts_agg_precision_max,
    texts_agg_precision_mean,
    texts_agg_precision_median,
    texts_agg_precision_min,
    texts_agg_recall_max,
    texts_agg_recall_mean,
    texts_agg_recall_median,
    texts_agg_recall_min,
    texts_expect_f1_equal,
    texts_expect_f1_range,
    texts_expect_precision_equal,
    texts_expect_precision_range,
    texts_expect_recall_equal,
    texts_expect_recall_range,
)
from pytest_texts_score.api_wrappers import (
    texts_agg_f1_average,
    texts_agg_completeness_mean,
    texts_agg_completeness_average,
    texts_agg_completeness_max,
    texts_agg_completeness_median,
    texts_agg_completeness_min,
    texts_agg_correctness_average,
    texts_agg_correctness_max,
    texts_agg_correctness_mean,
    texts_agg_correctness_median,
    texts_agg_correctness_min,
    texts_agg_precision_average,
    texts_agg_recall_average,
    texts_expect_completeness_equal,
    texts_expect_completeness_range,
    texts_expect_correctness_equal,
    texts_expect_correctness_range,
)

__all__ = [
    "texts_agg_completeness_average",
    "texts_agg_completeness_mean",
    "texts_agg_completeness_max",
    "texts_agg_completeness_median",
    "texts_agg_completeness_min",
    "texts_agg_correctness_average",
    "texts_agg_correctness_max",
    "texts_agg_correctness_mean",
    "texts_agg_correctness_median",
    "texts_agg_correctness_min",
    "texts_agg_f1_average",
    "texts_agg_f1_max",
    "texts_agg_f1_mean",
    "texts_agg_f1_median",
    "texts_agg_f1_min",
    "texts_agg_precision_average",
    "texts_agg_precision_max",
    "texts_agg_precision_mean",
    "texts_agg_precision_median",
    "texts_agg_precision_min",
    "texts_agg_recall_average",
    "texts_agg_recall_max",
    "texts_agg_recall_mean",
    "texts_agg_recall_median",
    "texts_agg_recall_min",
    "texts_expect_completeness_equal",
    "texts_expect_completeness_range",
    "texts_expect_correctness_equal",
    "texts_expect_correctness_range",
    "texts_expect_f1_equal",
    "texts_expect_f1_range",
    "texts_expect_precision_equal",
    "texts_expect_precision_range",
    "texts_expect_recall_equal",
    "texts_expect_recall_range",
]
