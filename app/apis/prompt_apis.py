# import fast api related libraries and packages
from fastapi import APIRouter, Depends, BackgroundTasks, Request

# import request response model
from app.models.prompt_api_models.request_models import PromptRequest
from app.models.prompt_api_models.response_models import PromptResponse

# import controllers
from app.controllers.prompt_controllers import PromptController

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages, PromptApiUrls

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

router = APIRouter(tags=["Ingestion"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

def get_prompt_controller():
    return PromptController()

@router.post("/prompt_api", response_model=PromptResponse)
async def prompt_page(
    request: PromptRequest,
    http_request: Request,
    controller: PromptController = Depends(get_prompt_controller)
):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request=http_request)
    info_logger.info(f"prompt_page | url = {BASE_URL_FAST_API_SERVER}{PromptApiUrls.PROMPT_API_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return await controller.process_prompt(request)