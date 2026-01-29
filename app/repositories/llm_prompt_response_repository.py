import hashlib
import time
from psycopg.rows import dict_row

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

    def insert(self,agent_id : str, llm_user_prompt_id : int, llm_prompt_response : str) -> RepositoryClassResponse:
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
            self.db.commit()
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
    
    # def update(self, agent_id: str, ai_model : str, system_prompt: str) -> RepositoryClassResponse:
    #     try:
    #         if (not system_prompt or system_prompt is None or system_prompt == "") and (not ai_model or ai_model is None or ai_model == ""):
    #             error_logger.error(f"SystemPromptRepository.update | Both system_prompt and ai_model is not provided in the request body")
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code = status.HTTP_400_BAD_REQUEST,
    #                 message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_AND_AI_MODEL_EMPTY.value
    #             )
            
    #         # Fetch existing record
    #         stmt = select(SystemPrompt).where(
    #             SystemPrompt.ai_agent_id == agent_id
    #         )
    #         obj = self.db.execute(stmt).scalar_one_or_none()

    #         if not obj:
    #             error_logger.error(
    #                 f"SystemPromptRepository.update | system_prompt not found for agent_id={agent_id}"
    #             )
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
    #             )
            

        
    #          # Apply partial updates
    #         if system_prompt and system_prompt.strip():
    #             obj.llm_system_prompt = system_prompt

    #         if ai_model and ai_model.strip():
    #             obj.ai_model = ai_model

    #         # ORM handles updated_at automatically (onupdate=func.now())
    #         row = obj.to_dict()
    #         self.db.commit()
    #         self.db.refresh(obj)

    #         if not row:
    #             error_logger.error(
    #                 f"SystemPromptRepository.update | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)}"
    #             )
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code = status.HTTP_404_NOT_FOUND,
    #                 message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
    #             )
    #         debug_logger.debug(f"SystemPromptRepository.update | update system_prompt | db_response = {row}")
    #         return RepositoryClassResponse(
    #                 status = True,
    #                 status_code = status.HTTP_200_OK,
    #                 message = PromptApiSuccessMessages.SYSTEM_PROMPT_UPDATED.value,
    #                 data = row
    #             )
    #     except Exception as e:
    #         error_logger.error(f"SystemPromptRepository.update | {str(e)}")
    #         return RepositoryClassResponse(
    #             status = False,
    #             status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             message = str(e)
    #         )  
        
    # def delete(self, agent_id: str) -> RepositoryClassResponse:
    #     try:
    #         obj = delete(SystemPrompt).where(SystemPrompt.ai_agent_id == agent_id)
    #         result = self.db.execute(obj)
    #         self.db.commit()

    #         debug_logger.debug(f"SystemPromptRepository.delete | delete system_prompt | db_response = {result.rowcount > 0}")
    #         if result.rowcount > 0:
    #             debug_logger.debug(f"SystemPromptRepository.delete | {PromptApiSuccessMessages.SYSTEM_PROMPT_DELETED.value}")
    #             return RepositoryClassResponse(
    #                 status = True,
    #                 status_code = status.HTTP_204_NO_CONTENT,
    #                 message = PromptApiSuccessMessages.SYSTEM_PROMPT_DELETED.value,
    #                 data = {}
    #             ) 
    #         else:
    #             error_logger.error(f"SystemPromptRepository.delete | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)}")
    #             return RepositoryClassResponse(
    #                 status = False,
    #                 status_code = status.HTTP_404_NOT_FOUND,
    #                 message = SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
    #             ) 
    #     except Exception as e:
    #         error_logger.error(f"SystemPromptRepository.delete | {str(e)}")
    #         return RepositoryClassResponse(
    #                 status = False,
    #                 status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                 message = str(e)
    #         )
        
    # def get_one(self, agent_id: str = None) -> RepositoryClassResponse:
    #     try:
    #         if (not agent_id or agent_id is None or agent_id == ""):
    #             error_logger.error(f"SystemPromptRepository.get_one | AI agent id is not provided | agent_id = {agent_id}")
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code = status.HTTP_400_BAD_REQUEST,
    #                 message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
    #             )
            
    #         obj = select(SystemPrompt).where(SystemPrompt.ai_agent_id==agent_id)
    #         row = self.db.execute(obj).scalar_one_or_none()

    #         debug_logger.debug(f"SystemPromptRepository.get_one | get_one system prompt for agent_id = ({agent_id}) | system_prompt = {row}")
    #         if not row:
    #             error_logger.error(
    #                 f"SystemPromptRepository.get_one | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)} "
    #             )
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code = status.HTTP_404_NOT_FOUND,
    #                 message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
    #             )
    #         row = row.to_dict()
    #         debug_logger.debug(f"SystemPromptRepository.get_one | db_response = {row}")
    #         return RepositoryClassResponse(
    #                     status = True,
    #                     status_code = status.HTTP_200_OK,
    #                     message = PromptApiSuccessMessages.SYSTEM_PROMPT_FETCHED.value,
    #                     data = row
    #                 )
    #     except Exception as e:
    #         error_logger.error(f"SystemPromptRepository.get_one | {str(e)}")
    #         return RepositoryClassResponse(
    #                 status = False,
    #                 status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                 message = str(e)
    #             ) 
        
    # def get_all(self, limit : int = 10, before_id : int = None) -> RepositoryClassResponse:
    #     try:
    #         print(f"limit : {limit}, before_id : {before_id}")
    #         # hard safety cap
    #         limit = min(10 if limit <=0 else limit, 50)
    #         fetch_limit = limit + 1

    #         if before_id:
    #             obj = (
    #                 select(SystemPrompt)
    #                 .where(SystemPrompt.id<=before_id)
    #                 .order_by(SystemPrompt.created_at.desc())
    #                 .limit(fetch_limit)
    #             )
    #         else:
    #             obj = (
    #                 select(SystemPrompt)
    #                 .order_by(SystemPrompt.created_at.desc())
    #                 .limit(fetch_limit)
    #             )
    #         rows = self.db.execute(obj).scalars().all()
    #         rows = [row.to_dict() for row in rows]

    #         if not rows:
    #             error_logger.error(
    #                 f"SystemPromptRepository.get_all | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_LIST_EMPTY.value}"
    #             )
    #             return RepositoryClassResponse(
    #                 status=False,
    #                 status_code = status.HTTP_404_NOT_FOUND,
    #                 message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_LIST_EMPTY.value,
    #                 data={
    #                     "items": [],
    #                     "next_cursor": None,
    #                     "has_more": False
    #                 }
    #             )
    #         debug_logger.debug(f"SystemPromptRepository.get_all | before_id={before_id}, limit={limit} |db_response = {rows}")

    #         has_more = len(rows) > limit

    #         # Trim extra row if it exists
    #         items = rows[:limit]

    #         next_cursor = items[-1]["id"] if has_more else None

    #         return RepositoryClassResponse(
    #                     status = True,
    #                     status_code = status.HTTP_200_OK,
    #                     message = PromptApiSuccessMessages.SYSTEM_PROMPT_FETCHED.value,
    #                     data={
    #                         "items": rows,
    #                         "next_cursor": next_cursor,
    #                         "has_more": has_more
    #                     }
    #                 )
    #     except Exception as e:
    #         error_logger.error(f"UserPromptRepository.get_all | {str(e)}")
    #         return RepositoryClassResponse(
    #                 status = False,
    #                 status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                 message = str(e)
    #             ) 