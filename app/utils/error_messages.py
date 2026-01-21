from enum import Enum

class PromptApiErrorMessages(Enum):
    # default server errors
    INTERNAL_SERVER_ERROR = "Internal server error"

    # Field related errors
    USER_PROMPT_EMPTY = "User prompt cannot be empty!"
    SYSTEM_PROMPT_EMPTY = "System prompt cannot be empty!"

class AgentApiErrorMessages(Enum):
    # field erros
    AI_AGENT_NAME_EMPTY = "AI agent name cannot be empty!"
    AI_AGENT_ID_EMPTY = "AI agent id cannot be empty!"
    AI_AGENT_NAME_OR_ID_REQUIRED = "Both AI agent name and AI agent id cannot be empty! atleast one of them is required!"

    UNDEFINED_DB_OPERATION_TYPE = "Wrong operation type! aborting operation"

    # db operation errors
    AGENT_ID_NOT_FOUND = "Agent not found"
    