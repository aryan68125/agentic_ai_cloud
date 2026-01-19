from fastapi import Request

class FastApiServer:
    @staticmethod
    def get_base_url(request: Request) -> str:
        """
        Returns base URL like:
        http://localhost:8000
        https://api.example.com
        """
        return str(request.base_url).rstrip("/")