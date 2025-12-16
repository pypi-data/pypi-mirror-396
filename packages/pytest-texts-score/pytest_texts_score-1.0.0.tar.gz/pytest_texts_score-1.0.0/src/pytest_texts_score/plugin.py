from openai import AzureOpenAI
import pytest
from typing import Callable, Optional

# A global variable to hold the pytest config object.
_global_config: Optional[pytest.Config] = None


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Add command-line and .ini options for LLM configuration to pytest.

    This hook implementation defines various options to configure the Azure
    OpenAI client, such as API key, endpoint, model, and other parameters.
    Options can be provided via the command line or a ``pytest.ini`` file.

    :param parser: The pytest option parser.
    :type parser: pytest.Parser
    :return: None.
    """
    group = parser.getgroup("llm", "Options for Langchain/Azure LLM client")
    # Add CLI options
    group.addoption(
        "--llm-api-key",
        action="store",
        default=None,
        help="API key for Azure OpenAI deployment (overrides ini)",
    )
    group.addoption(
        "--llm-endpoint",
        action="store",
        default=None,
        help="Azure endpoint for the LLM (overrides ini)",
    )
    group.addoption(
        "--llm-api-version",
        action="store",
        default=None,
        help="API version (overrides ini, default: 2024-05-01)",
    )
    group.addoption(
        "--llm-deployment",
        action="store",
        default=None,
        help="Deployment name for the Azure LLM (overrides ini)",
    )
    group.addoption(
        "--llm-max-tokens",
        action="store",
        default=None,
        type=int,
        help="Maximum tokens for LLM responses (overrides ini, default: 8192)",
    )
    group.addoption(
        "--llm-model",
        action="store",
        default=None,
        help="Azure model indetifier (overrides ini)",
    )

    # Add ini options
    parser.addini("llm_api_key",
                  "API key for Azure OpenAI deployment",
                  default=None)
    parser.addini("llm_endpoint", "Azure endpoint for the LLM", default=None)
    parser.addini("llm_deployment",
                  "Deployment name for the Azure LLM",
                  default=None)
    parser.addini("llm_model", "Azure model indetifier", default=None)
    # With defaults
    parser.addini("llm_api_version", "API version", default="2024-05-01")
    parser.addini("llm_max_tokens",
                  "Maximum tokens for LLM responses",
                  default="8192")


def pytest_configure(config: pytest.Config) -> None:
    """
    Resolve LLM config (CLI > ini > default) and initialize the client.

    This hook is called after command line and configuration files are parsed.
    It resolves the final configuration values by prioritizing command-line
    options over ``.ini`` file settings, and then over default values. It
    validates that all required settings are present and then initializes the
    global LLM client.

    :param config: The pytest config object.
    :type config: pytest.Config
    :return: None.
    :raises pytest.UsageError: If any required configuration values are missing.
    """
    from .client import init_client

    # Resolve final values
    config._llm_api_key = config.getoption("--llm-api-key") or config.getini(
        "llm_api_key")
    config._llm_endpoint = config.getoption("--llm-endpoint") or config.getini(
        "llm_endpoint")
    config._llm_api_version = config.getoption(
        "--llm-api-version") or config.getini("llm_api_version")
    config._llm_deployment = config.getoption(
        "--llm-deployment") or config.getini("llm_deployment")
    config._llm_model = config.getoption("--llm-model") or config.getini(
        "llm_model")

    config._llm_max_tokens = config.getoption("--llm-max-tokens")
    if config._llm_max_tokens is None:
        config._llm_max_tokens = int(config.getini("llm_max_tokens"))

    # Validate required fields
    missing = [
        name for name, value in {
            "api_key": config._llm_api_key,
            "endpoint": config._llm_endpoint,
            "api_version": config._llm_api_version,
            "deployment": config._llm_deployment,
            "max_tokens": config._llm_max_tokens,
            "model": config._llm_model,
        }.items() if not value
    ]

    if missing:
        raise pytest.UsageError(
            "[pytest-texts-score] Missing configuration values: "
            f"{', '.join(missing)}. Please provide them via CLI options or pytest.ini.\n\n"
            "Example:\n"
            "  pytest --llm-api-key=... --llm-endpoint=... ...\n\n"
            "or in pytest.ini:\n"
            "[pytest]\n"
            "llm_api_key = ...\n"
            "llm_endpoint = ...\n")

    # Initialize client only when all values are set
    init_client(config)
    global _global_config
    _global_config = config


def get_config() -> pytest.Config:
    """
    Return the initialized pytest configuration object.

    Retrieves the globally stored ``pytest.Config`` object, which contains
    the resolved LLM configuration. This function should be called after
    ``pytest_configure`` has run.

    :return: The pytest config object.
    :rtype: pytest.Config
    :raises RuntimeError: If the configuration has not been initialized.
    """
    if _global_config is None:
        raise RuntimeError("Config not initialized.")
    return _global_config


def pytest_report_header(config: pytest.Config) -> str:
    """
    Add LLM configuration details to the pytest report header.

    This hook provides a custom string to be displayed in the header of the
    test report, showing the resolved LLM configuration parameters for the
    current test run. The API key is masked for security.

    :param config: The pytest config object.
    :type config: pytest.Config
    :return: A string to be included in the report header.
    :rtype: str
    """
    return ("LLM config: "
            f"endpoint={config._llm_endpoint!r}, "
            f"deployment={config._llm_deployment!r}, "
            f"api_version={config._llm_api_version!r}, "
            f"api_key={mask_api_key(config._llm_api_key)}, "
            f"max_tokens={config._llm_max_tokens}, "
            f"model={config._llm_model}")


@pytest.fixture(scope="session")
def texts_score_client() -> AzureOpenAI:
    """
    Provide access to the initialized LLM client as a fixture.

    This session-scoped fixture allows tests to get the configured
    ``AzureOpenAI`` client instance.

    :return: The initialized ``AzureOpenAI`` client.
    :rtype: AzureOpenAI
    """
    from .client import get_client

    return get_client()


@pytest.fixture
def texts_score() -> dict[str, Callable]:
    """
    Provide access to text comparison helper functions as a fixture.

    This fixture returns a dictionary of callable functions for text scoring
    and evaluation. These functions include various aggregation and expectation
    helpers for metrics like F1 score, precision, recall, completeness, and correctness.

    :return: A dictionary mapping function names to callable helper functions.
    :rtype: dict[str, Callable]

    .. note::
        This fixture returns a dictionary of functions rather than exposing them
        globally.
    """
    from .api import (
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
    from .api_wrappers import (
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
        texts_agg_f1_average,
        texts_agg_precision_average,
        texts_agg_recall_average,
        texts_expect_completeness_equal,
        texts_expect_completeness_range,
        texts_expect_correctness_equal,
        texts_expect_correctness_range,
    )

    return {
        "agg_completeness_average": texts_agg_completeness_average,
        "agg_completeness_mean": texts_agg_completeness_mean,
        "agg_completeness_max": texts_agg_completeness_max,
        "agg_completeness_median": texts_agg_completeness_median,
        "agg_completeness_min": texts_agg_completeness_min,
        "agg_correctness_average": texts_agg_correctness_average,
        "agg_correctness_max": texts_agg_correctness_max,
        "agg_correctness_mean": texts_agg_correctness_mean,
        "agg_correctness_median": texts_agg_correctness_median,
        "agg_correctness_min": texts_agg_correctness_min,
        "agg_f1_average": texts_agg_f1_average,
        "agg_f1_max": texts_agg_f1_max,
        "agg_f1_mean": texts_agg_f1_mean,
        "agg_f1_median": texts_agg_f1_median,
        "agg_f1_min": texts_agg_f1_min,
        "agg_precision_average": texts_agg_precision_average,
        "agg_precision_max": texts_agg_precision_max,
        "agg_precision_mean": texts_agg_precision_mean,
        "agg_precision_median": texts_agg_precision_median,
        "agg_precision_min": texts_agg_precision_min,
        "agg_recall_average": texts_agg_recall_average,
        "agg_recall_max": texts_agg_recall_max,
        "agg_recall_mean": texts_agg_recall_mean,
        "agg_recall_median": texts_agg_recall_median,
        "agg_recall_min": texts_agg_recall_min,
        "expect_completeness_equal": texts_expect_completeness_equal,
        "expect_completeness_range": texts_expect_completeness_range,
        "expect_correctness_equal": texts_expect_correctness_equal,
        "expect_correctness_range": texts_expect_correctness_range,
        "expect_f1_equal": texts_expect_f1_equal,
        "expect_f1_range": texts_expect_f1_range,
        "expect_precision_equal": texts_expect_precision_equal,
        "expect_precision_range": texts_expect_precision_range,
        "expect_recall_equal": texts_expect_recall_equal,
        "expect_recall_range": texts_expect_recall_range,
    }


def mask_api_key(key: Optional[str]) -> Optional[str]:
    """
    Mask an API key for safe display.

    Replaces all but the first character of the API key with asterisks (``*``)
    to prevent leaking sensitive information in logs or reports.

    :param key: The API key to mask.
    :type key: Optional[str]
    :return: The masked API key, or ``None`` if the input was ``None``.
    :rtype: Optional[str]
    """
    if not key:
        return None
    return key[0] + "*" * (len(key) - 1)
