from enum import Enum

class PromptApiErrorMessages(Enum):
    # default server errors
    INTERNAL_SERVER_ERROR = "Internal server error"

    # Field related errors
    USER_PROMPT_EMPTY = "User prompt cannot be empty!"

    # db operation errors
    SYSTEM_PROMPT_NOT_FOUND = "System prompt not found"

class SystemPromptApiErrorMessages(Enum):
    # Field errors
    SYSTEM_PROMPT_AND_AI_MODEL_EMPTY = "System prompt field and ai_model field both of them cannot be empty! You have to either provide system_prompt If you wish to update system_prompt or ai_model if you wish to update ai_model"
    SYSTEM_PROMPT_EMPTY = "System prompt field cannot be empty!"
    AI_MODEL_NAME_EMPTY = "AI model name field cannot be empty!"

    # db operation errors
    SYSTEM_PROMPT_NOT_FOUND = "System prompt for AI Agent with the agent_id ({}) is not found in the database"
    SYSTEM_PROMPT_LIST_EMPTY = "No system prompt found in the database"

class UserPromptApiErrorMessages(Enum):
    # Field errors
    USER_PROMPT_EMPTY = "User prompt field cannot be empty!"
    USER_PROMPT_ID_EMPTY = "User prompt ID (Primary key) cannot be empty!"

    # db error
    USER_PROMPT_NOT_FOUND = "User prompt for AI Agent with the agent_id ({}) is not found in the database"
    USER_PROMPTS_NOT_FOUND = "List of user prompts is empty for agent_id ({})"
    USER_PROMPT_NOT_FOUND_MESSAGE = "User prompt not found in the database"

class AgentApiErrorMessages(Enum):
    # field errors
    AI_AGENT_NAME_EMPTY = "AI agent name cannot be empty!"
    AI_AGENT_ID_EMPTY = "AI agent id cannot be empty!"
    AI_AGENT_NAME_OR_ID_REQUIRED = "Both AI agent name and AI agent id cannot be empty! atleast one of them is required!"
    PAGE_NUMBER_EMPTY = "Page number cannot be empty! when fecthing multiple records from the database"
    PAGE_SIZE_EMPTY = "Page size cannot be empty when fetching multiple records from the database"
    AI_AGENT_NAME_AND_AGENT_ID_IS_NOT_REQUIRED = "Ai agent id and Ai agent name is supplied only one is required"
    

    UNDEFINED_DB_OPERATION_TYPE = "Wrong operation type! aborting operation"

    # db operation errors
    AGENT_ID_NOT_FOUND = "Agent not found"
    