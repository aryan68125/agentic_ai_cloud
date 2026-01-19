from enum import Enum 

class LoggerInfoMessages(Enum):
    API_HIT_SUCCESS = "Success check ok!"

"""
This enum of urls is only used in info type logger and is not used by fast api for api routing
"""
class PromptApiUrls(Enum):
    FAST_API_HEALTH_CHECK_URL = "/health"

    PROMPT_API_URL = "/api/prompt_api"

