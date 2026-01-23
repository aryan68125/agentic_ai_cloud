import hashlib
import time
from psycopg.rows import dict_row

# import repositories
from app.repositories.ai_agent_repository import AIAgentRepository

# import messages
from app.utils.success_messages import (PromptApiSuccessMessages, UserPromptApiSuccessMessages)
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
    def __init__(self, pool):
        self.pool = pool
        self._init()
        debug_logger.debug(f"UserPromptRepository.__init__ | UserPromptRepository initialized | pool = {self.pool}")
        self.ai_agent_repo = AIAgentRepository(pool=self.pool)

    def _init(self):
        with self.pool.connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS user_prompt_table (
                id BIGSERIAL PRIMARY KEY,
                llm_user_prompt TEXT NOT NULL,
                ai_agent_id TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            )
            """)
        debug_logger.debug(f"UserPromptRepository.__init__ | create user_prompt_table if not exist in the database")

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
                debug_logger.debug(f"UserPromptRepository.insert | User prompt is not provided in the request | user_prompt = {agent_id}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            if not user_prompt or user_prompt is None or user_prompt == "":
                debug_logger.debug(f"UserPromptRepository.insert | User prompt is not provided in the request | user_prompt = {user_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_EMPTY.value
                )
            result = self.check_if_ai_agent_name_exists(agent_id)
            if not result.status:
                return RepositoryClassResponse(
                        status = result.status,
                        status_code = result.status_code,
                        message = result.message
                    )
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute("""
                    INSERT INTO user_prompt_table (
                        llm_user_prompt,
                        ai_agent_id,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, now(), now())
                    RETURNING id, llm_user_prompt, ai_agent_id, created_at, updated_at
                """, (user_prompt, agent_id)).fetchone()
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
                debug_logger.debug(f"UserPromptRepository.update | User prompt is not provided in the request | user_prompt = {user_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_EMPTY.value
                )
            if not user_prompt_id or user_prompt_id is None:
                debug_logger.debug("UserPromptRepository.update | User prompt primary key is required to be able to update the user prompt record")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value
                )
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute("""
                    UPDATE user_prompt_table
                    SET
                        llm_user_prompt = %s,
                        updated_at = now()
                    WHERE id = %s
                    RETURNING id, llm_user_prompt, ai_agent_id, created_at, updated_at
                """, (user_prompt, user_prompt_id)).fetchone()

            if not row:
                debug_logger.debug(
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
                debug_logger.debug("UserPromptRepository.delete | User prompt primary key is required to be able to delete the user prompt record")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=UserPromptApiErrorMessages.USER_PROMPT_ID_EMPTY.value
                )
            with self.pool.connection() as conn:
                cur = conn.execute(
                    "DELETE FROM user_prompt_table WHERE id = %s",
                    (user_prompt_id,)
                )
            debug_logger.debug(f"UserPromptRepository.delete | delete user_prompt | db_response = {cur.rowcount > 0}")
            if cur.rowcount > 0:
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = UserPromptApiSuccessMessages.USER_PROMPT_DELETED.value,
                    data = {}
                ) 
            else:
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = UserPromptApiErrorMessages.USER_PROMPT_NOT_FOUND.value.format(user_prompt_id)
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
                debug_logger.debug(f"UserPromptRepository.get_all | AI agent id is not provided")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            # hard safety cap
            limit = min(10 if limit <=0 else limit, 50)
            fetch_limit = limit + 1  # 👈 key fix

            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                # keeps getting (older message)
                if before_id:
                    rows = conn.execute(
                        """
                        SELECT *
                        FROM user_prompt_table
                        WHERE ai_agent_id = %s
                        AND id < %s
                        ORDER BY id DESC
                        LIMIT %s
                        """,
                        (agent_id, before_id, fetch_limit)
                    ).fetchall()
                else:
                    # first page (latest messages)
                    rows = conn.execute(
                        """
                        SELECT *
                        FROM user_prompt_table
                        WHERE ai_agent_id = %s
                        ORDER BY id DESC
                        LIMIT %s
                        """,
                        (agent_id, fetch_limit)
                    ).fetchall()

            if not rows:
                debug_logger.debug(
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