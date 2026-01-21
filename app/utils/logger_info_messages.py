from enum import Enum 

class LoggerInfoMessages(Enum):
    API_HIT_SUCCESS = "Success check ok!"

"""
This enum of urls is only used in info type logger and is not used by fast api for api routing
"""
class PromptApiUrls(Enum):
    FAST_API_HEALTH_CHECK_URL = "/health"

    PROMPT_API_URL = "/process/prompt"

class HuggingFaceAPIUrls(Enum):
    HUGGING_FACE_GET_AI_MODELS = "/hugging_face/get_ai_models"

class AgentApiUrls(Enum):
    CREATE_AGENT_API_URL = "/process/agent/create"

