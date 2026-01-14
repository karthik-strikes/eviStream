"""
Centralized LLM configuration for eviStream.
All model initialization happens here.
"""

import dspy
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from core.config import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE

load_dotenv()


def get_dspy_model(
    model_name: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE
):
    """
    Get and configure DSPy model.

    Args:
        model_name: LLM model identifier
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature

    Returns:
        Configured DSPy LM instance
    """
    lm = dspy.LM(model_name, max_tokens=max_tokens, temperature=temperature)
    dspy.configure(lm=lm)
    return lm


# Initialize DSPy with default settings on module load
get_dspy_model()


# Centralized LangChain model configuration
def get_langchain_model(
    model_name: str = "google_genai:gemini-3-pro-preview",
    temperature: float = 0.2,
    max_tokens: int = 4000
):
    """
    Get configured LangChain model for code generation tasks.

    Args:
        model_name: LLM model identifier
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response
        request_timeout: Request timeout in seconds

    Returns:
        Configured LangChain ChatModel instance
    """
    return init_chat_model(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
