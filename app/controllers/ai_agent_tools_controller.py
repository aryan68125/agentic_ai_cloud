# import fast api framework packages
from fastapi import HTTPException, status, BackgroundTasks

# db orm related imports
from sqlalchemy.orm import Session

# import data repositories
from app.repositories.ai_agent_tool_repository import AIAgentToolsRepository

# import transaction exception handler
from app.database.db_transaction_exception_handler import TransactionAbort

# import response model
from app.models.api_request_response_model.response_models import (APIResponse, APIResponseMultipleData)

# import the enum that contains all the ai agent tools name
from app.utils.ai_tools_enum import AiAgentToolsList
from app.utils.success_messages import AIAgentToolApiSuccessMessage

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class AIAgentToolController:
    def __init__(self,db : Session):
        self.db = db
        self.agent_tool_repository = AIAgentToolsRepository(db=db)

    def get_agent_tools_list(self) -> APIResponse:
        try:
            info_logger.info(f"AIAgentToolController.get_agent_tools_list | {AIAgentToolApiSuccessMessage.AI_AGENT_TOOL_LIST_FETCHED.value}")
            agent_tools_list = [AiAgentToolsList.RESEARCH_TOOL.value]
            data = {
                "agent_tools_list":agent_tools_list
            }
            debug_logger.debug(f"AIAgentToolController.get_agent_tools_list | data = {data}")
            return APIResponse(
                status = status.HTTP_200_OK,
                message = AIAgentToolApiSuccessMessage.AI_AGENT_TOOL_LIST_FETCHED.value,
                data=data
            )
        except Exception as e:
            error_logger.error(f"AIAgentToolController.get_agent_tools_list | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    def set_tool_to_an_ai_agent(self,request) -> APIResponse:
        try:
            info_logger.info(f"AIAgentToolController.get_agent_tools_list | Attach the tool with the ai agent | agent_id = {request.agent_id}, tool_name = {request.agent_tool_name}")
            print(f"request : {request} | agent_id = {request.agent_id}, tool_name = {request.agent_tool_name}")
            with self.db.begin():
                usert_result = self.agent_tool_repository.upsert(agent_id = request.agent_id, agent_tool_name = request.agent_tool_name)
                if not usert_result.status:
                    raise TransactionAbort(usert_result)
            return APIResponse(
                status = usert_result.status_code,
                message = usert_result.message,
                data = usert_result.data
            )
        except TransactionAbort as e:
            error_logger.error(f"AIAgentToolController.set_tool_to_an_ai_agent | {str(e)}")
            return APIResponse(
                status = usert_result.status_code,
                message = usert_result.message,
                data = usert_result.data
            ) 
        except Exception as e:
            error_logger.error(f"AIAgentToolController.set_tool_to_an_ai_agent | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def remove_tool_from_agent(self,request,MULTI_TOOL : bool = False):
        try:
            info_logger.info(f"AIAgentToolController.remove_tool_from_agent | Detach 1 tool from the ai agent | request = {request}, MULTI_TOOL = {MULTI_TOOL}")
            if not MULTI_TOOL:
                with self.db.begin():
                    detach_tool_result = self.agent_tool_repository.delete_one_tool(agent_tool_attachment_id = request.agent_tool_attachment_id)
                    if not detach_tool_result.status:
                        raise TransactionAbort(detach_tool_result)
            if MULTI_TOOL:
                with self.db.begin():
                    detach_tool_result = self.agent_tool_repository.delete_multi_tool(agent_id = request.agent_id)
                    if not detach_tool_result.status:
                        raise TransactionAbort(detach_tool_result)

            return APIResponse(
                status = detach_tool_result.status_code,
                message = detach_tool_result.message,
                data = detach_tool_result.data
            )
        except TransactionAbort as e:
            error_logger.error(f"AIAgentToolController.remove_tool_from_agent | {str(e)}")
            return APIResponse(
                status = detach_tool_result.status_code,
                message = detach_tool_result.message,
                data = detach_tool_result.data
            ) 
        except Exception as e:
            error_logger.error(f"AIAgentToolController.remove_tool_from_agent | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
