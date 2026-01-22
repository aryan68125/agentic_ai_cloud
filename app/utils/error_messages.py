from enum import Enum

class PromptApiErrorMessages(Enum):
    # default server errors
    INTERNAL_SERVER_ERROR = "Internal server error"

    # Field related errors
    USER_PROMPT_EMPTY = "User prompt cannot be empty!"

    # db operation errors
    SYSTEM_PROMPT_NOT_FOUND = "System prompt not found"

class SystemPromptApiErrorMessages(Enum):
    SYSTEM_PROMPT_EMPTY = "System prompt cannot be empty!"

    # db operation errors
    SYSTEM_PROMPT_NOT_FOUND = "System prompt for AI Agent with the agent_id ({}) is not found in the database"

class AgentApiErrorMessages(Enum):
    # field erros
    AI_AGENT_NAME_EMPTY = "AI agent name cannot be empty!"
    AI_AGENT_ID_EMPTY = "AI agent id cannot be empty!"
    AI_AGENT_NAME_OR_ID_REQUIRED = "Both AI agent name and AI agent id cannot be empty! atleast one of them is required!"
    PAGE_NUMBER_EMPTY = "Page number cannot be empty! when fecthing multiple records from the database"
    PAGE_SIZE_EMPTY = "Page size cannot be empty when fetching multiple records from the database"
    

    UNDEFINED_DB_OPERATION_TYPE = "Wrong operation type! aborting operation"

    # db operation errors
    AGENT_ID_NOT_FOUND = "Agent not found"
    