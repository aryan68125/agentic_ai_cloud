from pydantic import BaseModel, Field, model_validator
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from app.utils.error_messages import PromptApiErrorMessages
from app.utils.field_descriptions import RequestFieldDescriptions

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptRequest(BaseModel):
    ai_model : str = Field(default="meta-llama/Llama-3.1-8B-Instruct",description=RequestFieldDescriptions.AI_MODEL.value)
    prompt_message : str = Field(default=None, description=RequestFieldDescriptions.PROMPT_MESSAGE.value)

    @model_validator(mode="after")
    def validate_prompt_message(self):
        if not self.prompt_message:
            error_logger.error(f"PromptRequest.validate_prompt_message | error = {PromptApiErrorMessages.PROMPT_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PromptApiErrorMessages.PROMPT_EMPTY.value
            )
        
        return self