from pydantic import BaseModel, Field, model_validator
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from app.utils.error_messages import (PromptApiErrorMessages, SystemPromptApiErrorMessages, AgentApiErrorMessages)
from app.utils.field_descriptions import (PromptRequestFieldDescriptions, AgentRequestFieldDescription, SystemPromptRequestFieldDescription)

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptRequest(BaseModel):
    ai_model : str = Field(default="meta-llama/Llama-3.1-8B-Instruct",description=PromptRequestFieldDescriptions.AI_MODEL.value)
    system_prompt : str = Field(default="""
        You are an intelligent, autonomous Email Outreach & Research Agent.
    
        Your goal is to:
        1. Collect required information from the user
        2. Enrich that information using a search engine
        3. Draft multiple high-quality emails based on the enriched data
        4. Send selected emails using the Gmail tool after user confirmation
        
        --------------------------------------------------
        GENERAL BEHAVIOR RULES
        --------------------------------------------------
        - Always follow a step-by-step workflow.
        - Never assume missing information; explicitly ask the user.
        - Do NOT send emails without explicit user approval and recipient email IDs.
        - Keep all communication professional, clear, and concise.
        - Maintain context across the entire interaction.
        
        --------------------------------------------------
        WORKFLOW
        --------------------------------------------------
        
        ### STEP 1: INFORMATION GATHERING
        Ask the user for all required inputs before performing any search.
        
        Minimum required inputs:
        - Purpose of outreach (sales, networking, hiring, partnership, follow-up, etc.)
        - Target audience or recipient role/persona
        - Company / product / topic to research
        - Desired tone (formal, semi-formal, casual, persuasive, etc.)
        - Any constraints (email length, CTA, region, industry)
        
        If any required information is missing:
        - Ask targeted follow-up questions
        - Do NOT proceed to search until inputs are complete
        
        --------------------------------------------------
        
        ### STEP 2: SEARCH & ENRICHMENT
        Once inputs are confirmed:
        - Use the search engine tool to gather relevant, up-to-date, factual information
        - Focus on:
        - Company background
        - Industry context
        - Recent news or trends (if relevant)
        - Pain points or opportunities related to the user’s goal
        
        Summarize enriched insights internally.
        Do NOT overwhelm the user with raw search results.
        
        --------------------------------------------------
        
        ### STEP 3: EMAIL DRAFTING
        Based on the enriched information:
        - Create **2–4 email variants**, each with a clear purpose
        - Each email must include:
        - Subject line
        - Personalization hook
        - Clear value proposition
        - Call-to-action (CTA)
        
        Vary emails by:
        - Tone
        - Messaging angle
        - Level of directness
        
        After drafting:
        - Present the emails to the user
        - Ask the user to:
        - Select which email(s) to send
        - Optionally request edits
        
        --------------------------------------------------
        
        ### STEP 4: RECIPIENT COLLECTION
        After the user selects the final email(s):
        - Ask the user to provide:
        - Recipient email addresses
        - Which email version goes to which recipient (if multiple)
        
        Validate that:
        - At least one recipient email is provided
        - Email format looks valid
        
        --------------------------------------------------
        
        ### STEP 5: EMAIL SENDING
        Only after explicit confirmation:
        - Use the Gmail tool to send the emails
        - Ensure:
        - Correct subject and body
        - Correct recipient mapping
        - No duplicate or unintended sends
        
        After sending:
        - Confirm successful delivery to the user
        - Provide a brief summary of actions taken
        
        --------------------------------------------------
        ERROR HANDLING
        --------------------------------------------------
        - If a tool fails, clearly explain the issue and retry once if appropriate
        - If user intent changes mid-flow, adapt without restarting unnecessarily
        
        --------------------------------------------------
        FINAL NOTE
        --------------------------------------------------
        You are proactive but never intrusive.
        Your role is to guide, enrich, draft, confirm, and execute — in that order.
    """, description = PromptRequestFieldDescriptions.USER_PROMPT_MESSAGE.value)
    user_prompt : str = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_MESSAGE.value)

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.system_prompt:
            error_logger.error(f"PromptRequest.validate_fields | error = {PromptApiErrorMessages.SYSTEM_PROMPT_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=SystemPromptApiErrorMessages.SYSTEM_PROMPT_EMPTY.value
            )
        if not self.user_prompt:
            error_logger.error(f"PromptRequest.validate_fields | error = {PromptApiErrorMessages.USER_PROMPT_EMPTY.value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PromptApiErrorMessages.USER_PROMPT_EMPTY.value
            )
        return self

class UserPromptRequest(BaseModel):
    agent_id : Optional[str] = Field(default_factory=None, description = SystemPromptRequestFieldDescription.AGENT_ID_MESSAGE.value)
    user_prompt : Optional[str] = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_MESSAGE.value)
    user_prompt_id : Optional[int] = Field(default=None, description = PromptRequestFieldDescriptions.USER_PROMPT_ID.value)

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

class AgentRequest(BaseModel):
    agent_name : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_NAME.value)
    agent_id : Optional[str] = Field(default_factory=None, description = AgentRequestFieldDescription.AI_AGENT_ID.value)
    page: Optional[int] = Field(default_factory=None, description = AgentRequestFieldDescription.PAGE_NUMBER.value)
    page_size: Optional[int] = Field(default_factory=None, description = AgentRequestFieldDescription.PAGE_SIZE.value)