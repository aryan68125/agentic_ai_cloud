# import fast api related libraries and packages
from fastapi import APIRouter, Depends, BackgroundTasks, Request, Body

# import request response model
from app.models.api_request_response_model.request_models import (HuggingFacePromptRequest, ResetHuggingFaceAIModelContextRequest)
from app.models.api_request_response_model.response_models import APIResponse

# import controllers
from app.controllers.hugging_face_ai_model_controllers import HuggingFaceAIModelController

# import controller dependencies 
from app.dependencies.controller_dependencies import get_hugging_face_ai_model_controller

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages, HuggingFaceAPIUrls

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

router = APIRouter(tags=["hugging_face_model_apis"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

@router.get("/hugging_face/get_models", response_model=APIResponse)
def get_ai_models(
    http_request: Request,
    controller: HuggingFaceAIModelController = Depends(get_hugging_face_ai_model_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"get_ai_models | url = {BASE_URL_FAST_API_SERVER}{HuggingFaceAPIUrls.HUGGING_FACE_GET_AI_MODELS.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.get_models()

@router.post("/hugging_face/user_prompt", response_model=APIResponse)
async def process_user_prompt_hugging_face(
    request: HuggingFacePromptRequest,
    http_request: Request,
    controller: HuggingFaceAIModelController = Depends(get_hugging_face_ai_model_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"process_user_prompt_api | url = {BASE_URL_FAST_API_SERVER}{HuggingFaceAPIUrls.HUGGING_FACE_PROCESS_PROMPT.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return await controller.process_hugging_face_prompt_request(request)

@router.delete("/hugging_face/reset_ai_agent_context", response_model=APIResponse)
def reset_ai_agent_context(
    request: ResetHuggingFaceAIModelContextRequest,
    http_request: Request,
    controller: HuggingFaceAIModelController = Depends(get_hugging_face_ai_model_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"process_user_prompt_hugging_face | url = {BASE_URL_FAST_API_SERVER}{HuggingFaceAPIUrls.HUGGINGFACE_AI_MODEL_RESET_CONTEXT.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.reset_huggingface_model_context(request)

from app.tools.research_tool.services.process_qwen_llm import ProcessPerplexityAIPromptService
from app.configs.config import ProjectConfigurations
from pydantic import BaseModel
class ResearchToolTestRequest(BaseModel):
    main_llm_request_query: str

@router.post("/hugging_face/research_tool_llm_test_api")
async def test_perplexity_research_tool_llm(payload: ResearchToolTestRequest):
    if not payload.main_llm_request_query.strip():
        return {
            "status": 400,
            "error": "query cannot be empty"
        }

    service = ProcessPerplexityAIPromptService(
        hugging_face_auth_token=ProjectConfigurations.HUGGING_FACE_AUTH_TOKEN.value,
        HF_API_URL=ProjectConfigurations.HF_API_URL.value
    )

    result = await service.process_main_LLM_research_query(
        request=payload
    )

    return result