# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func)

# imports related to database table models
from app.models.db_table_models.llm_prompt_response_table import LLMPromptResponseTable

# import repositories
from app.repositories.user_prompt_repository import UserPromptRepository

# import messages
from app.utils.success_messages import HuggingFaceAIModelAPISuccessMessage
from app.utils.error_messages import (AgentApiErrorMessages, UserPromptApiErrorMessages, LLmPromptResponseErrorMessage)

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

class LLmPromptResponseRepository:
    def __init__(self, db : Session):
        self.db = db
        debug_logger.debug(f"LLmPromptResponseRepository.__init__ | LLmPromptResponseRepository initialized | db = {self.db}")
        self.user_prompt_repo = UserPromptRepository(db=db)
        
    def check_if_user_prompt_exists(self, llm_user_prompt_id : int) -> RepositoryClassResponse:
        try:
            user_prompt_repo_result = self.user_prompt_repo.get_one(llm_user_prompt_id=llm_user_prompt_id)
            return RepositoryClassResponse(
                    status=user_prompt_repo_result.status,
                    status_code = user_prompt_repo_result.status_code,
                    message=user_prompt_repo_result.message
                )
        except Exception as e:
            error_logger.error(f"LLmPromptResponseRepository.check_if_user_prompt_exists | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

    def insert(self,agent_id : str, llm_user_prompt_id : int, llm_prompt_response : str, commit : bool = False) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"LLmPromptResponseRepository.insert | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            if not llm_user_prompt_id or llm_user_prompt_id is None or llm_user_prompt_id < 1:
                error_logger.error(f"LLmPromptResponseRepository.insert | {UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value
                )
            if not llm_prompt_response or llm_prompt_response is None or llm_prompt_response == "":
                error_logger.error(f"LLmPromptResponseRepository.insert | {LLmPromptResponseErrorMessage.LLM_PROMPT_RESPONSE_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=LLmPromptResponseErrorMessage.LLM_PROMPT_RESPONSE_EMPTY.value
                )
            result = self.check_if_user_prompt_exists(llm_user_prompt_id)
            if not result.status:
                return RepositoryClassResponse(
                        status = result.status,
                        status_code = result.status_code,
                        message = result.message
                    )
            
            obj = LLMPromptResponseTable(
                llm_user_prompt_id = llm_user_prompt_id,
                llm_prompt_response = llm_prompt_response,
                ai_agent_id = agent_id,

            )
            self.db.add(obj)
            self.db.flush()
            self.db.refresh(obj)
            row = obj.to_dict()

            debug_logger.debug(f"LLmPromptResponseRepository.insert | {HuggingFaceAIModelAPISuccessMessage.LLM_RESPONSE_INSERT.value} | db_response = {row}")
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_201_CREATED,
                message=HuggingFaceAIModelAPISuccessMessage.LLM_RESPONSE_INSERT.value,
                data=row
            )
        except Exception as e:
            error_logger.error(f"LLmPromptResponseRepository.insert | {str(e)}")
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )
        
    def delete_all(self, agent_id : str) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None:
                error_logger.error(f"LLmPromptResponseRepository.delete_all | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            
            obj = delete(LLMPromptResponseTable).where(LLMPromptResponseTable.ai_agent_id == agent_id)
            result = self.db.execute(obj)
            self.db.flush()

            debug_logger.debug(f"LLmPromptResponseRepository.delete_all | delete_all user_prompt | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"LLmPromptResponseRepository.delete_all | {HuggingFaceAIModelAPISuccessMessage.LLM_RESPONSE_DELETE.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = HuggingFaceAIModelAPISuccessMessage.LLM_RESPONSE_DELETE.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"LLmPromptResponseRepository.delete_all | {LLmPromptResponseErrorMessage.LLM_RESPONSE_NOT_FOUND.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = LLmPromptResponseErrorMessage.LLM_RESPONSE_NOT_FOUND.value
                ) 
        except Exception as e:
            error_logger.error(f"LLmPromptResponseRepository.delete_all | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
            )