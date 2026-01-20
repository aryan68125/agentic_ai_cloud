from enum import Enum

class PromptApiErrorMessages(Enum):
    # default server errors
    INTERNAL_SERVER_ERROR = "Internal server error"

    # Field related errors
    USER_PROMPT_EMPTY = "User prompt cannot be empty!"
    SYSTEM_PROMPT_EMPTY = "System prompt cannot be empty!"
    