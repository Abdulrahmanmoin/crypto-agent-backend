import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# Load environment variables
load_dotenv()

# Static client for direct OpenAI-like calls
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_gemini_model(model_name: str = "gemini-2.5-flash"):
    """
    Configures and returns a Gemini model instance using the OpenAI-compatible endpoint.
    """
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=gemini_client
    )

# Static instance for default use
gemini_model = get_gemini_model()
