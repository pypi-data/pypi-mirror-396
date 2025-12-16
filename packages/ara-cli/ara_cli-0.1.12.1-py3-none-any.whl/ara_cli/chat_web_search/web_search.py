import litellm
from ara_cli.prompt_handler import LLMSingleton


def is_web_search_supported(default_llm) -> bool:

    return litellm.utils.supports_web_search(model=default_llm)


def get_supported_models_message(model) -> str:
    return (
        f"Web search is not supported by the current default model. {model}\n"
        "Please choose one of the following models:\n"
        "==OpenAI==\n"
        "\tgpt-4o-search-preview\n"
        "==Anthropic==\n"
        "\tclaude-3-5-sonnet-latest, claude-3-5-sonnet-20241022\n"
        "\tclaude-3-5-haiku-latest, claude-3-5-haiku-20241022\n"
        "\tclaude-3-7-sonnet-20250219\n"
        "==More==\n"
        "https://docs.litellm.ai/docs/completion/web_search#which-search-engine-is-used"
        "\n"
    )


def perform_web_search_completion(query: str):
    """
    Performs a web search using litellm.completion with a web_search_preview tool.
    Streams the response.
    """
    chat_instance = LLMSingleton.get_instance()
    config_parameters = chat_instance.get_config_by_purpose("default")
    config_parameters.pop("provider", None)

    if not is_web_search_supported(config_parameters.get("model")):
        return get_supported_models_message()

    messages = [{"role": "user", "content": query}]

    completion = litellm.completion(
        **config_parameters,
        messages=messages,
        stream=True,
        web_search_options={"search_context_size": "medium"},
    )
    yield from completion
