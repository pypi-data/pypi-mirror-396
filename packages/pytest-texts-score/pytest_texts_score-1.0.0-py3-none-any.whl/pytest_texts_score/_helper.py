import pytest
import warnings

from pytest_texts_score.evaluate_score import ScoreType


def check_input_target(target: float, max_delta: float,
                       minimal_expected_max_delta: float,
                       skip_warnings: bool) -> None:
    """
    Validate parameters for a target-based score assertion.

    Checks if ``target`` and ``max_delta`` are within the valid range [0, 1].
    It also issues a ``UserWarning`` if the resulting test range is too broad
    (e.g., covers all possible values from 0 to 1) or if ``max_delta`` is
    considered too strict compared to ``minimal_expected_max_delta``.

    :param target: The expected score, must be between 0 and 1.
    :type target: float
    :param max_delta: The allowed deviation from the target, must be between 0 and 1.
    :type max_delta: float
    :param minimal_expected_max_delta: The recommended minimum value for ``max_delta``.
    :type minimal_expected_max_delta: float
    :param skip_warnings: If ``True``, suppresses warnings about broad or strict ranges.
    :type skip_warnings: bool
    :raises pytest.UsageError: If ``target`` or ``max_delta`` are outside the [0, 1] range.
    """
    if not 0 <= target <= 1:
        raise pytest.UsageError(
            f"`target` value must be in range 0 to 1; {target} given.")

    if not 0 <= max_delta <= 1:
        raise pytest.UsageError(
            f"`max_delta` value must be in range 0 to 1; {max_delta} given.")

    if not skip_warnings:
        if (target - max_delta <= 0) and (target + max_delta >= 1):
            warnings.warn(
                "The score range defined by `target` and `max_delta` covers all "
                "possible values ([0, 1]) and may not be a meaningful test.",
                UserWarning,
                # stacklevel=3 ensures the warning points to the user's test code,
                # not internal library calls. (e.g., user_test -> texts_expect_* -> check_input_*)
                stacklevel=3,
            )

        if max_delta < minimal_expected_max_delta:
            warnings.warn(
                f"Given max_delta ({max_delta}) is strict; "
                f"consider at least {minimal_expected_max_delta}.",
                UserWarning,
                # stacklevel=3 ensures the warning points to the user's test code,
                # not internal library calls.
                stacklevel=3,
            )


def check_input_range(
    max_score: float,
    min_score: float,
    minimal_expected_max_delta: float,
    skip_warnings: bool,
) -> None:
    """
    Validate parameters for a range-based score assertion.

    Checks if ``max_score`` and ``min_score`` define a valid range within [0, 1].
    It issues a ``UserWarning`` if the range is too broad (e.g., [0, 1]) or if the
    width of the range is considered too strict compared to
    ``minimal_expected_max_delta``.

    :param max_score: The maximum allowed score, must be between 0 and 1.
    :type max_score: float
    :param min_score: The minimum allowed score, must be between 0 and 1.
    :type min_score: float
    :param minimal_expected_max_delta: The recommended minimum range width.
    :type minimal_expected_max_delta: float
    :param skip_warnings: If ``True``, suppresses validation warnings.
    :type skip_warnings: bool
    :raises pytest.UsageError: If scores are out of range or if ``max_score < min_score``.
    """
    if max_score > 1:
        raise pytest.UsageError(
            f"`max_score` value must be in range 0 to 1; {max_score} given.")
    if min_score < 0:
        raise pytest.UsageError(
            f"`min_score` value must be in range 0 to 1; {min_score} given.")
    if max_score < min_score:
        raise pytest.UsageError(
            f"`max_score` ({max_score}) cannot be smaller than "
            f"`min_score` ({min_score})")

    if not skip_warnings:
        if max_score >= 1.0 and min_score <= 0.0:
            warnings.warn(
                "The score range is set to [0, 1], which covers all "
                "possible values and may not be a meaningful test.",
                UserWarning,
                # stacklevel=3 ensures the warning points to the user's test code,
                # not internal library calls.
                stacklevel=3,
            )
        elif (max_score - min_score) < minimal_expected_max_delta:
            warnings.warn(
                f"Range ({max_score - min_score:.3f}) is strict; "
                f"consider at least {minimal_expected_max_delta}.",
                UserWarning,
                # stacklevel=3 ensures the warning points to the user's test code,
                # not internal library calls.
                stacklevel=3,
            )


def check_input_runs(full_runs: int, each_question_runs: int) -> None:
    """
    Validate the number of runs for aggregated tests.

    Ensures that the number of runs are positive integers. It also issues a
    ``UserWarning`` if the total number of runs is high, as this could lead to
    long execution times and increased costs.

    :param full_runs: The number of times to generate new sets of questions.
                      Must be a positive integer.
    :type full_runs: int
    :param each_question_runs: The number of times to evaluate answers for each
                               set of questions. Must be a positive integer.
    :type each_question_runs: int
    :raises pytest.UsageError: If run counts are not positive integers.
    """
    if not isinstance(full_runs, int) or full_runs <= 0:
        raise pytest.UsageError(
            f"`full_runs` must be a positive integer; {full_runs} given.")

    if not isinstance(each_question_runs, int) or each_question_runs <= 0:
        raise pytest.UsageError(
            "`each_question_runs` must be a positive integer; "
            f"{each_question_runs} given.")

    total_runs = full_runs * each_question_runs
    if total_runs > 50:
        warnings.warn(
            f"The total number of runs ({total_runs}) is high, which may "
            "result in a long test execution time and increased cost.",
            UserWarning,
            # stacklevel=3 ensures the warning points to the user's test code,
            # not internal library calls.
            stacklevel=3,
        )


def test_score(score: float, max_score: float, min_score: float, expected: str,
               given: str, score_type: ScoreType) -> None:
    """
    Assert that a calculated score falls within an expected range.

    This function is the final assertion helper. It compares the calculated
    ``score`` against the ``min_score`` and ``max_score``. If the score is
    outside this range, it calls ``pytest.fail`` with a detailed error message
    that includes the score type and the texts being compared.

    :param score: The calculated score to test.
    :type score: float
    :param max_score: The upper bound of the acceptable range.
    :type max_score: float
    :param min_score: The lower bound of the acceptable range.
    :type min_score: float
    :param expected: The reference text, used for the failure message.
    :type expected: str
    :param given: The evaluated text, used for the failure message.
    :type given: str
    :param score_type: The type of score being tested (e.g., F1, precision).
    :type score_type: ScoreType
    """
    # Ensure score_type is an enum member for consistent string representation
    # in the failure message, even if a raw string was passed.
    if isinstance(score_type, str):
        score_type = ScoreType(score_type)

    if score < min_score:
        pytest.fail(
            f"Text {score_type} below minimum: {score:.2f} < {min_score}.\n"
            f"`expected`: '{expected}'\n`given`: '{given}'")
    elif score > max_score:
        pytest.fail(
            f"Text {score_type} above maximum: {score:.2f} > {max_score}.\n"
            f"`expected`: '{expected}'\n`given`: '{given}'")
