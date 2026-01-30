from fastapi import HTTPException, status, BackgroundTasks

from app.models.api_request_response_model.response_models import (APIResponse, APIResponseMultipleData)

# import common success and error messages
from app.utils.error_messages import PromptApiErrorMessages
from app.utils.success_messages import HuggingFaceAIModelAPISuccessMessage

# load hugging face ai model list
from app.utils.hugging_face_ai_model_enum import HuggingFaceModelList

# import logging utility
from app.utils.logger import LoggerFactory

# import services
from app.services.process_hugging_face_ai_prompt import ProcessHuggingFaceAIPromptService

# load project configurations
from app.configs.config import ProjectConfigurations

# db orm related imports
from sqlalchemy.orm import Session

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class HuggingFaceAIModelController:

    def __init__(self, db: Session):
        self.db = db
        self.process_prompt_service_obj = ProcessHuggingFaceAIPromptService(hugging_face_auth_token=ProjectConfigurations.HUGGING_FACE_AUTH_TOKEN.value,HF_API_URL = ProjectConfigurations.HF_API_URL.value, db=db)

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
    
    async def process_hugging_face_prompt_request(self, request) -> APIResponse:
        try:
            info_logger.info(f"HuggingFaceAIModelController.process_hugging_face_prompt_request | Started to process user prompt | user_prompt = {request.user_prompt}")
            result = await self.process_prompt_service_obj.process_user_prompt_llm(request=request) 
            if not result.status:
                return APIResponse(
                    status=result.status_code,
                    message=result.message
                )
            return APIResponse(
                status = status.HTTP_200_OK,
                message = result.message,
                data=result.data
            )
        except HTTPException:
            raise
        except Exception as e:
            error_logger.error(f"HuggingFaceAIModelController.process_hugging_face_prompt_request | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    def reset_huggingface_model_context(self,request) -> APIResponse:
        try:
            info_logger.info(f"HuggingFaceAIModelController.reset_huggingface_model_context | Reset ai agent context | agent_id = {request.agent_id}")
            result = self.process_prompt_service_obj.reset_agent(request=request)
            if not result.status:
                return APIResponse(
                    status=result.status_code,
                    message=result.message
                )
            return APIResponse(
                status = status.HTTP_200_OK,
                message = result.message,
                data=result.data
            )
        except Exception as e:
            error_logger.error(f"HuggingFaceAIModelController.reset_huggingface_model_context | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
