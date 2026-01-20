from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from loguru import logger
import os

class LLMFactory:
    @staticmethod
    def create_llm(provider: str, model_name: str = None):
        """
        Creates and returns an LLM instance based on the provider.
        """
        provider = provider.lower().strip()
        logger.info(f"Initializing LLM provider: {provider}, model: {model_name}")

        if provider == "openai":
            model = model_name if model_name else "gpt-4"
            return ChatOpenAI(model=model, temperature=0)
        
        elif provider == "gemini":
            model = model_name if model_name else "gemini-pro"
            if not os.getenv("GOOGLE_API_KEY"):
                logger.warning("GOOGLE_API_KEY not found in environment variables.")
            return ChatGoogleGenerativeAI(model=model, temperature=0, convert_system_message_to_human=True)
        
        elif provider == "ollama":
            model = model_name if model_name else "llama3"
            # Ollama usually runs locally on http://localhost:11434
            return ChatOllama(model=model, temperature=0)
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
