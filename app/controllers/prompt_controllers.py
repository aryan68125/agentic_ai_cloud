from fastapi import HTTPException, status, BackgroundTasks
import uuid

from app.models.api_request_response_model.response_models import (APIResponse, APIResponseMultipleData)

# import common success and error messages
from app.utils.error_messages import (PromptApiErrorMessages,AgentApiErrorMessages)
from app.utils.success_messages import PromptApiSuccessMessages

# load project configurations
from app.configs.config import ProjectConfigurations

# import logging utility
from app.utils.logger import LoggerFactory

# import services
from app.services.process_prompt import ProcessPromptService

# import database operation types
from app.utils.db_operation_type import DbRecordLevelOperationType

# import database connection manager
from app.utils.db_conn_manager import PostgresConnectionManager

# import repositories
from app.repositories.system_prompt_repository import SystemPromptRepository

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PromptController:
    def __init__(self):
        self.process_prompt_service_obj = ProcessPromptService(hugging_face_auth_token=ProjectConfigurations.HUGGING_FACE_AUTH_TOKEN.value,HF_API_URL = ProjectConfigurations.HF_API_URL.value)
        db_pool = PostgresConnectionManager.get_pool()
        self.system_prompt_repo = SystemPromptRepository(pool=db_pool)

    async def process_user_prompt(self, request) -> APIResponse:
        try:
            info_logger.info(f"PromptController.process_user_prompt | Started to process user prompt | user_prompt = {request.user_prompt}")
            result = await self.process_prompt_service_obj.process_user_prompt_llm(request=request) 
            if not result.status:
                return APIResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=result.message
                )
            return APIResponse(
                status = status.HTTP_200_OK,
                message = result.message,
                data=result.data

            )
        except Exception as e:
            error_logger.error(f"PromptController.process_user_prompt | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    
    def process_system_prompt(self, request, operation_type : str) -> APIResponseMultipleData:
        try:
            info_logger.info(f"PromptController.process_system_prompt | Started to process system prompt | operation_type = {operation_type} | agent_id = {request.agent_id} , system_prompt = {request.system_prompt}")
            
            if operation_type == DbRecordLevelOperationType.INSERT.value:
                info_logger.info(f"PromptController.process_system_prompt | insert agent name in the database")
                result = self.system_prompt_repo.insert(agent_id = request.agent_id, system_prompt = request.system_prompt)
                if not result.status:
                    error_logger.error(f"PromptController.process_system_prompt | error = {result.message}")
                debug_logger.debug(f"PromptController.process_system_prompt | result = {result}")

            elif operation_type == DbRecordLevelOperationType.UPDATE.value:
                info_logger.info(f"PromptController.process_system_prompt | update agent name in the database")
                if not request.agent_id:
                    error_logger.error(f"PromptController.process_system_prompt | operation_type = {operation_type} | error = {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                    )
                result = self.system_prompt_repo.update(
                    agent_id=request.agent_id, 
                    system_prompt=request.system_prompt
                )
                if not result.status:
                    error_logger.error(f"PromptController.process_system_prompt | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=result.status_code, 
                        detail=result.message
                    )
                debug_logger.debug(f"PromptController.process_system_prompt | result = {result}")

            elif operation_type == DbRecordLevelOperationType.DELETE.value:
                info_logger.info(f"PromptController.process_system_prompt | delete agent name in the database")
                result = self.system_prompt_repo.delete(request.agent_id)
                if not result.status:
                    error_logger.error(f"PromptController.process_system_prompt | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=result.status_code, 
                        detail=result.message)
                debug_logger.debug(f"PromptController.process_system_prompt | result = {result}")

            return APIResponseMultipleData(
                status = result.status_code,
                message = result.message,
                data=result.data
            )
        except Exception as e:
            error_logger.error(f"PromptController.process_system_prompt | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

