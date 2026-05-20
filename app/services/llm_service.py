from llama_cpp import Llama

from app.core.config import get_settings


class LlmService:
    _llm: Llama | None = None

    @classmethod
    def _get_model(cls) -> Llama:
        if cls._llm is None:
            settings = get_settings()
            cls._llm = Llama(
                model_path=settings.llm_model_path,
                n_ctx=512,
                n_threads=4,
            )
        return cls._llm

    async def ask(self, prompt: str) -> str:
        model = self._get_model()
        result = model(f"User: {prompt}\nAssistant:", max_tokens=300, stream=False)
        return result["choices"][0]["text"].strip()
