from enum import Enum

class PromptApiSuccessMessages(Enum):
    # default server errors
    INTERNAL_SERVER_ERROR = "Internal server error"

    # Field related errors
    PROMPT_EMPTY = "Prompt cannot be empty!"
    