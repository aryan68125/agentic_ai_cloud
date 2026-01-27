# import fast api related libraries and packages
from fastapi import (APIRouter, Depends, BackgroundTasks, Request, Query)

# import request response model
from app.models.api_request_response_model.request_models import (SystemPromptQueryParams, SystemPromptRequest,  UserPromptQueryParams, UserPromptRequest)
from app.models.api_request_response_model.response_models import APIResponseMultipleData

# import controllers
from app.controllers.prompt_controllers import PromptController

# controller dependecies 
from app.dependencies.controller_dependencies import get_prompt_controller

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import (LoggerInfoMessages, PromptApiUrls, SystemPromptApiUrls, UserPromptApiUrls)

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

# get db operation type
from app.utils.db_operation_type import DbRecordLevelOperationType

router = APIRouter(tags=["Prompt_processing_apis"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()



"""
Remove this from here 
"""
# @router.post("/user_prompt", response_model=APIResponse)
# async def process_user_prompt_api(
#     request: PromptRequest,
#     http_request: Request,
#     controller: PromptController = Depends(get_prompt_controller)
# ):
#     BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
#     info_logger.info(f"process_user_prompt_api | url = {BASE_URL_FAST_API_SERVER}{PromptApiUrls.PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
#     return await controller.process_user_prompt(request)

"""
CRUD Apis for user_prompt that is tied to the system_prompt , agent and model name STARTS
These apis is used to store user_prompts in the database
Things that will be saved in the database
ai_model : The model name that must be used on the hugging face side to process the user_prompt
ai_agent_id
system_prompt
user_prompt
"""
@router.post("/user_prompt/create", response_model=APIResponseMultipleData)
def create_user_prompt(
    request: UserPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"create_user_prompt | url = {BASE_URL_FAST_API_SERVER}{UserPromptApiUrls.CREATE_USER_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_user_prompt(request=request, operation_type=DbRecordLevelOperationType.INSERT.value)

@router.put("/user_prompt/update", response_model=APIResponseMultipleData)
def update_user_prompt(
    request: UserPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"update_user_prompt | url = {BASE_URL_FAST_API_SERVER}{UserPromptApiUrls.UPDATE_USER_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_user_prompt(request=request, operation_type=DbRecordLevelOperationType.UPDATE.value)

@router.delete("/user_prompt/delete", response_model=APIResponseMultipleData)
def delete_user_prompt(
    request: UserPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"delete_system_prompt | url = {BASE_URL_FAST_API_SERVER}{UserPromptApiUrls.DELETE_USER_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_user_prompt(request=request, operation_type=DbRecordLevelOperationType.DELETE.value)

@router.get("/user_prompt/get", response_model=APIResponseMultipleData)
def get_user_prompt(
    agent_id: str = Query(default=None, description="AI Agent ID"),
    limit: int = Query(default=10, ge=1, le=50),
    before_id: int | None = Query(None),
    http_request: Request = None,
    controller: PromptController = Depends(get_prompt_controller)
):  
    full_url = str(http_request.url)
    info_logger.info(
        f"get_user_prompt | url = {full_url} | {LoggerInfoMessages.API_HIT_SUCCESS.value}"
    )
    request = UserPromptQueryParams(agent_id=agent_id,limit=limit, before_id=before_id)
    return controller.process_user_prompt(request=request,operation_type=DbRecordLevelOperationType.GET_ALL.value)

"""
CRUD Apis for user_prompt that is tied to the system_prompt , agent and model name ENDS
"""

"""
CRUD Apis for system_prompt that is tied to a unique agent STARTS
"""
@router.post("/system_prompt/create", response_model=APIResponseMultipleData)
def create_system_prompt(
    request: SystemPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"create_system_prompt | url = {BASE_URL_FAST_API_SERVER}{SystemPromptApiUrls.CREATE_SYSTEM_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_system_prompt(request=request, operation_type=DbRecordLevelOperationType.INSERT.value)

@router.put("/system_prompt/update", response_model=APIResponseMultipleData)
def update_system_prompt(
    request: SystemPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"update_system_prompt | url = {BASE_URL_FAST_API_SERVER}{SystemPromptApiUrls.UPDATE_SYSTEM_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_system_prompt(request=request, operation_type=DbRecordLevelOperationType.UPDATE.value)

@router.delete("/system_prompt/delete", response_model=APIResponseMultipleData)
def delete_system_prompt(
    request: SystemPromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"delete_system_prompt | url = {BASE_URL_FAST_API_SERVER}{SystemPromptApiUrls.DELETE_SYSTEM_PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_system_prompt(request=request, operation_type=DbRecordLevelOperationType.DELETE.value)

@router.get("/system_prompt/get", response_model=APIResponseMultipleData)
def get_system_prompt(
    agent_id: str = Query(default=None, description="AI Agent ID"),
    limit: int = Query(default=10, ge=1, le=50),
    before_id: int | None = Query(None),
    http_request: Request = None,
    controller: PromptController = Depends(get_prompt_controller)
):  
    full_url = str(http_request.url)
    info_logger.info(
        f"get_system_prompt | url = {full_url} | {LoggerInfoMessages.API_HIT_SUCCESS.value}"
    )
    if agent_id and not(limit and before_id):
        # get one record 
        request = SystemPromptQueryParams(agent_id=agent_id)
        return controller.process_system_prompt(request=request,operation_type=DbRecordLevelOperationType.GET_ONE.value)
    elif not agent_id and (limit or before_id):
        request = SystemPromptQueryParams(limit=limit, before_id=before_id)
        return controller.process_system_prompt(request=request,operation_type=DbRecordLevelOperationType.GET_ALL.value)
"""
CRUD Apis for system_prompt that is tied to a unique agent ENDS
"""