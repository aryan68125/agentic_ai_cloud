# import fast api related libraries and packages
from fastapi import APIRouter, Depends, BackgroundTasks, Request

# import request response model
from app.models.api_request_response_model.request_models import AgentRequest
from app.models.api_request_response_model.response_models import (APIResponse,APIResponseMultipleData)

# import controllers
from app.controllers.agent_controllers import AgentController

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages, AgentApiUrls

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

# get db operation type
from app.utils.db_operation_type import DbRecordLevelOperationType

router = APIRouter(tags=["Agent_processing_apis"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

def get_agent_controller():
    return AgentController()

"""
CRUD Apis for Agent that is unique and is tied to the user STARTS
"""
@router.post("/agent/create", response_model=APIResponse)
def create_agent(
    request: AgentRequest,
    http_request: Request,
    controller: AgentController = Depends(get_agent_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"create_agent | url = {BASE_URL_FAST_API_SERVER}{AgentApiUrls.CREATE_AGENT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_agent(request=request, operation_type=DbRecordLevelOperationType.INSERT.value)

@router.put("/agent/update", response_model=APIResponse)
def update_agent(
    request: AgentRequest,
    http_request: Request,
    controller: AgentController = Depends(get_agent_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"update_agent | url = {BASE_URL_FAST_API_SERVER}{AgentApiUrls.UPDATE_AGENT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_agent(request=request, operation_type=DbRecordLevelOperationType.UPDATE.value)

@router.delete("/agent/delete", response_model=APIResponse)
def delete_agent(
    request: AgentRequest,
    http_request: Request,
    controller: AgentController = Depends(get_agent_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"delete_agent | url = {BASE_URL_FAST_API_SERVER}{AgentApiUrls.DELETE_AGENT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.process_agent(request=request, operation_type=DbRecordLevelOperationType.DELETE.value)

@router.post("/agent/get", response_model=APIResponseMultipleData)
def get_agent(
    request: AgentRequest,
    http_request: Request,
    controller: AgentController = Depends(get_agent_controller)
):  
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"create_agent | url = {BASE_URL_FAST_API_SERVER}{AgentApiUrls.GET_AGENT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    if not request.agent_id and not request.agent_name:
        return controller.process_agent(request=request, operation_type=DbRecordLevelOperationType.GET_ALL.value)
    if request.agent_id and not request.agent_name:
        return controller.process_agent(request=request,operation_type=DbRecordLevelOperationType.GET_ONE.value)
    if not request.agent_id and request.agent_name:
        return controller.process_agent(request=request,operation_type=DbRecordLevelOperationType.GET_ONE.value)
"""
CRUD Apis for Agent that is unique and is tied to the user ENDS
"""