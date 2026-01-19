# import fast api libraries
from fastapi import HTTPException, status

# import models
from app.models.prompt_api_models.services_class_response_models import ProcessPromptServiceClassResponse

# import logging utility
from app.utils.logger import LoggerFactory
from app.utils.success_messages import PromptApiSuccessMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ProcessPromptService:
    def __init__(self,hugging_face_auth_token):
        self.hugging_face_auth_token = hugging_face_auth_token

    def process_prompt(self,request) -> ProcessPromptServiceClassResponse:
        try:
            info_logger.info(f"ProcessPromptService.process_prompt | This class hit was a success! ")
            debug_logger.debug(f"ProcessPromptService.process_prompt | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")
            return ProcessPromptServiceClassResponse(
                status=True,
                message=PromptApiSuccessMessages.PROCESSED_PROMPT.value,
                data={
                    "test":"data"
                }
            )
        except Exception as e:
            return ProcessPromptServiceClassResponse(
                status=False,
                message=str(e)
            )