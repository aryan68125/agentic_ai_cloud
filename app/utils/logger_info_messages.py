from enum import Enum 

class LoggerInfoMessages(Enum):
    API_HIT_SUCCESS = "Success check ok!"

"""
This enum of urls is only used in info type logger and is not used by fast api for api routing
"""
class PromptApiUrls(Enum):
    FAST_API_HEALTH_CHECK_URL = "/health"
    PROMPT_API_URL = "/process/user_prompt"

class UserPromptApiUrls(Enum):
    CREATE_USER_PROMPT_API_URL = "/process/user_prompt/create"
    UPDATE_USER_PROMPT_API_URL = "/process/user_prompt/update"
    DELETE_USER_PROMPT_API_URL = "/process/user_prompt/delete"
    GET_USER_PROMPT_API_URL = "/process/user_prompt/get"

class SystemPromptApiUrls(Enum):
    CREATE_SYSTEM_PROMPT_API_URL = "/process/system_prompt/create"
    UPDATE_SYSTEM_PROMPT_API_URL = "/process/system_prompt/update"
    DELETE_SYSTEM_PROMPT_API_URL = "/process/system_prompt/delete"
    GET_SYSTEM_PROMPT_API_URL = "/process/system_prompt/get"

class HuggingFaceAPIUrls(Enum):
    HUGGING_FACE_GET_AI_MODELS = "/process/hugging_face/get_models"

class AgentApiUrls(Enum):
    CREATE_AGENT_API_URL = "/process/agent/create"
    UPDATE_AGENT_API_URL = "/process/agent/update"
    DELETE_AGENT_API_URL = "/process/agent/delete"
    GET_AGENT_API_URL = "/process/agent/get"

