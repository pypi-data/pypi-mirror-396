from enum import Enum
from typing import Literal
from pytest_texts_score.communication import (
    evaluate_questions,
    make_questions,
)
from statistics import median, mean

#: The maximum number of times to retry an LLM call upon failure before raising an exception.
MAXIMAL_RETRY_ON_ERROR = 5


class AggType(str, Enum):
    """Aggregation types for recall scores."""

    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MEDIAN = "median"
    AVERAGE = "average"
    MEAN = "mean"  # alias for average


class ScoreType(str, Enum):
    F1 = "f1"
    PRECISION = "precision"
    RECALL = "recall"


def texts_evaluate_f1(expected: str,
                      given: str,
                      retry_on_error: bool = True) -> float:
    """
    Calculate the F1 score between two texts.

    This function computes the F1 score by first calculating the precision and
    recall between the ``expected`` and ``given`` texts. It serves as a
    single-run evaluation of the harmonic mean of precision and recall.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to be evaluated against the reference.
    :type given: str
    :param retry_on_error: Whether to retry the LLM call on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The calculated F1 score.
    :rtype: float
    """
    precision = texts_evaluate_precision(expected, given, retry_on_error)
    recall = texts_evaluate_recall(expected, given, retry_on_error)
    return f1_score(precision, recall)


def texts_evaluate_precision(expected: str,
                             given: str,
                             retry_on_error: bool = True) -> float:
    """
    Evaluate the precision score of the given text against the expected text.

    Precision is calculated by generating questions from the ``given`` text and
    checking how well they are answered by the ``expected`` text. This measures
    how much of the information in the ``given`` text is also present in the
    ``expected`` text.

    :param expected: The reference text used for answering questions.
    :type expected: str
    :param given: The text from which questions are generated.
    :type given: str
    :param retry_on_error: Whether to retry the LLM call on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The calculated precision score.
    :rtype: float
    """
    return score_one_side(given, expected, retry_on_error=retry_on_error)


def texts_evaluate_recall(expected: str,
                          given: str,
                          retry_on_error: bool = True) -> float:
    """
    Evaluate the recall score of the given text against the expected text.

    Recall is calculated by generating questions from the ``expected`` text and
    checking how well they are answered by the ``given`` text. This measures
    how much of the information in the ``expected`` text is covered by the
    ``given`` text.

    :param expected: The reference text from which questions are generated.
    :type expected: str
    :param given: The text used for answering questions.
    :type given: str
    :param retry_on_error: Whether to retry the LLM call on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The calculated recall score.
    :rtype: float
    """
    return score_one_side(expected, given, retry_on_error=retry_on_error)


def texts_multiple_f1(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    score_only: bool = True,
    retry_on_error: bool = True,
) -> list[float] | list[tuple[int, int, float, float, float]]:
    """
    Perform multiple evaluation runs to get a list of F1 scores.

    This function runs the F1 score evaluation multiple times to account for
    variability in LLM responses. It generates new sets of questions for
    precision and recall in each ``generate_questions`` loop, and for each set,
    it evaluates answers ``generate_answers_per_questions`` times.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param score_only: If ``True``, returns only a list of F1 scores. If ``False``, returns a list of tuples with detailed run info. Defaults to ``True``.
    :type score_only: bool
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: A list of F1 scores, or a list of tuples ``(question_run, answer_run, precision, recall, f1_score)``.
    :rtype: list[float] | list[tuple[int, int, float, float, float]]
    :raises Exception: If the operation fails after the maximum number of retries.
    """
    # This function contains a retry mechanism. The outer loop iterates through `generate_questions`,
    # creating new question sets. The inner `while True` loop handles retries for LLM calls
    # within a single question set generation, providing resilience against transient network or API errors.
    results = []
    retries = 0
    for q_i in range(generate_questions):
        while True:
            try:
                question_text_precision = make_questions(given)
                question_text_recall = make_questions(expected)
                for a_i in range(generate_answers_per_questions):
                    answers_list_precision = evaluate_questions(
                        expected, question_text_precision)
                    score_value_counts = [
                        j.get("answer") for j in answers_list_precision
                    ]
                    precision = sum(score_value_counts) / len(
                        score_value_counts)

                    answers_list_recall = evaluate_questions(
                        given, question_text_recall)
                    score_value_counts = [
                        j.get("answer") for j in answers_list_recall
                    ]
                    recall = sum(score_value_counts) / len(score_value_counts)
                    if score_only:
                        results.append(f1_score(precision, recall))
                    else:
                        results.append((q_i, a_i, precision, recall,
                                        f1_score(precision, recall)))
                break

            except Exception as e:
                if not retry_on_error:
                    raise
                print(f"Error on question_run={q_i}; retrying: {e}")
                retries += 1
                if retries > MAXIMAL_RETRY_ON_ERROR:
                    raise Exception(
                        f"Operation failed after {retries} retries. Last error: {e}"
                    ) from e
                continue
    return results


def texts_multiple_precision(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    score_only: bool = True,
    retry_on_error: bool = True,
) -> list[float] | list[tuple[int, int, float]]:
    """
    Perform multiple evaluation runs to get a list of precision scores.

    This function runs the precision score evaluation multiple times. It
    generates new sets of questions from the ``given`` text in each
    ``generate_questions`` loop, and for each set, it evaluates answers
    ``generate_answers_per_questions`` times using the ``expected`` text.

    :param expected: The reference text for answering.
    :type expected: str
    :param given: The text to generate questions from.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param score_only: If ``True``, returns only a list of precision scores. If ``False``, returns a list of tuples with detailed run info. Defaults to ``True``.
    :type score_only: bool
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: A list of precision scores, or a list of tuples ``(question_run, answer_run, precision)``.
    :rtype: list[float] | list[tuple[int, int, float]]
    :raises Exception: If the operation fails after the maximum number of retries.
    """
    # This function contains a retry mechanism. The outer loop iterates through `generate_questions`,
    # creating new question sets. The inner `while True` loop handles retries for LLM calls
    # within a single question set generation.
    results = []
    retries = 0
    for q_i in range(generate_questions):
        while True:
            try:
                question_text_precision = make_questions(given)
                for a_i in range(generate_answers_per_questions):
                    answers_list_precision = evaluate_questions(
                        expected, question_text_precision)
                    score_value_counts = [
                        j.get("answer") for j in answers_list_precision
                    ]
                    precision = sum(score_value_counts) / len(
                        score_value_counts)

                    if score_only:
                        results.append(precision)
                    else:
                        results.append((q_i, a_i, precision))
                break

            except Exception as e:
                if not retry_on_error:
                    raise
                print(f"Error on question_run={q_i}; retrying: {e}")
                retries += 1
                if retries > MAXIMAL_RETRY_ON_ERROR:
                    raise Exception(
                        f"Operation failed after {retries} retries. Last error: {e}"
                    ) from e
                continue
    return results


def texts_multiple_recall(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    score_only: bool = True,
    retry_on_error: bool = True,
) -> list[float] | list[tuple[int, int, float]]:
    """
    Perform multiple evaluation runs to get a list of recall scores.

    This function runs the recall score evaluation multiple times. It generates
    new sets of questions from the ``expected`` text in each
    ``generate_questions`` loop, and for each set, it evaluates answers
    ``generate_answers_per_questions`` times using the ``given`` text.

    :param expected: The reference text to generate questions from.
    :type expected: str
    :param given: The text for answering.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param score_only: If ``True``, returns only a list of recall scores. If ``False``, returns a list of tuples with detailed run info. Defaults to ``True``.
    :type score_only: bool
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: A list of recall scores, or a list of tuples ``(question_run, answer_run, recall)``.
    :rtype: list[float] | list[tuple[int, int, float]]
    :raises Exception: If the operation fails after the maximum number of retries.
    """
    # This function contains a retry mechanism. The outer loop iterates through `generate_questions`,
    # creating new question sets. The inner `while True` loop handles retries for LLM calls
    # within a single question set generation.
    results = []
    retries = 0
    for q_i in range(generate_questions):
        while True:
            try:
                question_text_recall = make_questions(expected)
                for a_i in range(generate_answers_per_questions):
                    answers_list_recall = evaluate_questions(
                        given, question_text_recall)
                    score_value_counts = [
                        j.get("answer") for j in answers_list_recall
                    ]
                    recall = sum(score_value_counts) / len(score_value_counts)
                    if score_only:
                        results.append(recall)
                    else:
                        results.append((q_i, a_i, recall))
                break

            except Exception as e:
                if not retry_on_error:
                    raise
                print(f"Error on question_run={q_i}; retrying: {e}")
                retries += 1
                if retries > MAXIMAL_RETRY_ON_ERROR:
                    raise Exception(
                        f"Operation failed after {retries} retries. Last error: {e}"
                    ) from e
                continue
    return results


def score_one_side(base_text: str,
                   answer_text: str,
                   retry_on_error: bool = True) -> float:
    """
    Calculate a one-sided score by generating questions from one text and answering with another.

    This is a fundamental building block for both precision and recall calculations.
    It generates a set of questions based on ``base_text`` and then evaluates
    how well ``answer_text`` can answer them. The final score is the average of
    the answer scores. This process forms
    the basis for calculating both precision and recall.

    :param base_text: The text to generate questions from.
    :type base_text: str
    :param answer_text: The text to answer the questions with.
    :type answer_text: str
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The average score from the evaluation.
    :rtype: float
    :raises Exception: If the operation fails after the maximum number of retries.
    """
    # This function includes a retry loop to handle transient errors during LLM communication,
    # making the scoring process more robust.
    retries = 0
    while True:
        try:
            qustions_text = make_questions(base_text)
            answers_list = evaluate_questions(answer_text, qustions_text)
            score_value_counts = [j.get("answer") for j in answers_list]
            return sum(score_value_counts) / len(score_value_counts)
        except Exception as e:
            if not retry_on_error:
                raise
            print(f"Error on scoring; retrying: {e}")
            retries += 1
            if retries > MAXIMAL_RETRY_ON_ERROR:
                raise Exception(
                    f"Operation failed after {retries} retries. Last error: {e}"
                ) from e
            continue


def scores_agg(
    scores: list[float],
    agg_type: AggType |
    Literal["minimum", "maximum", "median", "average", "mean"],
) -> float:
    """
    Aggregate a list of scores using a specified method.

    This function takes a list of numeric scores and applies an aggregation
    function (min, max, median, or mean/average) to produce a single
    summary score.

    :param scores: A list of scores to aggregate.
    :type scores: list[float]
    :param agg_type: The aggregation method to use.
    :type agg_type: AggType | Literal["minimum", "maximum", "median", "average", "mean"]
    :return: The aggregated score.
    :rtype: float
    :raises ValueError: If an unknown aggregation type is provided.
    """
    # Convert string to enum if needed
    if isinstance(agg_type, str):
        agg_type = AggType(agg_type)

    # Apply aggregation
    match agg_type:
        case AggType.MINIMUM:
            return float(min(scores))

        case AggType.MAXIMUM:
            return float(max(scores))

        case AggType.MEDIAN:
            return float(median(scores))

        case AggType.AVERAGE | AggType.MEAN:
            return float(mean(scores))

        case _:
            raise ValueError(f"Unknown aggregation type: {agg_type}")


def texts_agg_f1(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    agg_type: AggType |
    Literal["minimum", "maximum", "median", "average", "mean"],
    retry_on_error: bool = True,
) -> float:
    """
    Calculate an aggregated F1 score over multiple runs.

    This function first generates multiple F1 scores by calling
    ``texts_multiple_f1`` and then aggregates these scores using the
    specified ``agg_type``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param agg_type: The aggregation method to use on the collected scores.
    :type agg_type: AggType | Literal["minimum", "maximum", "median", "average", "mean"]
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The final aggregated F1 score.
    :rtype: float
    """
    scores = texts_multiple_f1(
        expected=expected,
        given=given,
        generate_questions=generate_questions,
        generate_answers_per_questions=generate_answers_per_questions,
        score_only=True,
        retry_on_error=retry_on_error,
    )
    return scores_agg(scores, agg_type)


def texts_agg_precision(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    agg_type: AggType |
    Literal["minimum", "maximum", "median", "average", "mean"],
    retry_on_error: bool = True,
) -> float:
    """
    Calculate an aggregated precision score over multiple runs.

    This function first generates multiple precision scores by calling
    ``texts_multiple_precision`` and then aggregates these scores using the
    specified ``agg_type``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param agg_type: The aggregation method to use on the collected scores.
    :type agg_type: AggType | Literal["minimum", "maximum", "median", "average", "mean"]
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The final aggregated precision score.
    :rtype: float
    """
    scores = texts_multiple_precision(
        expected=expected,
        given=given,
        generate_questions=generate_questions,
        generate_answers_per_questions=generate_answers_per_questions,
        score_only=True,
        retry_on_error=retry_on_error,
    )
    return scores_agg(scores, agg_type)


def texts_agg_recall(
    expected: str,
    given: str,
    generate_questions: int,
    generate_answers_per_questions: int,
    agg_type: AggType |
    Literal["minimum", "maximum", "median", "average", "mean"],
    retry_on_error: bool = True,
) -> float:
    """
    Calculate an aggregated recall score over multiple runs.

    This function first generates multiple recall scores by calling
    ``texts_multiple_recall`` and then aggregates these scores using the
    specified ``agg_type``.

    :param expected: The reference text.
    :type expected: str
    :param given: The text to evaluate.
    :type given: str
    :param generate_questions: The number of times to generate a new set of questions.
    :type generate_questions: int
    :param generate_answers_per_questions: The number of times to evaluate answers for each set of questions.
    :type generate_answers_per_questions: int
    :param agg_type: The aggregation method to use on the collected scores.
    :type agg_type: AggType | Literal["minimum", "maximum", "median", "average", "mean"]
    :param retry_on_error: Whether to retry LLM calls on failure. Defaults to ``True``.
    :type retry_on_error: bool
    :return: The final aggregated recall score.
    :rtype: float
    """
    scores = texts_multiple_recall(
        expected=expected,
        given=given,
        generate_questions=generate_questions,
        generate_answers_per_questions=generate_answers_per_questions,
        score_only=True,
        retry_on_error=retry_on_error,
    )
    return scores_agg(scores, agg_type)


def f1_score(precision: float, recall: float) -> float:
    """
    Calculate the F1 score from precision and recall.

    Computes the harmonic mean of precision and recall. Returns 0 if both
    precision and recall are 0 to avoid division by zero.

    :param precision: The precision score (between 0.0 and 1.0).
    :type precision: float
    :param recall: The recall score (between 0.0 and 1.0).
    :type recall: float
    :return: The F1 score.
    :rtype: float
    """
    # Guard against division by zero if both precision and recall are 0.
    if precision + recall == 0:
        return 0
    return (2 * precision * recall) / (precision + recall)
