from pydantic import BaseModel, Field, model_validator
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from app.utils.error_messages import (PromptApiErrorMessages, SystemPromptApiErrorMessages, AgentApiErrorMessages)
from app.utils.field_descriptions import (PromptRequestFieldDescriptions, AgentRequestFieldDescription, SystemPromptRequestFieldDescription, LLMPromptResponseClassRequestFieldDescription)

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

# This is only used in get requests
class LLMPromptResponseClassRequest(BaseModel):
    agent_id: Optional[str] = Field(default=None, description=AgentRequestFieldDescription.AI_AGENT_ID.value)
    id : Optional[int] = Field(default=None, description=LLMPromptResponseClassRequestFieldDescription.LLM_RESPONSE_ID.value)
    llm_user_prompt_id : Optional[int] = Field(default=None,description = PromptRequestFieldDescriptions.USER_PROMPT_PK.value)
    llm_prompt_response : Optional[int] = Field(default=None,description = LLMPromptResponseClassRequestFieldDescription.LLM_RESPONSE_TEXT.value)
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="Number of messages to fetch")
    before_id: Optional[int] = Field(default=None, description="Cursor for infinite scroll")