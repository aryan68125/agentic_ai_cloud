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
    LLM_RESPONSE_DELETE = "All LLMs responses deleted successfully!"
    LLM_CONTEXT_RESET_SUCCESS = "LLM context window reset successfull"

    # llm context management messages
    LLM_CONTEXT_FETCHED = "LLM context fetched successfully!"

class AiAgentApiSuccessMessage(Enum):
    AGENT_NAME_INSERTED = "AI Agent name inserted successfully!"
    AGENT_NAME_UPDATED = "AI Agent name updated successfully!"
    AGENT_NAME_DELETED = "AI Agent name delete success!"
    AGENT_NAME_FETCHED = "AI Agent name fetched successfully!"

class AIAgentToolApiSuccessMessage(Enum):
    AI_AGENT_TOOL_LIST_FETCHED = "Ai agent tool list fetched successfully!"
    SET_AGENT_TOOL_SUCCESS = "Tool attached successfully to this ai agent!"
    TOOL_ALREADY_ATTACHED = "Tool already attached. Timestamp updated."
    TOOL_ATTACHED = "Tool attached to agent."

    TOOL_DETACHED_FROM_THE_AGENT_SUCCESS = "Tool detached from the agent successfully!"
    TOOLS_ATTCHED_TO_AGENT_LIST_FETCH = "Tools attached to the agent is fetched successfully!"

class ResearchToolSuccessMessages(Enum):
    MAIN_LLM_QUERY_PROCESSED = "Query of the main llm is processed successfully!"
    
    # db operation messages
    VERIFIED_PAYLOAD_SAVED = "Verified payload saved successfully!"
    VERIFIED_PAYLOAD_DELETED = "Verified payload deleted successfully!"
    