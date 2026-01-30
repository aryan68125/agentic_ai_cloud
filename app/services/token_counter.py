class TokenCounter:
    @staticmethod
    def count(text: str) -> int:
        if not text:
            return 0
        # TEMP / naive implementation
        return len(text.split())