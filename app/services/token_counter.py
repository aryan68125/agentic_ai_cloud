from transformers import AutoTokenizer
from threading import Lock

class TokenCounter:
    """
    TokenCounter v2 (Model-Agnostic)

    - Supports ANY Hugging Face model
    - Automatically loads the correct tokenizer
    - Caches tokenizers per model
    - Thread-safe
    """

    _tokenizers: dict[str, AutoTokenizer] = {}
    _lock = Lock()

    @classmethod
    def _get_tokenizer(cls, model_name: str):
        with cls._lock:
            if model_name not in cls._tokenizers:
                cls._tokenizers[model_name] = AutoTokenizer.from_pretrained(
                    model_name,
                    use_fast=True
                )
            return cls._tokenizers[model_name]

    @classmethod
    def count(cls, text: str, model_name: str) -> int:
        if not text:
            return 0

        tokenizer = cls._get_tokenizer(model_name)

        # No special tokens; roles are handled by you
        return len(
            tokenizer.encode(
                text,
                add_special_tokens=False
            )
        )
