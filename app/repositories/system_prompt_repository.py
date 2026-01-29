import hashlib
import time
from psycopg.rows import dict_row

# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func)

# imports related to database table models
from app.models.db_table_models.system_prompt_table import SystemPrompt

# import repositories
from app.repositories.ai_agent_repository import AIAgentRepository

# import messages
from app.utils.success_messages import PromptApiSuccessMessages
from app.utils.error_messages import (AgentApiErrorMessages,SystemPromptApiErrorMessages)

# import class response model
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import db operation type
from app.utils.db_operation_type import DbRecordLevelOperationType

# import status codes from fast-api
from fastapi import status

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class SystemPromptRepository:
    def __init__(self, db : Session):
        self.db = db
        debug_logger.debug(f"SystemPromptRepository.__init__ | SystemPromptRepository initialized | pool = {self.db}")
        self.ai_agent_repo = AIAgentRepository(db=self.db)

    def check_if_ai_agent_name_exists(self, agent_id : str) -> RepositoryClassResponse:
        try:
            result = self.ai_agent_repo.get_one(
                    agent_id=agent_id
                )
            if not result.status:
                error_logger.error(f"SystemPromptRepository.check_if_ai_agent_name_exists | operation_type = {DbRecordLevelOperationType.GET_ONE.value} | error = {result.message}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"SystemPromptRepository.check_if_ai_agent_name_exists | result = {result}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = result.status_code,
                    message = result.message,
                    data=result.data
                )
        except Exception as e:
            error_logger.error(f"SystemPromptRepository.check_if_ai_agent_name_exists | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )
    
    def insert(self,agent_id : str, ai_model : str, system_prompt : str) -> RepositoryClassResponse:
        try:
            if not system_prompt or system_prompt is None or system_prompt == "":
                error_logger.error(f"SystemPromptRepository.insert | System prompt is not provided in the request | system_prompt = {system_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_EMPTY.value
                )
            if not ai_model or ai_model is None or ai_model == "":
                error_logger.error(f"SystemPromptRepository.insert | AI model name is not provided in the request | ai_model = {ai_model}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=SystemPromptApiErrorMessages.AI_MODEL_NAME_EMPTY.value
                )
            result = self.check_if_ai_agent_name_exists(agent_id)
            if not result.status:
                return RepositoryClassResponse(
                        status = result.status,
                        status_code = result.status_code,
                        message = result.message
                    )
            
            obj = SystemPrompt(
                llm_system_prompt=system_prompt,
                ai_agent_id=agent_id,
                ai_model=ai_model
            )
            self.db.add(obj)
            self.db.flush()
            self.db.refresh(obj)
            row = obj.to_dict()

            debug_logger.debug(f"SystemPromptRepository.insert | insert system_prompt | db_response = {row}")
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_201_CREATED,
                message=PromptApiSuccessMessages.SYSTEM_PROMPT_INSERTED.value,
                data=row
            )
        except Exception as e:
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )
    
    def update(self, agent_id: str, ai_model : str, system_prompt: str) -> RepositoryClassResponse:
        try:
            if (not system_prompt or system_prompt is None or system_prompt == "") and (not ai_model or ai_model is None or ai_model == ""):
                error_logger.error(f"SystemPromptRepository.update | Both system_prompt and ai_model is not provided in the request body")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_AND_AI_MODEL_EMPTY.value
                )
            
            # Fetch existing record
            stmt = select(SystemPrompt).where(
                SystemPrompt.ai_agent_id == agent_id
            )
            obj = self.db.execute(stmt).scalar_one_or_none()

            if not obj:
                error_logger.error(
                    f"SystemPromptRepository.update | system_prompt not found for agent_id={agent_id}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
                )
            

        
             # Apply partial updates
            if system_prompt and system_prompt.strip():
                obj.llm_system_prompt = system_prompt

            if ai_model and ai_model.strip():
                obj.ai_model = ai_model

            # ORM handles updated_at automatically (onupdate=func.now())
            self.db.flush()
            self.db.refresh(obj)
            row = obj.to_dict()

            if not row:
                error_logger.error(
                    f"SystemPromptRepository.update | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
                )
            debug_logger.debug(f"SystemPromptRepository.update | update system_prompt | db_response = {row}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = PromptApiSuccessMessages.SYSTEM_PROMPT_UPDATED.value,
                    data = row
                )
        except Exception as e:
            error_logger.error(f"SystemPromptRepository.update | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )  
        
    def delete(self, agent_id: str) -> RepositoryClassResponse:
        try:
            obj = delete(SystemPrompt).where(SystemPrompt.ai_agent_id == agent_id)
            result = self.db.execute(obj)
            self.db.flush()

            debug_logger.debug(f"SystemPromptRepository.delete | delete system_prompt | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"SystemPromptRepository.delete | {PromptApiSuccessMessages.SYSTEM_PROMPT_DELETED.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = PromptApiSuccessMessages.SYSTEM_PROMPT_DELETED.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"SystemPromptRepository.delete | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
                ) 
        except Exception as e:
            error_logger.error(f"SystemPromptRepository.delete | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
            )
        
    def get_one(self, agent_id: str = None) -> RepositoryClassResponse:
        try:
            if (not agent_id or agent_id is None or agent_id == ""):
                error_logger.error(f"SystemPromptRepository.get_one | AI agent id is not provided | agent_id = {agent_id}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            
            obj = select(SystemPrompt).where(SystemPrompt.ai_agent_id==agent_id)
            row = self.db.execute(obj).scalar_one_or_none()

            debug_logger.debug(f"SystemPromptRepository.get_one | get_one system prompt for agent_id = ({agent_id}) | system_prompt = {row}")
            if not row:
                error_logger.error(
                    f"SystemPromptRepository.get_one | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)} "
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
                )
            row = row.to_dict()
            debug_logger.debug(f"SystemPromptRepository.get_one | db_response = {row}")
            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = PromptApiSuccessMessages.SYSTEM_PROMPT_FETCHED.value,
                        data = row
                    )
        except Exception as e:
            error_logger.error(f"SystemPromptRepository.get_one | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 
        
    def get_all(self, limit : int = 10, before_id : int = None) -> RepositoryClassResponse:
        try:
            print(f"limit : {limit}, before_id : {before_id}")
            # hard safety cap
            limit = min(10 if limit <=0 else limit, 50)
            fetch_limit = limit + 1

            if before_id:
                obj = (
                    select(SystemPrompt)
                    .where(SystemPrompt.id<=before_id)
                    .order_by(SystemPrompt.created_at.desc())
                    .limit(fetch_limit)
                )
            else:
                obj = (
                    select(SystemPrompt)
                    .order_by(SystemPrompt.created_at.desc())
                    .limit(fetch_limit)
                )
            rows = self.db.execute(obj).scalars().all()
            rows = [row.to_dict() for row in rows]

            if not rows:
                error_logger.error(
                    f"SystemPromptRepository.get_all | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_LIST_EMPTY.value}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_LIST_EMPTY.value,
                    data={
                        "items": [],
                        "next_cursor": None,
                        "has_more": False
                    }
                )
            debug_logger.debug(f"SystemPromptRepository.get_all | before_id={before_id}, limit={limit} |db_response = {len(rows)}")

            has_more = len(rows) > limit

            # Trim extra row if it exists
            items = rows[:limit]

            next_cursor = items[-1]["id"] if has_more else None

            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = PromptApiSuccessMessages.SYSTEM_PROMPT_FETCHED.value,
                        data={
                            "items": rows,
                            "next_cursor": next_cursor,
                            "has_more": has_more
                        }
                    )
        except Exception as e:
            error_logger.error(f"UserPromptRepository.get_all | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 