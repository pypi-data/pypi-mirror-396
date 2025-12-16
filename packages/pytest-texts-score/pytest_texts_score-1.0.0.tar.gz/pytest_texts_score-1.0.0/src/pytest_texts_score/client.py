import pytest
from openai import AzureOpenAI
from typing import Optional

# This global variable holds the singleton-like client instance.
# It's initialized once by `init_client` and then retrieved by `get_client`.
_client_instance: Optional[AzureOpenAI] = None


def init_client(config: pytest.Config) -> AzureOpenAI:
    """
    Initialize and store the global AzureOpenAI client.

    This function uses the provided pytest configuration object to instantiate
    the ``AzureOpenAI`` client. The created client instance is stored in a
    global variable for later retrieval via ``get_client()``.

    :param config: The pytest config object containing LLM settings.
    :type config: pytest.Config
    :return: The newly created ``AzureOpenAI`` client instance.
    :rtype: AzureOpenAI
    """

    global _client_instance
    _client_instance = AzureOpenAI(
        api_key=config._llm_api_key,
        azure_endpoint=config._llm_endpoint,
        api_version=config._llm_api_version,
        azure_deployment=config._llm_deployment,
    )
    return _client_instance


def get_client() -> AzureOpenAI:
    """
    Return the initialized AzureOpenAI client.

    Retrieves the globally stored ``AzureOpenAI`` client instance. It is
    designed to be called after ``init_client()`` has been executed,
    typically within a pytest fixture.

    :return: The initialized ``AzureOpenAI`` client instance.
    :rtype: AzureOpenAI
    :raises RuntimeError: If the client has not been initialized by calling ``init_client()`` first.
    """
    if _client_instance is None:
        raise RuntimeError("Client not initialized. Call init_client() first.")
    return _client_instance
