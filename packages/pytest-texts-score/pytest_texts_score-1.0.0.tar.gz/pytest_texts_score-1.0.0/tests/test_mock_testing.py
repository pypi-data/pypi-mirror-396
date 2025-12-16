from unittest.mock import call, patch

import pytest

from pytest_texts_score import (
    texts_agg_f1_average,
    texts_agg_f1_max,
    texts_agg_f1_mean,
    texts_agg_f1_median,
    texts_agg_f1_min,
    texts_agg_precision_average,
    texts_agg_precision_max,
    texts_agg_precision_mean,
    texts_agg_precision_median,
    texts_agg_precision_min,
    texts_agg_recall_average,
    texts_agg_recall_max,
    texts_agg_recall_mean,
    texts_agg_recall_median,
    texts_agg_recall_min,
    texts_agg_completeness_mean,
    texts_agg_completeness_average,
    texts_agg_completeness_max,
    texts_agg_completeness_median,
    texts_agg_completeness_min,
    texts_agg_correctness_mean,
    texts_agg_correctness_average,
    texts_agg_correctness_max,
    texts_agg_correctness_median,
    texts_agg_correctness_min,
)
from pytest_texts_score.evaluate_score import (
    MAXIMAL_RETRY_ON_ERROR,
    score_one_side,
    texts_multiple_f1,
    texts_multiple_precision,
    texts_multiple_recall,
)


# Test for texts_agg_f1_mean
# Expected behavior: Calculates the mean of F1 scores
@patch('pytest_texts_score.evaluate_score.texts_multiple_f1')
def test_texts_agg_f1_mean_mock(mock_texts_multiple_f1):
    # Mock return value: F1 scores [1, 1, 0, 0]
    # Expected mean: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_f1.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_f1_mean("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_f1 was called exactly once
    mock_texts_multiple_f1.assert_called_once()


# Test for texts_agg_f1_average
# Expected behavior: Calculates the average of F1 scores (same as mean)
@patch('pytest_texts_score.evaluate_score.texts_multiple_f1')
def test_texts_agg_f1_average_mock(mock_texts_multiple_f1):
    # Mock return value: F1 scores [1, 1, 0, 0]
    # Expected average: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_f1.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_f1_average("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_f1 was called exactly once
    mock_texts_multiple_f1.assert_called_once()


# Test for texts_agg_f1_max
# Expected behavior: Returns the maximum F1 score
@patch('pytest_texts_score.evaluate_score.texts_multiple_f1')
def test_texts_agg_f1_max_mock(mock_texts_multiple_f1):
    # Mock return value: F1 scores [1, 1, 0, 0]
    # Expected max: 1
    mock_texts_multiple_f1.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_f1_max("any", "any", 1, 4, 1, True)

    # Verify that texts_multiple_f1 was called exactly once
    mock_texts_multiple_f1.assert_called_once()


# Test for texts_agg_f1_median
# Expected behavior: Returns the median F1 score
@patch('pytest_texts_score.evaluate_score.texts_multiple_f1')
def test_texts_agg_f1_median_mock(mock_texts_multiple_f1):
    # Mock return value: F1 scores [1, 1, 0, 0]
    # Sorted: [0, 0, 1, 1], Expected median: (0 + 1) / 2 = 0.5
    mock_texts_multiple_f1.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_f1_median("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_f1 was called exactly once
    mock_texts_multiple_f1.assert_called_once()


# Test for texts_agg_f1_min
# Expected behavior: Returns the minimum F1 score
@patch('pytest_texts_score.evaluate_score.texts_multiple_f1')
def test_texts_agg_f1_min_mock(mock_texts_multiple_f1):
    # Mock return value: F1 scores [1, 1, 0, 0]
    # Expected min: 0
    mock_texts_multiple_f1.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_f1_min("any", "any", 0, 4, 1, True)

    # Verify that texts_multiple_f1 was called exactly once
    mock_texts_multiple_f1.assert_called_once()


# Test for texts_agg_precision_mean
# Expected behavior: Returns the mean of F1 score
@patch('pytest_texts_score.evaluate_score.texts_multiple_precision')
def test_texts_agg_precision_mean_mock(mock_texts_multiple_precision):
    # Mock return value: Precision scores [1, 1, 0, 0]
    # Expected mean: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_precision.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_precision_mean("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_precision was called exactly once
    mock_texts_multiple_precision.assert_called_once()


# Test for texts_agg_precision_average
# Expected behavior: Calculates the average of precision scores (same as mean)
@patch('pytest_texts_score.evaluate_score.texts_multiple_precision')
def test_texts_agg_precision_average_mock(mock_texts_multiple_precision):
    # Mock return value: Precision scores [1, 1, 0, 0]
    # Expected average: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_precision.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_precision_average("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_precision was called exactly once
    mock_texts_multiple_precision.assert_called_once()


# Test for texts_agg_precision_max
# Expected behavior: Returns the maximum precision score
@patch('pytest_texts_score.evaluate_score.texts_multiple_precision')
def test_texts_agg_precision_max_mock(mock_texts_multiple_precision):
    # Mock return value: Precision scores [1, 1, 0, 0]
    # Expected max: 1
    mock_texts_multiple_precision.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_precision_max("any", "any", 1, 4, 1, True)

    # Verify that texts_multiple_precision was called exactly once
    mock_texts_multiple_precision.assert_called_once()


# Test for texts_agg_precision_median
# Expected behavior: Returns the median precision score
@patch('pytest_texts_score.evaluate_score.texts_multiple_precision')
def test_texts_agg_precision_median_mock(mock_texts_multiple_precision):
    # Mock return value: Precision scores [1, 1, 0, 0]
    # Sorted: [0, 0, 1, 1], Expected median: (0 + 1) / 2 = 0.5
    mock_texts_multiple_precision.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_precision_median("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_precision was called exactly once
    mock_texts_multiple_precision.assert_called_once()


# Test for texts_agg_precision_min
# Expected behavior: Returns the minimum precision score
@patch('pytest_texts_score.evaluate_score.texts_multiple_precision')
def test_texts_agg_precision_min_mock(mock_texts_multiple_precision):
    # Mock return value: Precision scores [1, 1, 0, 0]
    # Expected min: 0
    mock_texts_multiple_precision.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_precision_min("any", "any", 0, 4, 1, True)

    # Verify that texts_multiple_precision was called exactly once
    mock_texts_multiple_precision.assert_called_once()


# Test for texts_agg_recall_mean
# Expected behavior: Calculates the mean of recall scores
@patch('pytest_texts_score.evaluate_score.texts_multiple_recall')
def test_texts_agg_recall_mean_mock(mock_texts_multiple_recall):
    # Mock return value: Recall scores [1, 1, 0, 0]
    # Expected mean: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_recall.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_recall_mean("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_recall was called exactly once
    mock_texts_multiple_recall.assert_called_once()


# Test for texts_agg_recall_average
# Expected behavior: Calculates the average of recall scores (same as mean)
@patch('pytest_texts_score.evaluate_score.texts_multiple_recall')
def test_texts_agg_recall_average_mock(mock_texts_multiple_recall):
    # Mock return value: Recall scores [1, 1, 0, 0]
    # Expected average: (1 + 1 + 0 + 0) / 4 = 0.5
    mock_texts_multiple_recall.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_recall_average("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_recall was called exactly once
    mock_texts_multiple_recall.assert_called_once()


# Test for texts_agg_recall_max
# Expected behavior: Returns the maximum recall score
@patch('pytest_texts_score.evaluate_score.texts_multiple_recall')
def test_texts_agg_recall_max_mock(mock_texts_multiple_recall):
    # Mock return value: Recall scores [1, 1, 0, 0]
    # Expected max: 1
    mock_texts_multiple_recall.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_recall_max("any", "any", 1, 4, 1, True)

    # Verify that texts_multiple_recall was called exactly once
    mock_texts_multiple_recall.assert_called_once()


# Test for texts_agg_recall_median
# Expected behavior: Returns the median recall score
@patch('pytest_texts_score.evaluate_score.texts_multiple_recall')
def test_texts_agg_recall_median_mock(mock_texts_multiple_recall):
    # Mock return value: Recall scores [1, 1, 0, 0]
    # Sorted: [0, 0, 1, 1], Expected median: (0 + 1) / 2 = 0.5
    mock_texts_multiple_recall.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_recall_median("any", "any", 0.5, 0, 4, 1, True)

    # Verify that texts_multiple_recall was called exactly once
    mock_texts_multiple_recall.assert_called_once()


# Test for texts_agg_recall_min
# Expected behavior: Returns the minimum recall score
@patch('pytest_texts_score.evaluate_score.texts_multiple_recall')
def test_texts_agg_recall_min_mock(mock_texts_multiple_recall):
    # Mock return value: Recall scores [1, 1, 0, 0]
    # Expected min: 0
    mock_texts_multiple_recall.return_value = [1, 1, 0, 0]

    # Call the function with test parameters
    texts_agg_recall_min("any", "any", 0, 4, 1, True)

    # Verify that texts_multiple_recall was called exactly once
    mock_texts_multiple_recall.assert_called_once()


# Test for texts_agg_completeness_mean
# Expected behavior: Wrapper for texts_agg_precision_mean
@patch('pytest_texts_score.api_wrappers.texts_agg_precision_mean')
def test_texts_agg_completeness_mean_mock(mock_texts_agg_precision_mean):
    # Call the wrapper function with test parameters
    texts_agg_completeness_mean("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_precision_mean was called with the same parameters
    mock_texts_agg_precision_mean.assert_called_once_with(
        "expected", "given", 0.5, 0.1, 5, 1, True)


# Test for texts_agg_completeness_average
# Expected behavior: Wrapper for texts_agg_precision_average
@patch('pytest_texts_score.api_wrappers.texts_agg_precision_average')
def test_texts_agg_completeness_average_mock(mock_texts_agg_precision_average):
    # Call the wrapper function with test parameters
    texts_agg_completeness_average("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_precision_average was called with the same parameters
    mock_texts_agg_precision_average.assert_called_once_with(
        "expected", "given", 0.5, 0.1, 5, 1, True)


# Test for texts_agg_completeness_max
# Expected behavior: Wrapper for texts_agg_precision_max
@patch('pytest_texts_score.api_wrappers.texts_agg_precision_max')
def test_texts_agg_completeness_max_mock(mock_texts_agg_precision_max):
    # Call the wrapper function with test parameters
    texts_agg_completeness_max("expected", "given", 1.0, 5, 1, True)

    # Verify that texts_agg_precision_max was called with the same parameters
    mock_texts_agg_precision_max.assert_called_once_with(
        "expected", "given", 1.0, 5, 1, True)


# Test for texts_agg_completeness_median
# Expected behavior: Wrapper for texts_agg_precision_median
@patch('pytest_texts_score.api_wrappers.texts_agg_precision_median')
def test_texts_agg_completeness_median_mock(mock_texts_agg_precision_median):
    # Call the wrapper function with test parameters
    texts_agg_completeness_median("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_precision_median was called with the same parameters
    mock_texts_agg_precision_median.assert_called_once_with(
        "expected", "given", 0.5, 0.1, 5, 1, True)


# Test for texts_agg_completeness_min
# Expected behavior: Wrapper for texts_agg_precision_min
@patch('pytest_texts_score.api_wrappers.texts_agg_precision_min')
def test_texts_agg_completeness_min_mock(mock_texts_agg_precision_min):
    # Call the wrapper function with test parameters
    texts_agg_completeness_min("expected", "given", 0.0, 5, 1, True)

    # Verify that texts_agg_precision_min was called with the same parameters
    mock_texts_agg_precision_min.assert_called_once_with(
        "expected", "given", 0.0, 5, 1, True)


# Test for texts_agg_correctness_mean
# Expected behavior: Wrapper for texts_agg_recall_mean
@patch('pytest_texts_score.api_wrappers.texts_agg_recall_mean')
def test_texts_agg_correctness_mean_mock(mock_texts_agg_recall_mean):
    # Call the wrapper function with test parameters
    texts_agg_correctness_mean("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_recall_mean was called with the same parameters
    mock_texts_agg_recall_mean.assert_called_once_with("expected", "given", 0.5,
                                                       0.1, 5, 1, True)


# Test for texts_agg_correctness_average
# Expected behavior: Wrapper for texts_agg_recall_average
@patch('pytest_texts_score.api_wrappers.texts_agg_recall_average')
def test_texts_agg_correctness_average_mock(mock_texts_agg_recall_average):
    # Call the wrapper function with test parameters
    texts_agg_correctness_average("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_recall_average was called with the same parameters
    mock_texts_agg_recall_average.assert_called_once_with(
        "expected", "given", 0.5, 0.1, 5, 1, True)


# Test for texts_agg_correctness_max
# Expected behavior: Wrapper for texts_agg_recall_max
@patch('pytest_texts_score.api_wrappers.texts_agg_recall_max')
def test_texts_agg_correctness_max_mock(mock_texts_agg_recall_max):
    # Call the wrapper function with test parameters
    texts_agg_correctness_max("expected", "given", 1.0, 5, 1, True)

    # Verify that texts_agg_recall_max was called with the same parameters
    mock_texts_agg_recall_max.assert_called_once_with("expected", "given", 1.0,
                                                      5, 1, True)


# Test for texts_agg_correctness_median
# Expected behavior: Wrapper for texts_agg_recall_median
@patch('pytest_texts_score.api_wrappers.texts_agg_recall_median')
def test_texts_agg_correctness_median_mock(mock_texts_agg_recall_median):
    # Call the wrapper function with test parameters
    texts_agg_correctness_median("expected", "given", 0.5, 0.1, 5, 1, True)

    # Verify that texts_agg_recall_median was called with the same parameters
    mock_texts_agg_recall_median.assert_called_once_with(
        "expected", "given", 0.5, 0.1, 5, 1, True)


# Test for texts_agg_correctness_min
# Expected behavior: Wrapper for texts_agg_recall_min
@patch('pytest_texts_score.api_wrappers.texts_agg_recall_min')
def test_texts_agg_correctness_min_mock(mock_texts_agg_recall_min):
    # Call the wrapper function with test parameters
    texts_agg_correctness_min("expected", "given", 0.0, 5, 1, True)

    # Verify that texts_agg_recall_min was called with the same parameters
    mock_texts_agg_recall_min.assert_called_once_with("expected", "given", 0.0,
                                                      5, 1, True)


# Test for retry mechanism in score_one_side
# Expected behavior: Retries on failure and succeeds
@patch('pytest_texts_score.evaluate_score.evaluate_questions')
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_score_one_side_retry_succeeds(mock_make_questions,
                                       mock_evaluate_questions):
    # Configure make_questions to fail twice then succeed
    mock_make_questions.side_effect = [
        Exception("Failed to generate questions"),
        Exception("Failed to generate questions again"), "successful questions"
    ]
    # Configure evaluate_questions to return a successful response
    mock_evaluate_questions.return_value = [{"answer": 1.0}, {"answer": 0.5}]

    # Call the function that should retry
    result = score_one_side("base", "answer", retry_on_error=True)

    # Verify the result is correct
    assert result == 0.75
    # Verify make_questions was called 3 times
    assert mock_make_questions.call_count == 3
    # Verify evaluate_questions was called once with the successful questions
    mock_evaluate_questions.assert_called_once_with("answer",
                                                    "successful questions")


# Test for retry mechanism in score_one_side when it always fails
# Expected behavior: Retries until max retries and then raises an exception
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_score_one_side_retry_fails(mock_make_questions):
    # Configure make_questions to always fail
    mock_make_questions.side_effect = Exception("Always fails")

    # Verify that the function raises an exception after exhausting retries
    with pytest.raises(
            Exception,
            match=f"Operation failed after {MAXIMAL_RETRY_ON_ERROR + 1} retries"
    ):
        score_one_side("base", "answer", retry_on_error=True)

    # Verify make_questions was called MAXIMAL_RETRY_ON_ERROR + 1 times
    assert mock_make_questions.call_count == MAXIMAL_RETRY_ON_ERROR + 1


# --- Tests for retry mechanism in texts_multiple_* functions ---


# Test for retry mechanism in texts_multiple_f1
# Expected behavior: Retries on failure and succeeds
@patch('pytest_texts_score.evaluate_score.evaluate_questions')
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_f1_retry_succeeds(mock_make_questions,
                                          mock_evaluate_questions):
    mock_make_questions.side_effect = [
        Exception("Failed to generate questions"),  # First call fails
        # Subsequent calls succeed
        "successful questions precision",
        "successful questions recall"
    ]
    mock_evaluate_questions.side_effect = [
        # Mock responses for precision and recall
        [{
            "answer": 1.0
        }],  # precision
        [{
            "answer": 0.5
        }],  # recall
    ]

    # Call the function that should retry
    result = texts_multiple_f1("expected", "given", 1, 1, score_only=True)

    # Verify the result is correct
    assert result == [0.6666666666666666]
    # Verify make_questions was called 3 times (1 failure, 2 successes)
    assert mock_make_questions.call_count == 3
    # Verify evaluate_questions was called twice (for precision and recall)
    assert mock_evaluate_questions.call_count == 2


# Test for retry mechanism in texts_multiple_f1 when it always fails
# Expected behavior: Retries until max retries and then raises an exception
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_f1_retry_fails(mock_make_questions):
    # Configure make_questions to always fail
    mock_make_questions.side_effect = Exception("Always fails")

    with pytest.raises(
            Exception,
            match=f"Operation failed after {MAXIMAL_RETRY_ON_ERROR + 1} retries"
    ):
        texts_multiple_f1("expected", "given", 1, 1)

    # Verify make_questions was called MAXIMAL_RETRY_ON_ERROR + 1 times
    assert mock_make_questions.call_count == MAXIMAL_RETRY_ON_ERROR + 1


# Test for retry mechanism in texts_multiple_precision
# Expected behavior: Retries on failure and succeeds
@patch('pytest_texts_score.evaluate_score.evaluate_questions')
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_precision_retry_succeeds(mock_make_questions,
                                                 mock_evaluate_questions):
    mock_make_questions.side_effect = [
        Exception("Failed to generate questions"), "successful questions"
    ]
    # Configure evaluate_questions to return a successful response
    mock_evaluate_questions.return_value = [{"answer": 0.75}]

    # Call the function that should retry
    result = texts_multiple_precision("expected",
                                      "given",
                                      1,
                                      1,
                                      score_only=True)

    # Verify the result is correct
    assert result == [0.75]
    # Verify make_questions was called 2 times (1 failure, 1 success)
    assert mock_make_questions.call_count == 2
    # Verify evaluate_questions was called once with the successful questions
    mock_evaluate_questions.assert_called_once_with("expected",
                                                    "successful questions")


# Test for retry mechanism in texts_multiple_precision when it always fails
# Expected behavior: Retries until max retries and then raises an exception
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_precision_retry_fails(mock_make_questions):
    # Configure make_questions to always fail
    mock_make_questions.side_effect = Exception("Always fails")

    with pytest.raises(
            Exception,
            match=f"Operation failed after {MAXIMAL_RETRY_ON_ERROR + 1} retries"
    ):
        texts_multiple_precision("expected", "given", 1, 1)

    # Verify make_questions was called MAXIMAL_RETRY_ON_ERROR + 1 times
    assert mock_make_questions.call_count == MAXIMAL_RETRY_ON_ERROR + 1


# Test for retry mechanism in texts_multiple_recall
# Expected behavior: Retries on failure and succeeds
@patch('pytest_texts_score.evaluate_score.evaluate_questions')
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_recall_retry_succeeds(mock_make_questions,
                                              mock_evaluate_questions):
    mock_make_questions.side_effect = [
        Exception("Failed to generate questions"), "successful questions"
    ]
    mock_evaluate_questions.return_value = [{"answer": 0.25}]

    result = texts_multiple_recall("expected", "given", 1, 1, score_only=True)

    # Verify the result is correct
    assert result == [0.25]
    # Verify make_questions was called 2 times (1 failure, 1 success)
    assert mock_make_questions.call_count == 2
    # Verify evaluate_questions was called once with the successful questions
    mock_evaluate_questions.assert_called_once_with("given",
                                                    "successful questions")


# Test for retry mechanism in texts_multiple_recall when it always fails
# Expected behavior: Retries until max retries and then raises an exception
@patch('pytest_texts_score.evaluate_score.make_questions')
def test_texts_multiple_recall_retry_fails(mock_make_questions):
    # Configure make_questions to always fail
    mock_make_questions.side_effect = Exception("Always fails")

    with pytest.raises(
            Exception,
            match=f"Operation failed after {MAXIMAL_RETRY_ON_ERROR + 1} retries"
    ):
        texts_multiple_recall("expected", "given", 1, 1)

    # Verify make_questions was called MAXIMAL_RETRY_ON_ERROR + 1 times
    assert mock_make_questions.call_count == MAXIMAL_RETRY_ON_ERROR + 1
