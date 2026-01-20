from fastapi import HTTPException, status, BackgroundTasks
import uuid

from app.models.prompt_api_models.response_models import APIResponse

# import common success and error messages
from app.utils.error_messages import PromptApiErrorMessages
from app.utils.success_messages import PromptApiSuccessMessages

# load project configurations
from app.configs.config import ProjectConfigurations

# import logging utility
from app.utils.logger import LoggerFactory

# import services
from app.services.process_prompt import ProcessPromptService

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptController:
    def __init__(self):
        self.process_prompt_service_obj = ProcessPromptService(hugging_face_auth_token=ProjectConfigurations.HUGGING_FACE_AUTH_TOKEN.value,HF_API_URL = ProjectConfigurations.HF_API_URL.value)

    async def process_prompt(self, request) -> APIResponse:
        try:
            info_logger.info(f"PromptController.process_prompt | Started to process prompt | user_prompt = {request.user_prompt}")
            result = await self.process_prompt_service_obj.process_prompt(request=request) 
            if not result.status:
                return APIResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=result.message
                )
            return APIResponse(
                status = status.HTTP_200_OK,
                message = result.message,
                data=result.data

            )
        except Exception as e:
            error_logger.error(f"PromptController.process_prompt | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
