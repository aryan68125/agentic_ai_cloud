from fastapi import HTTPException, status, BackgroundTasks
import uuid

from app.models.prompt_api_models.response_models import PromptResponse
from app.utils.error_messages import PromptApiErrorMessages
from app.services.json_reader import JsonIngestionService
from app.services.excel_reader import ExcelIngestionService

# import logging utility
from app.utils.logger import LoggerFactory

# import info logger messages
from app.utils.logger_info_messages import LoggerInfoMessages

# import utility to generate ingestion id
from app.utils.generate_ingestion_id import GenerateFileAndIngestionID
import time

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptController:
    def __init__(self):
        pass

    def process_prompt(self, request) -> PromptResponse:
        try:
            prompt_message = request.prompt_message
            return PromptResponse(
                status = status.HTTP_200_OK,
                message = "Prompt processed successfully!"
            )
        except Exception as e:
            error_logger.error(f"PromptController.process_prompt | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
