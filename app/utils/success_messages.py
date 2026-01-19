from enum import Enum

class PromptApiSuccessMessages(Enum):

    # API related success messages
    PROCESSED_PROMPT = "Prompt processed successfully!"
    AI_RESPONSE_PROCESSING_EXTRACT_CONTENT = "Content extraction from hugging face response successfull!"
    AI_RESPONSE_PROCESSING_EXTRACT_API_USAGE = "AI api usage extracted successfully!"
    AI_RESPONSE_NORMALIZATION = "Response normalization successfull!"

class HuggingFaceAIModelAPISuccessMessage(Enum):
    FETCH_LIST_OF_AI_MODELS = "List of ai models fetched successfully!"
    