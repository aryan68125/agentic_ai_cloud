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

class LLmPromptResponseErrorMessage(Enum):
    LLM_PROMPT_RESPONSE_EMPTY = "LLM prompt respose cannot be empty"
    LLM_RESPONSE_NOT_FOUND = "No LLM response found in the database"

class HuggingFaceAIModelAPIErrorMessage(Enum):
    LLM_PROMPT_HUGGING_FACE_ERROR = "Invalid LLM response: content missing or not a string"
    HUGGING_FACE_LLM_API_TIMEOUT = "LLM response timed out. Model is slow or overloaded."
    LLM_CONTEXT_LIMIT_EMPTY = "Limit for the llm context cannot be less than or equal to zero or None"

class AIAgentToolApiErrorMessage(Enum):
    AGENT_TOOL_NAME_EMPTY = "Agent tool name cannot be empty!"
    AGENT_TOOL_NAME_INVALID = "Agent tool name entered is invalid!"

    AGENT_TOOL_ATTACHMENT_ID = "Agent tool attachment id must not be empty!"
    AGENT_TOOL_IS_NOT_ATTACHED_ERR = "The tool you are trying to detach is not attached in the first place!"
    NO_TOOLS_ATTACHED_TO_THE_AGENT = "No tool is attached to the agent!"
    