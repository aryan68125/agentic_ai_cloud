# import fast api libraries
from fastapi import HTTPException, status

# import library required for making request to hugging face
import httpx

# import models
from app.models.prompt_api_models.services_class_response_models import ProcessPromptServiceClassResponse

# import helper sub services
from app.services.process_huggingface_ai_response import ProcessPromptResponseService

# import logging utility
from app.utils.logger import LoggerFactory
from app.utils.success_messages import PromptApiSuccessMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ProcessPromptService:
    def __init__(self,hugging_face_auth_token,HF_API_URL):
        self.hugging_face_auth_token = hugging_face_auth_token
        self.HF_API_URL = HF_API_URL
        self.process_response_service = ProcessPromptResponseService()

    async def process_prompt(self,request) -> ProcessPromptServiceClassResponse:
        try:
            info_logger.info(f"ProcessPromptService.process_prompt | This class hit was a success! ")
            debug_logger.debug(f"ProcessPromptService.process_prompt | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")
            
            headers = {"Authorization": f"Bearer {self.hugging_face_auth_token}"}
            
            # Below is the explaination on how the body should be constructed before sending it to the hugging face LLM
            # body = {
            #     "model": request.ai_model,
            #     "messages": [
            #         """
            #             Here you will tell the model how to behave
            #         """
            #         # {"role": "system", "content": "You are a helpful assistant."},
            #         """
            #             Here the end user will write the prompt for it to gain answers from the LLM
            #         """
            #         {"role": "user", "content": request.user_prompt}
            #     ]
            # }

            body = {
                "model": request.ai_model,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt}
                ]
            }

            debug_logger.debug(f"ProcessPromptService.process_prompt | make request to hugging face | HEADERS = {headers} , BODY = {body}")
            # make request to hugging face api_model
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.HF_API_URL, json=body, headers=headers)
                debug_logger.debug(f"ProcessPromptService.process_prompt | executing async with httpx.AsyncClient() | hugging_face_response = {resp}")
                resp.raise_for_status()
                debug_logger.debug(f"ProcessPromptService.process_prompt | response data from hugging face resp.json() | data = {resp.json()}")
                data = resp.json()

            # process response from hugging face ai_model
            result_process_response_service = self.process_response_service.extract_content(data)
            if not result_process_response_service:
                return ProcessPromptServiceClassResponse(
                    status = False,
                    message = result_process_response_service.message
                )
            return ProcessPromptServiceClassResponse(
                status=True,
                message=PromptApiSuccessMessages.PROCESSED_PROMPT.value,
                data=result_process_response_service.data
            )
        except Exception as e:
            error_logger.error(f"ProcessPromptService.process_prompt | error = {str(e)}")
            return ProcessPromptServiceClassResponse(
                status=False,
                message=str(e)
            )