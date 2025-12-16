# Test for texts_compare_fixture
# Expected behavior: Verifies that the texts_score fixture is properly registered and works in pytest
def test_texts_compare_fixture(pytester):
    """Make sure that pytest accepts texts_compare fixture."""
    from pytest_texts_score.communication import get_config

    # Get config from current pytest session
    config = get_config()

    # Create a temporary pytest test module that uses the texts_score fixture
    pytester.makepyfile("""
        def test_sth(texts_score):
            texts_score["expect_f1_equal"]("foo","foo",1.0)
    """)

    # Run pytest with the configuration from the running session
    # Pass all LLM configuration parameters to ensure proper setup
    result = pytester.runpytest(
        '-v',
        f'--llm-api-key={config._llm_api_key}',
        f'--llm-endpoint={config._llm_endpoint}',
        f'--llm-deployment={config._llm_deployment}',
        f'--llm-model={config._llm_model}',
        f'--llm-api-version={config._llm_api_version}',
        f'--llm-max-tokens={config._llm_max_tokens}',
    )

    # Verify that the test passed - fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED*',
    ])

    # Verify that we get a '0' exit code for the testsuite (success)
    assert result.ret == 0


# Test for direct import functionality
# Expected behavior: Verifies that functions can be imported directly and used without fixture
def test_import(pytester):
    """Make sure that import works."""
    from pytest_texts_score.communication import get_config

    # Get config from current pytest session
    config = get_config()

    # Create a temporary pytest test module that imports function directly
    pytester.makepyfile("""
    from pytest_texts_score import texts_expect_f1_equal

    def test_sth():
        texts_expect_f1_equal("foo", "foo", 1.0)
    """)

    # Run pytest with the configuration from the running session
    # Pass all LLM configuration parameters to ensure proper setup
    result = pytester.runpytest(
        '-v',
        f'--llm-api-key={config._llm_api_key}',
        f'--llm-endpoint={config._llm_endpoint}',
        f'--llm-deployment={config._llm_deployment}',
        f'--llm-model={config._llm_model}',
        f'--llm-api-version={config._llm_api_version}',
        f'--llm-max-tokens={config._llm_max_tokens}',
    )

    # Verify that the test passed - fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED*',
    ])

    # Verify that we get a '0' exit code for the testsuite (success)
    assert result.ret == 0
