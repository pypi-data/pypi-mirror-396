"""
This module provides wrapper functions for the public API, offering alternative
names for existing functionality. For example, functions using 'mean' are
aliased with 'average'.
"""
from pytest_texts_score.api import (
    texts_agg_f1_mean,
    texts_agg_precision_max,
    texts_agg_precision_mean,
    texts_agg_precision_median,
    texts_agg_precision_min,
    texts_agg_recall_max,
    texts_agg_recall_mean,
    texts_agg_recall_median,
    texts_agg_recall_min,
    texts_expect_precision_equal,
    texts_expect_precision_range,
    texts_expect_recall_equal,
    texts_expect_recall_range,
)


def texts_agg_f1_average(expected: str,
                         given: str,
                         target: float,
                         max_delta: float = 0.1,
                         full_runs: int = 5,
                         each_question_runs: int = 1,
                         retry_on_error: bool = True) -> None:
    """Alias for texts_agg_f1_mean."""
    texts_agg_f1_mean(expected, given, target, max_delta, full_runs,
                      each_question_runs, retry_on_error)


def texts_agg_precision_average(expected: str,
                                given: str,
                                target: float,
                                max_delta: float = 0.1,
                                full_runs: int = 5,
                                each_question_runs: int = 1,
                                retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_mean."""
    texts_agg_precision_mean(expected, given, target, max_delta, full_runs,
                             each_question_runs, retry_on_error)


def texts_agg_recall_average(expected: str,
                             given: str,
                             target: float,
                             max_delta: float = 0.1,
                             full_runs: int = 5,
                             each_question_runs: int = 1,
                             retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_mean."""
    texts_agg_recall_mean(expected, given, target, max_delta, full_runs,
                          each_question_runs, retry_on_error)


# --- Completeness Wrappers (alias for Precision) ---


def texts_expect_completeness_equal(
    expected: str,
    given: str,
    target: float = 1.0,
    max_delta: float = 0.2,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """Alias for texts_expect_precision_equal."""
    texts_expect_precision_equal(expected, given, target, max_delta,
                                 skip_warnings, retry_on_error)


def texts_expect_completeness_range(
    expected: str,
    given: str,
    min_score: float,
    max_score: float,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """Alias for texts_expect_precision_range."""
    texts_expect_precision_range(expected, given, min_score, max_score,
                                 skip_warnings, retry_on_error)


def texts_agg_completeness_min(expected: str,
                               given: str,
                               lower_bound: float,
                               full_runs: int = 5,
                               each_question_runs: int = 1,
                               retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_min."""
    texts_agg_precision_min(expected, given, lower_bound, full_runs,
                            each_question_runs, retry_on_error)


def texts_agg_completeness_max(expected: str,
                               given: str,
                               upper_bound: float,
                               full_runs: int = 5,
                               each_question_runs: int = 1,
                               retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_max."""
    texts_agg_precision_max(expected, given, upper_bound, full_runs,
                            each_question_runs, retry_on_error)


def texts_agg_completeness_median(expected: str,
                                  given: str,
                                  target: float,
                                  max_delta: float = 0.1,
                                  full_runs: int = 5,
                                  each_question_runs: int = 1,
                                  retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_median."""
    texts_agg_precision_median(expected, given, target, max_delta, full_runs,
                               each_question_runs, retry_on_error)


def texts_agg_completeness_average(expected: str,
                                   given: str,
                                   target: float,
                                   max_delta: float = 0.1,
                                   full_runs: int = 5,
                                   each_question_runs: int = 1,
                                   retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_average."""
    texts_agg_precision_average(expected, given, target, max_delta, full_runs,
                                each_question_runs, retry_on_error)


def texts_agg_completeness_mean(expected: str,
                                given: str,
                                target: float,
                                max_delta: float = 0.1,
                                full_runs: int = 5,
                                each_question_runs: int = 1,
                                retry_on_error: bool = True) -> None:
    """Alias for texts_agg_precision_mean."""
    texts_agg_precision_mean(expected, given, target, max_delta, full_runs,
                             each_question_runs, retry_on_error)


# --- Correctness Wrappers (alias for Recall) ---


def texts_expect_correctness_equal(
    expected: str,
    given: str,
    target: float = 1.0,
    max_delta: float = 0.2,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """Alias for texts_expect_recall_equal."""
    texts_expect_recall_equal(expected, given, target, max_delta, skip_warnings,
                              retry_on_error)


def texts_expect_correctness_range(
    expected: str,
    given: str,
    min_score: float,
    max_score: float,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """Alias for texts_expect_recall_range."""
    texts_expect_recall_range(expected, given, min_score, max_score,
                              skip_warnings, retry_on_error)


def texts_agg_correctness_min(expected: str,
                              given: str,
                              lower_bound: float,
                              full_runs: int = 5,
                              each_question_runs: int = 1,
                              retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_min."""
    texts_agg_recall_min(expected, given, lower_bound, full_runs,
                         each_question_runs, retry_on_error)


def texts_agg_correctness_max(expected: str,
                              given: str,
                              upper_bound: float,
                              full_runs: int = 5,
                              each_question_runs: int = 1,
                              retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_max."""
    texts_agg_recall_max(expected, given, upper_bound, full_runs,
                         each_question_runs, retry_on_error)


def texts_agg_correctness_median(expected: str,
                                 given: str,
                                 target: float,
                                 max_delta: float = 0.1,
                                 full_runs: int = 5,
                                 each_question_runs: int = 1,
                                 retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_median."""
    texts_agg_recall_median(expected, given, target, max_delta, full_runs,
                            each_question_runs, retry_on_error)


def texts_agg_correctness_average(expected: str,
                                  given: str,
                                  target: float,
                                  max_delta: float = 0.1,
                                  full_runs: int = 5,
                                  each_question_runs: int = 1,
                                  retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_average."""
    texts_agg_recall_average(expected, given, target, max_delta, full_runs,
                             each_question_runs, retry_on_error)


def texts_agg_correctness_mean(expected: str,
                               given: str,
                               target: float,
                               max_delta: float = 0.1,
                               full_runs: int = 5,
                               each_question_runs: int = 1,
                               retry_on_error: bool = True) -> None:
    """Alias for texts_agg_recall_mean."""
    texts_agg_recall_mean(expected, given, target, max_delta, full_runs,
                          each_question_runs, retry_on_error)
