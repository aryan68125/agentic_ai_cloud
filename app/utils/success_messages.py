from enum import Enum

class PromptApiSuccessMessages(Enum):

    # user prompt API related success messages
    PROCESSED_PROMPT = "Prompt processed successfully!"
    AI_RESPONSE_PROCESSING_EXTRACT_CONTENT = "Content extraction from hugging face response successfull!"
    AI_RESPONSE_PROCESSING_EXTRACT_API_USAGE = "AI api usage extracted successfully!"
    AI_RESPONSE_NORMALIZATION = "Response normalization successfull!"

    # system prompt API related success messages
    SYSTEM_PROMPT_INSERTED = "System prompt inserted successfully!"
    SYSTEM_PROMPT_UPDATED = "System prompt updated successfully!"
    SYSTEM_PROMPT_DELETED = "System prompt delete success!"
    SYSTEM_PROMPT_FETCHED = "System prompt fetched successfully!"

class UserPromptApiSuccessMessages(Enum):
    # user prompt API success messages
    USER_PROMPT_INSERTED = "User prompt inserted successfully!"
    USER_PROMPT_UPDATED = "User prompt updated successfully!"
    USER_PROMPT_DELETED = "User prompt deleted successfully!"
    USER_PROMPT_FETCHED = "User prompt fetched successfully!"

class HuggingFaceAIModelAPISuccessMessage(Enum):
    FETCH_LIST_OF_AI_MODELS = "List of ai models fetched successfully!"

    # llm process user prompt messages
    LLM_RESPONSE_INSERT = "LLM response inserted successfully1"
    LLM_USER_PROMPT_SUCCESS = "LLm processed the user_prompt successfully!"

class AiAgentApiSuccessMessage(Enum):
    AGENT_NAME_INSERTED = "AI Agent name inserted successfully!"
    AGENT_NAME_UPDATED = "AI Agent name updated successfully!"
    AGENT_NAME_DELETED = "AI Agent name delete success!"
    AGENT_NAME_FETCHED = "AI Agent name fetched successfully!"