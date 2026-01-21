from enum import Enum 

class PromptRequestFieldDescriptions(Enum):
    # IngestionRequest model field descriptions
    AI_MODEL = "Enter the ai model you want to use"
    USER_PROMPT_MESSAGE = "Enter your prompt here!"

class AgentRequestFieldDescription(Enum):
    AI_AGENT_NAME = "Enter the ai agent name here!"
    AI_AGENT_ID = "Enter the AI agent ID"