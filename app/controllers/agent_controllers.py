from fastapi import HTTPException, status, BackgroundTasks, Depends

from app.models.api_request_response_model.response_models import APIResponseMultipleData

# import logging utility
from app.utils.logger import LoggerFactory

# import repositories
from app.repositories.ai_agent_repository import AIAgentRepository

# import db operation type
from app.utils.db_operation_type import DbRecordLevelOperationType

# import error messages
from app.utils.error_messages import AgentApiErrorMessages

# db orm related imports
from sqlalchemy.orm import Session

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class AgentController:
    def __init__(self,db: Session):
        self.ai_agent_repo = AIAgentRepository(db=db)

    def process_agent(self, request, operation_type : str) -> APIResponseMultipleData:
        try:
            info_logger.info(f"AgentController.process_agent | Started to process agent | operation_type = {operation_type} | agent_name = {request.agent_name}")
            # Here the logic to save the ai agent name in the database will come
            if operation_type == DbRecordLevelOperationType.INSERT.value:
                info_logger.info(f"AgentController.process_agent | insert agent name in the database")
                result = self.ai_agent_repo.insert(request.agent_name)
                if not result.status:
                    error_logger.error(f"AgentController.process_agent | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=result.message
                    )
                debug_logger.debug(f"AgentController.process_agent | result = {result}")

            elif operation_type == DbRecordLevelOperationType.UPDATE.value:
                info_logger.info(f"AgentController.process_agent | update agent name in the database")
                result = self.ai_agent_repo.update(
                    agent_id=request.agent_id,
                    new_name=request.agent_name
                )
                if not result.status:
                    error_logger.error(f"AgentController.process_agent | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=result.status_code, 
                        detail=result.message
                    )
                debug_logger.debug(f"AgentController.process_agent | result = {result}")
                
            elif operation_type == DbRecordLevelOperationType.DELETE.value:
                info_logger.info(f"AgentController.process_agent | delete agent name in the database")
                result = self.ai_agent_repo.delete(request.agent_id)
                if not result.status:
                    error_logger.error(f"AgentController.process_agent | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=result.status_code, 
                        detail=result.message)
                debug_logger.debug(f"AgentController.process_agent | result = {result}")
           
            elif operation_type == DbRecordLevelOperationType.GET_ALL.value:
                info_logger.info(f"AgentController.process_agent | get all agent's name from the database")
                result = self.ai_agent_repo.get_all(page = request.page,page_size = request.page_size)
                if not result.status:
                    error_logger.error(f"AgentController.process_agent | {result.message}")
                    raise HTTPException(
                        status_code=result.status_code,
                        detail=result.message
                    )
                debug_logger.debug(f"AgentController.process_agent | result = {result}")

            elif operation_type == DbRecordLevelOperationType.GET_ONE.value:
                info_logger.info(f"AgentController.process_agent | get one agent name from the database")
                if not request.agent_id and request.agent_name:
                    error_logger.error(f"AgentController.process_agent | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                    )
                result = self.ai_agent_repo.get_one(
                    agent_id=request.agent_id,
                    agent_name=request.agent_name
                )
                if not result.status:
                    error_logger.error(f"AgentController.process_agent | operation_type = {operation_type} | error = {result.message}")
                    raise HTTPException(
                        status_code=result.status_code, 
                        detail=result.message)
                debug_logger.debug(f"AgentController.process_agent | result = {result}")
            else:
                error_logger.error(f"AgentController.process_agent | {AgentApiErrorMessages.UNDEFINED_DB_OPERATION_TYPE.value}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=AgentApiErrorMessages.UNDEFINED_DB_OPERATION_TYPE.value
                )
            return APIResponseMultipleData(
                status = result.status_code,
                message = result.message,
                data=result.data
            )
        except HTTPException:
            raise
        except Exception as e:
            error_logger.error(f"AgentController.process_agent | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
