# import fast api related libraries and packages
from fastapi import APIRouter, Depends, BackgroundTasks, Request, Body

# import controller dependencies 
from app.dependencies.controller_dependencies import get_ai_agent_tool_controller

# import request model
from app.models.api_request_response_model.request_models import (SetAgentToolToAnAgentRequest, DetachAgentToolFromAgentRequest)

# import controller
from app.controllers.ai_agent_tools_controller import AIAgentToolController

# import api urls
from app.utils.logger_info_messages import AiAgentToolUrls

# import success messages 
from app.utils.success_messages import AIAgentToolApiSuccessMessage

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

# import logging utility
from app.utils.logger import LoggerFactory

router = APIRouter(tags=["ai_agent_tools"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

@router.get("/agent_tools/get")
def get_list_of_agent_tools(
    http_request : Request,
    controller : AIAgentToolController = Depends(get_ai_agent_tool_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"get_list_of_agent_tools | url = {BASE_URL_FAST_API_SERVER}{AiAgentToolUrls.GET_ALL_AI_AGENT_TOOLS.value} | {AIAgentToolApiSuccessMessage.AI_AGENT_TOOL_LIST_FETCHED.value}")
    return controller.get_agent_tools_list()

@router.post("/set_agent_tool")
def set_agent_tool_to_an_agent(
    request : SetAgentToolToAnAgentRequest,
    http_request: Request,
    controller: AIAgentToolController = Depends(get_ai_agent_tool_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"get_list_of_agent_tools | url = {BASE_URL_FAST_API_SERVER}{AiAgentToolUrls.SET__TOOL_TO_AN_AGENT.value} | {AIAgentToolApiSuccessMessage.SET_AGENT_TOOL_SUCCESS.value}")
    return controller.set_tool_to_an_ai_agent(request=request)

@router.post("/detach_agent_tool")
def detach_one_tool_from_agent(
    request : DetachAgentToolFromAgentRequest,
    http_request: Request,
    controller: AIAgentToolController = Depends(get_ai_agent_tool_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"detach_one_tool_from_agent | url = {BASE_URL_FAST_API_SERVER}{AiAgentToolUrls.DETACH_AGENT_TOOL.value} | {AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value}")
    return controller.remove_tool_from_agent(request=request, MULTI_TOOL = False)

@router.delete("/reset_agent_tools")
def detach_all_tools_from_agent(
    request : DetachAgentToolFromAgentRequest,
    http_request: Request,
    controller: AIAgentToolController = Depends(get_ai_agent_tool_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"detach_all_tools_from_agent | url = {BASE_URL_FAST_API_SERVER}{AiAgentToolUrls.DETACH_ALL_AGENT_TOOLs.value} | {AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value}")
    return controller.remove_tool_from_agent(request=request, MULTI_TOOL = True)