from langchain_ollama import ChatOllama

from app.config import settings


class LLMService:
    """
    Local LLM service using Ollama through LangChain.
    """

    def __init__(
        self,
        model: str | None = None,
    ):
        self.llm = ChatOllama(
            model=model or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
            num_predict=600,
            reasoning=False
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