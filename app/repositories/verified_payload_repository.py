# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func)

# imports related to database table models
from app.models.db_table_models.llm_prompt_response_table import LLMPromptResponseTable
from app.models.db_table_models.verified_payload_table import VerifiedPayload

# import repositories
from app.repositories.user_prompt_repository import UserPromptRepository

# import messages
from app.utils.success_messages import ResearchToolSuccessMessages
from app.utils.error_messages import (AgentApiErrorMessages, ResearchToolErrorMessages)

# import class response model
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import status codes from fast-api
from fastapi import status

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class VerifiedPayloadRepository:
    def __init__(self, db : Session):
        self.db = db
        debug_logger.debug(f"VerifiedPayloadRepository.__init__ | VerifiedPayloadRepository initialized | db = {self.db}")

    def insert(self, agent_id:str = None, payload:dict = None) -> RepositoryClassResponse : 
        try:
            if not agent_id or agent_id == "" or agent_id is None:
                error_logger.error(f"VerifiedPayloadRepository.insert | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            if not payload or payload is None:
                error_logger.error(f"VerifiedPayloadRepository.insert | {ResearchToolErrorMessages.VERIFIED_PAYLOAD_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=ResearchToolErrorMessages.VERIFIED_PAYLOAD_EMPTY.value
                )
            obj = VerifiedPayload(
                verified_payload=payload,
                ai_agent_id=agent_id,
            )
            self.db.add(obj)
            self.db.flush()
            self.db.refresh(obj)
            row = obj.to_dict()

            debug_logger.debug(f"VerifiedPayloadRepository.insert | {ResearchToolSuccessMessages.VERIFIED_PAYLOAD_SAVED.value} | db_result = {row}")
            return RepositoryClassResponse(
                status = True,
                status_code = status.HTTP_201_CREATED,
                message = ResearchToolSuccessMessages.VERIFIED_PAYLOAD_SAVED.value,
                data = row
            )
        except Exception as e:
            error_logger.error(f"VerifiedPayloadRepository.insert | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )
        
    def delete_all(self, agent_id:str = None) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None:
                error_logger.error(f"VerifiedPayloadRepository.delete_all | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            
            obj = delete(VerifiedPayload).where(VerifiedPayload.ai_agent_id == agent_id)
            result = self.db.execute(obj)
            self.db.flush()

            debug_logger.debug(f"VerifiedPayloadRepository.delete_all | delete_all veryfied_payload | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"VerifiedPayloadRepository.delete_all | {ResearchToolSuccessMessages.VERIFIED_PAYLOAD_DELETED.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = ResearchToolSuccessMessages.VERIFIED_PAYLOAD_DELETED.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"VerifiedPayloadRepository.delete_all | {ResearchToolErrorMessages.VERIFIED_PAYLOAD_NOT_FOUND.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = ResearchToolErrorMessages.VERIFIED_PAYLOAD_NOT_FOUND.value
                ) 
        except Exception as e:
            error_logger.error(f"VerifiedPayloadRepository.delete_all | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )