from enum import Enum

class PromptApiSuccessMessages(Enum):

    # user prompt API related success messages
    PROCESSED_PROMPT = "Prompt processed successfully!"
    AI_RESPONSE_PROCESSING_EXTRACT_CONTENT = "Content extraction from hugging face response successfull!"
    AI_RESPONSE_PROCESSING_EXTRACT_API_USAGE = "AI api usage extracted successfully!"
    AI_RESPONSE_NORMALIZATION = "Response normalization successfull!"

    # system prompt API related success messages
    SYSTEM_PROMPT_SAVED = "System prompt saved successfully!"

class HuggingFaceAIModelAPISuccessMessage(Enum):
    FETCH_LIST_OF_AI_MODELS = "List of ai models fetched successfully!"

class AiAgentApiSuccessMessage(Enum):
    AGENT_NAME_INSERTED = "AI Agent name inserted successfully!"
    AGENT_NAME_UPDATED = "AI Agent name updated successfully!"
    AGENT_NAME_DELETED = "AI Agent name delete success!"
    AGENT_NAME_FETCHED = "AI Agent name fetched successfully!"
    