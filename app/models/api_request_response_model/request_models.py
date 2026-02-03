from pydantic import BaseModel, Field, model_validator
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from app.utils.error_messages import (PromptApiErrorMessages, AIAgentToolApiErrorMessage, AgentApiErrorMessages)
from app.utils.field_descriptions import (SetAgentToolToAnAgentRequestFieldDescription, PromptRequestFieldDescriptions, AgentRequestFieldDescription, SystemPromptRequestFieldDescription)

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class UserPromptRequest(BaseModel):
    agent_id : Optional[str] = Field(default_factory=None, description = SystemPromptRequestFieldDescription.AGENT_ID_MESSAGE.value)
    user_prompt : Optional[str] = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_MESSAGE.value)
    user_prompt_id : Optional[int] = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_ID.value)

# This is only used in get requests
class UserPromptQueryParams(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="AI Agent ID")
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="Number of messages to fetch")
    before_id: Optional[int] = Field(default=None, description="Cursor for infinite scroll")
    @model_validator(mode="after")
    def validate_fields(self):
        if not self.agent_id:
            error_logger.error(f"UserPromptQueryParams.validate_fields | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
            )
        return self

class SystemPromptRequest(BaseModel):
    agent_id : str = Field(default_factory=None, description = SystemPromptRequestFieldDescription.AGENT_ID_MESSAGE.value)
    ai_model : Optional[str] = Field(default="meta-llama/Llama-3.1-8B-Instruct",description=PromptRequestFieldDescriptions.AI_MODEL.value)
    system_prompt : Optional[str] = Field(default_factory=None, description = SystemPromptRequestFieldDescription.SYSTEM_PROMPT_MESSAGE.value)
    @model_validator(mode="after")
    def validate_fields(self):
        if not self.agent_id:
            error_logger.error(f"SystemPromptRequest.validate_fields | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
            )
        return self

# This is only used in get requests
class SystemPromptQueryParams(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="AI Agent ID")
    limit:Optional[int] = Field(default=None, description="No records shown in a page")
    before_id:Optional[int] = Field(default=None,description="next record id")

class AgentRequest(BaseModel):
    agent_name : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_NAME.value)
    agent_id : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_ID.value)

class AgentQueryParams(BaseModel):
    agent_name : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_NAME.value)
    agent_id : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_ID.value)
    page: Optional[int] = Field(default_factory=None, description = AgentRequestFieldDescription.PAGE_NUMBER.value)
    page_size: Optional[int] = Field(default_factory=None, description = AgentRequestFieldDescription.PAGE_SIZE.value)

class HuggingFacePromptRequest(BaseModel):
    agent_id : str = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_ID.value)
    user_prompt : str = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_MESSAGE.value)

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.agent_id:
            error_logger.error(f"HuggingFacePromptRequest.validate_fields | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
            )
        if not self.user_prompt:
            error_logger.error(f"HuggingFacePromptRequest.validate_fields | error = {PromptApiErrorMessages.USER_PROMPT_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PromptApiErrorMessages.USER_PROMPT_EMPTY.value
            )
        return self
    
class ResetHuggingFaceAIModelContextRequest(BaseModel):
    agent_id : str = Field(default=None,description = AgentRequestFieldDescription.AI_AGENT_ID.value)
    @model_validator(mode="after")
    def validate_fields(self):
        if not self.agent_id:
            error_logger.error(f"HuggingFacePromptRequest.validate_fields | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
            )
        return self
    
class SetAgentToolToAnAgentRequest(BaseModel):
    agent_id : str = Field(default=None, description = AgentRequestFieldDescription.AI_AGENT_ID.value)
    agent_tool_name : str = Field(default=None,description = SetAgentToolToAnAgentRequestFieldDescription.AI_AGENT_TOOL_NAME.value)
    @model_validator(mode="after")
    def validate_fields(self):
        if not self.agent_id:
            error_logger.error(f"SetAgentToolToAnAgentRequest.validate_fields | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
            )
        return self