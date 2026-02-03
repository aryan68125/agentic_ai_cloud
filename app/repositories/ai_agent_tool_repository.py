# import status codes from fast-api
from fastapi import status

# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func)

# import tables
from app.models.db_table_models.attached_ai_tools_table import AttachedAIToolsTable
from app.models.db_table_models.ai_agent_table import AIAgentName

# import agent tool names
from app.utils.ai_tools_enum import AiAgentToolsList

# import error messages
from app.utils.error_messages import (AgentApiErrorMessages, AIAgentToolApiErrorMessage, AgentApiErrorMessages)

# import success_messages
from app.utils.success_messages import (AIAgentToolApiSuccessMessage,AiAgentApiSuccessMessage)

# import class response model
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class AIAgentToolsRepository:
    def __init__(self, db : Session):
        self.db = db
        debug_logger.debug(f"AIAgentToolsRepository.__init__ | AIAgentToolsRepository initialized | db = {self.db}")

    def check_if_agent_id_exists(self,agent_id : str) -> RepositoryClassResponse:
        try:
            stmt = select(AIAgentName).where(
                AIAgentName.ai_agent_id == agent_id
            )
            existing = self.db.execute(stmt).scalar_one_or_none()
            if existing:
                return RepositoryClassResponse(
                    status=True,
                    status_code=status.HTTP_200_OK,
                    message=AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value
                )
            else:
                return RepositoryClassResponse(
                    status=True,
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
        except Exception as e:
            error_logger.error(f"AIAgentToolsRepository.check_if_agent_id_exists | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

    def upsert(self,agent_id : str , agent_tool_name : str) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"AIAgentToolsRepository.upsert | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            if not agent_tool_name or agent_tool_name is None or agent_tool_name == "":
                error_logger.error(f"AIAgentToolsRepository.upsert | {AIAgentToolApiErrorMessage.AGENT_TOOL_NAME_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AIAgentToolApiErrorMessage.AGENT_TOOL_NAME_EMPTY.value
                )
            
            check_if_agent_id_exists_result = self.check_if_agent_id_exists(agent_id=agent_id)
            if check_if_agent_id_exists_result.status and (check_if_agent_id_exists_result.status_code == status.HTTP_404_NOT_FOUND):
                error_logger.error(f"AIAgentToolsRepository.upsert | {check_if_agent_id_exists_result.message}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = check_if_agent_id_exists_result.status_code,
                    message=check_if_agent_id_exists_result.message
                )
            
            if agent_tool_name not in {tool.value for tool in AiAgentToolsList}:
                error_logger.error(f"AIAgentToolsRepository.upsert | {AIAgentToolApiErrorMessage.AGENT_TOOL_NAME_INVALID.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AIAgentToolApiErrorMessage.AGENT_TOOL_NAME_INVALID.value
                )
            
            # check if the record exists 
            obj = select(AttachedAIToolsTable).where(
                AttachedAIToolsTable.ai_agent_id == agent_id,
                AttachedAIToolsTable.agent_tool_name == agent_tool_name
            )
            existing = self.db.execute(obj).scalar_one_or_none()
            debug_logger.debug(f"AIAgentToolsRepository.upsert | existing = {existing}")
            if existing:
                # touch the row (updated_at will auto-update)
                self.db.flush()
                self.db.refresh(existing)
                row = existing.to_dict()
                debug_logger.debug(f"AIAgentToolsRepository.upsert | UPDATE EXISTING RECORD | row = {row}")

                return RepositoryClassResponse(
                    status=True,
                    status_code=status.HTTP_200_OK,
                    message=AIAgentToolApiSuccessMessage.TOOL_ALREADY_ATTACHED.value,
                    data=row
                )

            # insert new
            obj = AttachedAIToolsTable(
                ai_agent_id=agent_id,
                agent_tool_name=agent_tool_name
            )
            self.db.add(obj)
            self.db.flush()
            self.db.refresh(obj)
            row = obj.to_dict()
            debug_logger.debug(f"AIAgentToolsRepository.upsert | INSERT NEW RECORD | row = {row}")
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_201_CREATED,
                message=AIAgentToolApiSuccessMessage.TOOL_ATTACHED.value,
                data=row
            )

        except Exception as e:
            error_logger.error(f"AIAgentToolsRepository.upsert | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )
        
    def delete_one_tool(self, agent_tool_attachment_id : int = None) -> RepositoryClassResponse:
        try:
            if not agent_tool_attachment_id:
                error_logger.error(f"AIAgentToolsRepository.delete_one_tool | {AIAgentToolApiErrorMessage.AGENT_TOOL_ATTACHMENT_ID.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=AIAgentToolApiErrorMessage.AGENT_TOOL_ATTACHMENT_ID.value,
                ) 
            obj = delete(AttachedAIToolsTable).where(AttachedAIToolsTable.id == agent_tool_attachment_id)
            result = self.db.execute(obj)
            self.db.flush()

            debug_logger.debug(f"AIAgentToolsRepository.delete_one_tool | delete the tool attached to the agent | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"AIAgentToolsRepository.delete_one_tool | {AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"AIAgentToolsRepository.delete_one_tool | {AIAgentToolApiErrorMessage.AGENT_TOOL_IS_NOT_ATTACHED_ERR.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AIAgentToolApiErrorMessage.AGENT_TOOL_IS_NOT_ATTACHED_ERR.value
                ) 
        except Exception as e:
            error_logger.error(f"AIAgentToolsRepository.delete_one_tool | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            ) 
        
    def delete_multi_tool(self, agent_id : str = None) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"AIAgentToolsRepository.delete_multi_tool | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            
            obj = delete(AttachedAIToolsTable).where(AttachedAIToolsTable.ai_agent_id == agent_id)
            result = self.db.execute(obj)
            self.db.flush()

            debug_logger.debug(f"AIAgentToolsRepository.delete_multi_tool | delete all tools attached to the agent | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"AIAgentToolsRepository.delete_multi_tool | {AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = AIAgentToolApiSuccessMessage.TOOL_DETACHED_FROM_THE_AGENT_SUCCESS.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"AIAgentToolsRepository.delete_multi_tool | {AIAgentToolApiErrorMessage.AGENT_TOOL_IS_NOT_ATTACHED_ERR.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AIAgentToolApiErrorMessage.AGENT_TOOL_IS_NOT_ATTACHED_ERR.value
                ) 
        except Exception as e:
            error_logger.error(f"AIAgentToolsRepository.delete_multi_tool | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )