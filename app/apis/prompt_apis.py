# import fast api related libraries and packages
from fastapi import APIRouter, Depends, BackgroundTasks

# import request response model
from app.models.prompt_api_models.request_models import PromptRequest
from app.models.prompt_api_models.response_models import PromptResponse

# import controllers
from app.controllers.prompt_controllers import PromptController

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages

router = APIRouter(tags=["Ingestion"])

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

def get_prompt_controller():
    return PromptController()

@router.post("/prompt_api", response_model=PromptResponse)
def prompt_page(
    request: PromptRequest,
    controller: PromptController = Depends(get_prompt_controller)
):
    info_logger.info(f"api_hit : /api/prompt_api : {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return controller.ingest(request)