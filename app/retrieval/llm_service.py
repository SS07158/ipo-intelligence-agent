from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


class LLMService:
    """
    LLM service supporting both local Ollama and cloud Gemini.

    Provider is selected through settings.llm_provider:
        - ollama
        - gemini
    """

    def __init__(
        self,
        model: str | None = None,
    ):
        provider = settings.llm_provider.lower().strip()

        if provider == "ollama":
            self.llm = ChatOllama(
                model=model or settings.ollama_model,
                base_url=settings.ollama_base_url,
                temperature=0,
                num_predict=600,
                reasoning=False,
            )

        elif provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY is required when LLM_PROVIDER=gemini"
                )

            self.llm = ChatGoogleGenerativeAI(
                model=model or settings.gemini_model,
                google_api_key=settings.gemini_api_key,
                temperature=0,
                max_output_tokens=600,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {settings.llm_provider}. "
                "Use 'ollama' or 'gemini'."
            )

    def generate(
        self,
        messages: list[tuple[str, str]],
    ) -> str:
        """
        Generate a response from the supplied messages.
        """

        response = self.llm.invoke(messages)

        return response.content