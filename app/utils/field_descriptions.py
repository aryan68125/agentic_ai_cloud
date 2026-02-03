from enum import Enum 

class PromptRequestFieldDescriptions(Enum):
    # IngestionRequest model field descriptions
    AI_MODEL = "Enter the ai model you want to use"
    USER_PROMPT_MESSAGE = "Enter your prompt here!"
    USER_PROMPT_ID = "Enter the primay key of the user_promp record you want to update"
    USER_PROMPT_PK = "Enter the primary key of the user_prompt record from the user prompt table"
    LIMIT = "This field allows you to set the number of chats you will get per window/api call (batch size per api call)"
    BEFORE_ID = "This enables you to get older user prompts from the database"

class SystemPromptRequestFieldDescription(Enum):
    SYSTEM_PROMPT_MESSAGE = "System prompt text (can be very long) this will be used to configure LLM"
    AGENT_ID_MESSAGE = "Enter the agent_id for whome you are trying to set the system prompt here!"

class AgentRequestFieldDescription(Enum):
    AI_AGENT_NAME = "Enter the ai agent name here!"
    AI_AGENT_ID = "Enter the AI agent ID"
    PAGE_NUMBER = "Enter the page number"
    PAGE_SIZE = "Page size is the number of records you want to show per page"

class LLMPromptResponseClassRequestFieldDescription(Enum):
    LLM_RESPONSE_ID = "Enter primary key for the llm response"
    LLM_RESPONSE_TEXT = "Enter the llm user_prompt response from hugging face here"

class SetAgentToolToAnAgentRequestFieldDescription(Enum):
    AI_AGENT_TOOL_NAME = "Enter the tool name that you want your agent to use"
    AGENT_TOOL_ATTACHMENT_ID = "Enter the pk of record that stores the tool is attached to the agent"
    