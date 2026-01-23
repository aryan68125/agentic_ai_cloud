from enum import Enum 

class PromptRequestFieldDescriptions(Enum):
    # IngestionRequest model field descriptions
    AI_MODEL = "Enter the ai model you want to use"
    USER_PROMPT_MESSAGE = "Enter your prompt here!"
    USER_PROMPT_ID = "Enter the primay key of the user_promp record you want to update"

class SystemPromptRequestFieldDescription(Enum):
    SYSTEM_PROMPT_MESSAGE = "System prompt text (can be very long) this will be used to configure LLM"
    AGENT_ID_MESSAGE = "Enter the agent_id for whome you are trying to set the system prompt here!"

class AgentRequestFieldDescription(Enum):
    AI_AGENT_NAME = "Enter the ai agent name here!"
    AI_AGENT_ID = "Enter the AI agent ID"
    PAGE_NUMBER = "Enter the page number"
    PAGE_SIZE = "Page size is the number of records you want to show per page"