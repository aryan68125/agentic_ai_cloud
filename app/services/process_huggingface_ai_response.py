# import logging utility
from app.utils.logger import LoggerFactory
from app.utils.success_messages import PromptApiSuccessMessages

# import models
from app.models.class_return_model.services_class_response_models import ProcessPromptResponseServiceClassResponse

# import messages
from app.utils.success_messages import PromptApiSuccessMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ProcessPromptResponseService:
    @staticmethod
    def extract_content(hf_response: dict) -> ProcessPromptResponseServiceClassResponse:
        info_logger.info(f"ProcessPromptResponseService.extract_content | Extract assistant message content from Hugging Face chat completion response.")
        try:
            prompt_output = hf_response["choices"][0]["message"]["content"]
            debug_logger.debug(f"ProcessPromptResponseService.extract_content | prompt_output = {prompt_output}")
            return ProcessPromptResponseServiceClassResponse(
                status = True,
                message = PromptApiSuccessMessages.AI_RESPONSE_PROCESSING_EXTRACT_CONTENT.value,
                data = {
                    "content":prompt_output
                }
            )
        except Exception as e:
            error_logger.error(f"ProcessPromptResponseService.extract_content | error = {str(e)}")
            return ProcessPromptResponseServiceClassResponse(
                status = False,
                message = str(e)
            )

    @staticmethod
    def extract_usage(hf_response: dict) -> ProcessPromptResponseServiceClassResponse:
        try:
            info_logger.info(f"ProcessPromptResponseService.extract_usage | Extract token usage information (optional).")
            usage = hf_response.get("usage", {})
            return ProcessPromptResponseServiceClassResponse(
                status = True,
                message = PromptApiSuccessMessages.AI_RESPONSE_PROCESSING_EXTRACT_API_USAGE.value,
                data = {
                    "usage":usage
                }
            )
        except Exception as e:
            error_logger.error(f"ProcessPromptResponseService.extract_usage | error = {str(e)}")
            return ProcessPromptResponseServiceClassResponse(
                status = False,
                message = str(e)
            )

    @staticmethod
    def normalize(hf_response: dict) -> ProcessPromptResponseServiceClassResponse:
        try:
            info_logger.info(f"ProcessPromptResponseService.normalize | Return a normalized response suitable for frontend | content = {content}, usage = {usage}")
            content = ProcessPromptResponseService.extract_content(hf_response)
            usage = ProcessPromptResponseService.extract_usage(hf_response)

            return ProcessPromptResponseServiceClassResponse(
                status = True,
                message = PromptApiSuccessMessages.AI_RESPONSE_NORMALIZATION.value,
                data = {
                    "content": content,
                    "usage": usage,
                    "model": hf_response.get("model"),
                    "hf_completion_id": hf_response.get("id"),
                }
            )
        except Exception as e:
            error_logger.error(f"ProcessPromptResponseService.normalize | error = {str(e)}")
            return ProcessPromptResponseServiceClassResponse(
                status = False,
                message = str(e)
            )
 
