from fastapi import HTTPException, status, BackgroundTasks
import uuid

from app.models.prompt_api_models.response_models import PromptResponse

# import common success and error messages
from app.utils.error_messages import PromptApiErrorMessages
from app.utils.success_messages import PromptApiSuccessMessages

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptController:
    def __init__(self):
        pass

    def process_prompt(self, request) -> PromptResponse:
        try:
            prompt_message = request.prompt_message
            info_logger.info(f"PromptController.process_prompt | Started to process prompt | prompt_message = {prompt_message}")
            return PromptResponse(
                status = status.HTTP_200_OK,
                message = PromptApiSuccessMessages.PROCESSED_PROMPT.value
            )
        except Exception as e:
            error_logger.error(f"PromptController.process_prompt | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
