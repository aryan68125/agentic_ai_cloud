# import fast api libraries
from fastapi import HTTPException, status

# import library required for making request to hugging face
import httpx

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
    def __init__(self,hugging_face_auth_token,HF_API_URL):
        self.hugging_face_auth_token = hugging_face_auth_token
        self.HF_API_URL = HF_API_URL

    async def process_prompt(self,request) -> ProcessPromptServiceClassResponse:
        try:
            info_logger.info(f"ProcessPromptService.process_prompt | This class hit was a success! ")
            debug_logger.debug(f"ProcessPromptService.process_prompt | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")
            
            headers = {"Authorization": f"Bearer {self.hugging_face_auth_token}"}
            
            body = {
                "model": request.ai_model,
                "messages": [
                    # {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.prompt_message}
                ]
            }

            debug_logger.debug(f"ProcessPromptService.process_prompt | make request to hugging face | HEADERS = {headers} , BODY = {body}")
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.HF_API_URL, json=body, headers=headers)
                debug_logger.debug(f"ProcessPromptService.process_prompt | executing async with httpx.AsyncClient() | hugging_face_response = {resp}")
                resp.raise_for_status()
                data = resp.json()
            
            return ProcessPromptServiceClassResponse(
                status=True,
                message=PromptApiSuccessMessages.PROCESSED_PROMPT.value,
                data={
                    "response_from_hugging_face":data
                }
            )
        except Exception as e:
            error_logger.error(f"ProcessPromptService.process_prompt | error = {str(e)}")
            return ProcessPromptServiceClassResponse(
                status=False,
                message=str(e)
            )
        

"""
response from hugging face = 
{
  "status": 200,
  "message": "Prompt processed successfully!",
  "data": {
    "response_from_hugging_face": {
      "id": "83132744aef24d6bbb4df0d48f9d2237",
      "object": "chat.completion",
      "created": 1768814775,
      "model": "meta-llama/llama-3.1-8b-instruct",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "This is the beginning of our conversation. I'm happy to chat with you, but I don't have any previous messages from you to refer to. I'm a large language model, and I don't retain any information about previous conversations or users. Each time you interact with me, it's a new conversation. What would you like to talk about?"
          },
          "finish_reason": "stop",
          "content_filter_results": {
            "hate": {
              "filtered": false
            },
            "self_harm": {
              "filtered": false
            },
            "sexual": {
              "filtered": false
            },
            "violence": {
              "filtered": false
            },
            "jailbreak": {
              "filtered": false,
              "detected": false
            },
            "profanity": {
              "filtered": false,
              "detected": false
            }
          }
        }
      ],
      "usage": {
        "prompt_tokens": 51,
        "completion_tokens": 72,
        "total_tokens": 123,
        "prompt_tokens_details": null,
        "completion_tokens_details": null
      },
      "system_fingerprint": ""
    }
  }
}
"""