import hashlib
import time

# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func, and_)

# imports related to database table models
from app.models.db_table_models.user_prompt_table import UserPrompt

# import repositories
from app.repositories.ai_agent_repository import AIAgentRepository

# import messages
from app.utils.success_messages import ( UserPromptApiSuccessMessages)
from app.utils.error_messages import (AgentApiErrorMessages,SystemPromptApiErrorMessages, UserPromptApiErrorMessages)

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

class UserPromptRepository:
    def __init__(self, db : Session):
        self.db = db
        debug_logger.debug(f"UserPromptRepository.__init__ | AIAgentRepository initialized | database_session = {self.db}")
        self.ai_agent_repo = AIAgentRepository(db=self.db)

    # ---------- CRUD OPERATIONS ----------

    def check_if_ai_agent_name_exists(self, agent_id : str) -> RepositoryClassResponse:
        try:
            result = self.ai_agent_repo.get_one(
                    agent_id=agent_id
                )
            if not result.status:
                error_logger.error(f"UserPromptRepository.check_if_ai_agent_name_exists | operation_type = {DbRecordLevelOperationType.GET_ONE.value} | error = {result.message}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"UserPromptRepository.check_if_ai_agent_name_exists | result = {result}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = result.status_code,
                    message = result.message,
                    data=result.data
                )
        except Exception as e:
            error_logger.error(f"UserPromptRepository.check_if_ai_agent_name_exists | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )
    
    def insert(self,agent_id : str, user_prompt : str) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"UserPromptRepository.insert | User prompt is not provided in the request | user_prompt = {agent_id}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            if not user_prompt or user_prompt is None or user_prompt == "":
                error_logger.error(f"UserPromptRepository.insert | User prompt is not provided in the request | user_prompt = {user_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_EMPTY.value
                )
            result = self.check_if_ai_agent_name_exists(agent_id)
            if not result.status:
                error_logger.error(f"UserPromptRepository.insert | result = {result}")
                return RepositoryClassResponse(
                        status = result.status,
                        status_code = result.status_code,
                        message = result.message
                    )

            obj = UserPrompt(
                llm_user_prompt=user_prompt,
                ai_agent_id=agent_id,
            )
            row = obj.to_dict()
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)

            debug_logger.debug(f"UserPromptRepository.insert | insert user_prompt | db_response = {row}")
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_201_CREATED,
                message=UserPromptApiSuccessMessages.USER_PROMPT_INSERTED.value,
                data=row
            )
        except Exception as e:
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

    def update(self, user_prompt_id: int, user_prompt: str) -> RepositoryClassResponse:
        try:
            if not user_prompt or user_prompt is None or user_prompt == "":
                error_logger.error(f"UserPromptRepository.update | User prompt is not provided in the request | user_prompt = {user_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_EMPTY.value
                )
            if not user_prompt_id or user_prompt_id is None:
                error_logger.error("UserPromptRepository.update | User prompt primary key is required to be able to update the user prompt record")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value
                )

            obj = (
                update(UserPrompt)
                .where(UserPrompt.id == user_prompt_id)
                .values(llm_user_prompt=user_prompt)
                .returning(UserPrompt)
            )
            row = self.db.execute(obj).scalar_one_or_none()
            row = row.to_dict()
            self.db.commit()

            if not row:
                error_logger.error(
                    f"UserPromptRepository.update | {UserPromptApiErrorMessages.USER_PROMPT_NOT_FOUND.value.format(user_prompt_id)}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=UserPromptApiErrorMessages.USER_PROMPT_NOT_FOUND.value.format(user_prompt_id)
                )
            debug_logger.debug(f"UserPromptRepository.update | update user_prompt | db_response = {row}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = UserPromptApiSuccessMessages.USER_PROMPT_UPDATED.value,
                    data = row
                )
        except Exception as e:
            error_logger.error(f"UserPromptRepository.update | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )  
        
    def delete(self, user_prompt_id: str) -> RepositoryClassResponse:
        try:
            if not user_prompt_id or user_prompt_id is None:
                error_logger.error(f"UserPromptRepository.delete | {UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value
                )
            
            obj = delete(UserPrompt).where(UserPrompt.id == user_prompt_id)
            result = self.db.execute(obj)
            self.db.commit()

            debug_logger.debug(f"UserPromptRepository.delete | delete user_prompt | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                debug_logger.debug(f"UserPromptRepository.delete | {UserPromptApiSuccessMessages.USER_PROMPT_DELETED.value}")
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = UserPromptApiSuccessMessages.USER_PROMPT_DELETED.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"UserPromptRepository.delete | {UserPromptApiErrorMessages.USER_PROMPT_NOT_FOUND_MESSAGE.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = UserPromptApiErrorMessages.USER_PROMPT_NOT_FOUND_MESSAGE.value
                ) 
        except Exception as e:
            error_logger.error(f"UserPromptRepository.delete | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
            )

    def get_all(self, agent_id: str = None, limit : int = 10, before_id : int = None) -> RepositoryClassResponse:
        try:
            if (not agent_id or agent_id is None or agent_id == ""):
                error_logger.error(f"UserPromptRepository.get_all | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            # hard safety cap
            limit = min(10 if limit <=0 else limit, 50)
            fetch_limit = limit + 1

            if before_id:
                obj = (
                    select(UserPrompt)
                    .where(
                        and_(
                            UserPrompt.ai_agent_id == agent_id,
                            UserPrompt.id <= before_id
                        )
                    )
                    .order_by(UserPrompt.created_at.desc())
                    .limit(fetch_limit)
                )
            else:
                obj = (
                    select(UserPrompt)
                    .where(UserPrompt.ai_agent_id==agent_id)
                    .order_by(UserPrompt.created_at.desc())
                    .limit(fetch_limit)
                )
            rows = self.db.execute(obj).scalars().all()
            rows = [row.to_dict() for row in rows]

            if not rows:
                error_logger.error(
                    f"UserPromptRepository.get_all | {UserPromptApiErrorMessages.USER_PROMPTS_NOT_FOUND.value.format(agent_id)}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=UserPromptApiErrorMessages.USER_PROMPTS_NOT_FOUND.value.format(agent_id),
                    data={
                        "items": [],
                        "next_cursor": None,
                        "has_more": False
                    }
                )
            debug_logger.debug(f"UserPromptRepository.get_all | before_id={before_id}, limit={limit} |db_response = {rows}")

            has_more = len(rows) > limit

            # Trim extra row if it exists
            items = rows[:limit]

            next_cursor = items[-1]["id"] if has_more else None

            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = UserPromptApiSuccessMessages.USER_PROMPT_FETCHED.value,
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