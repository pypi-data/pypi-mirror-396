from pytest_texts_score._helper import check_input_range, check_input_runs, check_input_target, test_score
from pytest_texts_score.evaluate_score import (
    AggType,
    ScoreType,
    texts_agg_f1,
    texts_agg_precision,
    texts_agg_recall,
    texts_evaluate_f1,
    texts_evaluate_precision,
    texts_evaluate_recall,
)

#: A recommended minimum value for the `max_delta` or range width.
#: Used to warn users if their test's acceptance criteria are very strict,
#: which might lead to flaky tests due to LLM non-determinism.
MINIMAL_EXPECTED_MAX_DELTA = 0.05


def texts_expect_f1_equal(
    expected: str,
    given: str,
    target: float = 1.0,
    max_delta: float = 0.2,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the F1 score is close to a target value.

    This is a convenience wrapper around :func:`~.texts_expect_f1_range`.
    It performs a single F1 score evaluation and asserts that the result
    is within ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected F1 score. Defaults to 1.0.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.2.
    :type max_delta: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_target(target, max_delta, MINIMAL_EXPECTED_MAX_DELTA,
                       skip_warnings)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    texts_expect_f1_range(expected,
                          given,
                          min_score,
                          max_score,
                          skip_warnings=True,
                          retry_on_error=retry_on_error)


def texts_expect_f1_range(
    expected: str,
    given: str,
    min_score: float,
    max_score: float,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the F1 score falls within a specified range.

    This function performs a single evaluation of the F1 score between the
    ``expected`` and ``given`` texts. It then asserts that the resulting score
    is between ``min_score`` and ``max_score``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param min_score: The minimum acceptable F1 score.
    :type min_score: float
    :param max_score: The maximum acceptable F1 score.
    :type max_score: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_range(max_score, min_score, MINIMAL_EXPECTED_MAX_DELTA,
                      skip_warnings)

    score = texts_evaluate_f1(expected, given, retry_on_error=retry_on_error)

    test_score(score, max_score, min_score, expected, given, ScoreType.F1)


def texts_expect_precision_equal(
    expected: str,
    given: str,
    target: float = 1.0,
    max_delta: float = 0.2,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the precision score is close to a target value.

    This is a convenience wrapper around :func:`~.texts_expect_precision_range`.
    It performs a single precision score evaluation and asserts that the result
    is within ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected precision score. Defaults to 1.0.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.2.
    :type max_delta: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_target(target, max_delta, MINIMAL_EXPECTED_MAX_DELTA,
                       skip_warnings)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    texts_expect_precision_range(expected,
                                 given,
                                 min_score,
                                 max_score,
                                 skip_warnings=True,
                                 retry_on_error=retry_on_error)


def texts_expect_precision_range(
    expected: str,
    given: str,
    min_score: float,
    max_score: float,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the precision score falls within a specified range.

    This function performs a single evaluation of the precision score between the
    ``expected`` and ``given`` texts. It then asserts that the resulting score
    is between ``min_score`` and ``max_score``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param min_score: The minimum acceptable precision score.
    :type min_score: float
    :param max_score: The maximum acceptable precision score.
    :type max_score: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_range(max_score, min_score, MINIMAL_EXPECTED_MAX_DELTA,
                      skip_warnings)

    score = texts_evaluate_precision(expected,
                                     given,
                                     retry_on_error=retry_on_error)

    test_score(score, max_score, min_score, expected, given,
               ScoreType.PRECISION)


def texts_expect_recall_equal(
    expected: str,
    given: str,
    target: float = 1.0,
    max_delta: float = 0.2,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the recall score is close to a target value.

    This is a convenience wrapper around :func:`~.texts_expect_recall_range`.
    It performs a single recall score evaluation and asserts that the result
    is within ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected recall score. Defaults to 1.0.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.2.
    :type max_delta: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_target(target, max_delta, MINIMAL_EXPECTED_MAX_DELTA,
                       skip_warnings)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    texts_expect_recall_range(expected,
                              given,
                              min_score,
                              max_score,
                              skip_warnings=True,
                              retry_on_error=retry_on_error)


def texts_expect_recall_range(
    expected: str,
    given: str,
    min_score: float,
    max_score: float,
    skip_warnings: bool = False,
    retry_on_error: bool = True,
) -> None:
    """
    Assert that the recall score falls within a specified range.

    This function performs a single evaluation of the recall score between the
    ``expected`` and ``given`` texts. It then asserts that the resulting score
    is between ``min_score`` and ``max_score``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param min_score: The minimum acceptable recall score.
    :type min_score: float
    :param max_score: The maximum acceptable recall score.
    :type max_score: float
    :param skip_warnings: If ``True``, suppresses input validation warnings.
    :type skip_warnings: bool
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_range(max_score, min_score, MINIMAL_EXPECTED_MAX_DELTA,
                      skip_warnings)

    score = texts_evaluate_recall(expected,
                                  given,
                                  retry_on_error=retry_on_error)

    test_score(score, max_score, min_score, expected, given, ScoreType.RECALL)


# F1 Score Aggregation Functions


def texts_agg_f1_min(expected: str,
                     given: str,
                     lower_bound: float,
                     full_runs: int = 5,
                     each_question_runs: int = 1,
                     retry_on_error: bool = True) -> None:
    """
    Assert that the minimum aggregated F1 score is above a lower bound.

    Performs multiple evaluation runs, calculates the minimum F1 score across
    all runs, and asserts that this minimum score is greater than or equal to
    ``lower_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param lower_bound: The minimum acceptable score for the aggregated minimum.
    :type lower_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_f1(expected, given, full_runs, each_question_runs,
                         AggType.MINIMUM, retry_on_error)
    # For a 'min' test, we assert the score is within [lower_bound, 1.0].
    # The upper bound is 1.0 because a higher score is always better.
    test_score(score, 1.0, lower_bound, expected, given, ScoreType.F1)


def texts_agg_f1_max(expected: str,
                     given: str,
                     upper_bound: float,
                     full_runs: int = 5,
                     each_question_runs: int = 1,
                     retry_on_error: bool = True) -> None:
    """
    Assert that the maximum aggregated F1 score is below an upper bound.

    Performs multiple evaluation runs, calculates the maximum F1 score across
    all runs, and asserts that this maximum score is less than or equal to
    ``upper_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param upper_bound: The maximum acceptable score for the aggregated maximum.
    :type upper_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_f1(expected, given, full_runs, each_question_runs,
                         AggType.MAXIMUM, retry_on_error)
    # For a 'max' test, we assert the score is within [0.0, upper_bound].
    # The lower bound is 0.0 because a lower score is always acceptable.
    test_score(score, upper_bound, 0.0, expected, given, ScoreType.F1)


def texts_agg_f1_median(expected: str,
                        given: str,
                        target: float,
                        max_delta: float = 0.1,
                        full_runs: int = 5,
                        each_question_runs: int = 1,
                        retry_on_error: bool = True) -> None:
    """
    Assert that the median aggregated F1 score is close to a target value.

    Performs multiple evaluation runs, calculates the median F1 score, and
    asserts that it falls within the range defined by ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected median score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_f1(expected, given, full_runs, each_question_runs,
                         AggType.MEDIAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given, ScoreType.F1)


def texts_agg_f1_mean(expected: str,
                      given: str,
                      target: float,
                      max_delta: float = 0.1,
                      full_runs: int = 5,
                      each_question_runs: int = 1,
                      retry_on_error: bool = True) -> None:
    """
    Assert that the mean aggregated F1 score is close to a target value.

    Performs multiple evaluation runs, calculates the mean (average) F1 score,
    and asserts that it falls within the range defined by ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected mean score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_f1(expected, given, full_runs, each_question_runs,
                         AggType.MEAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given, ScoreType.F1)


# Precision Score Aggregation Functions


def texts_agg_precision_min(expected: str,
                            given: str,
                            lower_bound: float,
                            full_runs: int = 5,
                            each_question_runs: int = 1,
                            retry_on_error: bool = True) -> None:
    """
    Assert that the minimum aggregated precision is above a lower bound.

    Performs multiple evaluation runs, calculates the minimum precision score
    across all runs, and asserts that this minimum score is greater than or
    equal to ``lower_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param lower_bound: The minimum acceptable score for the aggregated minimum.
    :type lower_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_precision(expected, given, full_runs, each_question_runs,
                                AggType.MINIMUM, retry_on_error)
    # For a 'min' test, we assert the score is within [lower_bound, 1.0].
    # The upper bound is 1.0 because a higher score is always better.
    test_score(score, 1.0, lower_bound, expected, given, ScoreType.PRECISION)


def texts_agg_precision_max(expected: str,
                            given: str,
                            upper_bound: float,
                            full_runs: int = 5,
                            each_question_runs: int = 1,
                            retry_on_error: bool = True) -> None:
    """
    Assert that the maximum aggregated precision is below an upper bound.

    Performs multiple evaluation runs, calculates the maximum precision score
    across all runs, and asserts that this maximum score is less than or equal
    to ``upper_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param upper_bound: The maximum acceptable score for the aggregated maximum.
    :type upper_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_precision(expected, given, full_runs, each_question_runs,
                                AggType.MAXIMUM, retry_on_error)
    # For a 'max' test, we assert the score is within [0.0, upper_bound].
    # The lower bound is 0.0 because a lower score is always acceptable.
    test_score(score, upper_bound, 0.0, expected, given, ScoreType.PRECISION)


def texts_agg_precision_median(expected: str,
                               given: str,
                               target: float,
                               max_delta: float = 0.1,
                               full_runs: int = 5,
                               each_question_runs: int = 1,
                               retry_on_error: bool = True) -> None:
    """
    Assert that the median aggregated precision is close to a target value.

    Performs multiple evaluation runs, calculates the median precision score,
    and asserts that it falls within the range defined by ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected median score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_precision(expected, given, full_runs, each_question_runs,
                                AggType.MEDIAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given,
               ScoreType.PRECISION)


def texts_agg_precision_mean(expected: str,
                             given: str,
                             target: float,
                             max_delta: float = 0.1,
                             full_runs: int = 5,
                             each_question_runs: int = 1,
                             retry_on_error: bool = True) -> None:
    """
    Assert that the mean aggregated precision is close to a target value.

    Performs multiple evaluation runs, calculates the mean (average) precision
    score, and asserts that it falls within the range ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected mean score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_precision(expected, given, full_runs, each_question_runs,
                                AggType.MEAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given,
               ScoreType.PRECISION)


# Recall Score Aggregation Functions


def texts_agg_recall_min(expected: str,
                         given: str,
                         lower_bound: float,
                         full_runs: int = 5,
                         each_question_runs: int = 1,
                         retry_on_error: bool = True) -> None:
    """
    Assert that the minimum aggregated recall is above a lower bound.

    Performs multiple evaluation runs, calculates the minimum recall score
    across all runs, and asserts that this minimum score is greater than or
    equal to ``lower_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param lower_bound: The minimum acceptable score for the aggregated minimum.
    :type lower_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_recall(expected, given, full_runs, each_question_runs,
                             AggType.MINIMUM, retry_on_error)
    # For a 'min' test, we assert the score is within [lower_bound, 1.0].
    # The upper bound is 1.0 because a higher score is always better.
    test_score(score, 1.0, lower_bound, expected, given, ScoreType.RECALL)


def texts_agg_recall_max(expected: str,
                         given: str,
                         upper_bound: float,
                         full_runs: int = 5,
                         each_question_runs: int = 1,
                         retry_on_error: bool = True) -> None:
    """
    Assert that the maximum aggregated recall is below an upper bound.

    Performs multiple evaluation runs, calculates the maximum recall score
    across all runs, and asserts that this maximum score is less than or equal
    to ``upper_bound``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param upper_bound: The maximum acceptable score for the aggregated maximum.
    :type upper_bound: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_recall(expected, given, full_runs, each_question_runs,
                             AggType.MAXIMUM, retry_on_error)
    # For a 'max' test, we assert the score is within [0.0, upper_bound].
    # The lower bound is 0.0 because a lower score is always acceptable.
    test_score(score, upper_bound, 0.0, expected, given, ScoreType.RECALL)


def texts_agg_recall_median(expected: str,
                            given: str,
                            target: float,
                            max_delta: float = 0.1,
                            full_runs: int = 5,
                            each_question_runs: int = 1,
                            retry_on_error: bool = True) -> None:
    """
    Assert that the median aggregated recall is close to a target value.

    Performs multiple evaluation runs, calculates the median recall score, and
    asserts that it falls within the range defined by ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected median score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_recall(expected, given, full_runs, each_question_runs,
                             AggType.MEDIAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given, ScoreType.RECALL)


def texts_agg_recall_mean(expected: str,
                          given: str,
                          target: float,
                          max_delta: float = 0.1,
                          full_runs: int = 5,
                          each_question_runs: int = 1,
                          retry_on_error: bool = True) -> None:
    """
    Assert that the mean aggregated recall is close to a target value.

    Performs multiple evaluation runs, calculates the mean (average) recall
    score, and asserts that it falls within the range ``target ± max_delta``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param target: The expected mean score.
    :type target: float
    :param max_delta: The allowed deviation from the target. Defaults to 0.1.
    :type max_delta: float
    :param full_runs: Number of times to generate new questions. Defaults to 5.
    :type full_runs: int
    :param each_question_runs: Number of times to evaluate answers per question set. Defaults to 1.
    :type each_question_runs: int
    :param retry_on_error: If ``True``, retries LLM calls on failure.
    :type retry_on_error: bool
    """
    check_input_runs(full_runs, each_question_runs)
    score = texts_agg_recall(expected, given, full_runs, each_question_runs,
                             AggType.MEAN, retry_on_error)

    min_score = max(0.0, target - max_delta)
    max_score = min(1.0, target + max_delta)

    test_score(score, max_score, min_score, expected, given, ScoreType.RECALL)
