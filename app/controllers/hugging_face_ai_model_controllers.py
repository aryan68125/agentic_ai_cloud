from fastapi import HTTPException, status, BackgroundTasks
import uuid

from app.models.api_request_response_model.response_models import APIResponse

# import common success and error messages
from app.utils.error_messages import PromptApiErrorMessages
from app.utils.success_messages import HuggingFaceAIModelAPISuccessMessage

# load hugging face ai model list
from app.utils.hugging_face_ai_model_enum import HuggingFaceModelList

# import logging utility
from app.utils.logger import LoggerFactory

# import services
from app.services.process_prompt import ProcessPromptService

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class HuggingFaceAIModelController:

    def get_models(self) -> APIResponse:
        try:
            info_logger.info(f"HuggingFaceAIModelController.get_models | Get all available ai models")
            data = {
                "model_list" : HuggingFaceModelList.model_list.value
            }
            debug_logger.debug(f"HuggingFaceAIModelController.get_models | Get all available ai models | ai_model_list = {data}")
            return APIResponse(
                status = status.HTTP_200_OK,
                message = HuggingFaceAIModelAPISuccessMessage.FETCH_LIST_OF_AI_MODELS.value,
                data=data

            )
        except Exception as e:
            error_logger.error(f"HuggingFaceAIModelController.get_models | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
