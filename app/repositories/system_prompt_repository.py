import hashlib
import time
from psycopg.rows import dict_row

# import repositories
from app.repositories.ai_agent_repository import AIAgentRepository

# import messages
from app.utils.success_messages import PromptApiSuccessMessages
from app.utils.error_messages import (PromptApiErrorMessages,AgentApiErrorMessages,SystemPromptApiErrorMessages)

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
    def __init__(self, pool):
        self.pool = pool
        self._init()
        debug_logger.debug(f"SystemPromptRepository.__init__ | SystemPromptRepository initialized | pool = {self.pool}")
        self.ai_agent_repo = AIAgentRepository(pool=self.pool)

    def _init(self):
        with self.pool.connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS system_prompt_table (
                id BIGSERIAL PRIMARY KEY,
                llm_system_prompt TEXT NOT NULL,
                ai_agent_id TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            )
            """)
        debug_logger.debug(f"SystemPromptRepository.__init__ | create system_prompt_table if not exist in the database")

    def check_if_ai_agent_name_exists(self, agent_id : str) -> RepositoryClassResponse:
        try:
            result = self.ai_agent_repo.get_one(
                    agent_id=agent_id
                )
            if not result.status:
                error_logger.error(f"AgentController.check_if_ai_agent_name_exists | operation_type = {DbRecordLevelOperationType.GET_ONE.value} | error = {result.message}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"AgentController.check_if_ai_agent_name_exists | result = {result}")
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
    
    def insert(self,agent_id : str, system_prompt : str) -> RepositoryClassResponse:
        try:
            if not system_prompt or system_prompt is None or system_prompt == "":
                debug_logger.debug(f"SystemPromptRepository.update | System prompt is not provided in the request | system_prompt = {system_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_EMPTY.value
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
                    INSERT INTO system_prompt_table (
                        llm_system_prompt,
                        ai_agent_id,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, now(), now())
                    RETURNING id, llm_system_prompt, ai_agent_id, created_at, updated_at
                """, (system_prompt, agent_id)).fetchone()
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
    
    def update(self, agent_id: str, system_prompt: str) -> RepositoryClassResponse:
        try:
            if not system_prompt or system_prompt is None or system_prompt == "":
                debug_logger.debug(f"SystemPromptRepository.update | System prompt is not provided in the request | system_prompt = {system_prompt}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_EMPTY.value
                )
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute("""
                    UPDATE system_prompt_table
                    SET
                        llm_system_prompt = %s,
                        updated_at = now()
                    WHERE ai_agent_id = %s
                    RETURNING id, llm_system_prompt, ai_agent_id, created_at, updated_at
                """, (system_prompt, agent_id)).fetchone()

            if not row:
                debug_logger.debug(
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
            with self.pool.connection() as conn:
                cur = conn.execute(
                    "DELETE FROM system_prompt_table WHERE ai_agent_id = %s",
                    (agent_id,)
                )
            debug_logger.debug(f"SystemPromptRepository.delete | delete system_prompt | db_response = {cur.rowcount > 0}")
            if cur.rowcount > 0:
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = PromptApiSuccessMessages.SYSTEM_PROMPT_DELETED.value,
                    data = {}
                ) 
            else:
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
                debug_logger.debug(f"SystemPromptRepository.get_one | AI agent id is not provided | agent_id = {agent_id}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute(
                    "SELECT * FROM ai_agent_table WHERE ai_agent_id = %s",
                    (agent_id,)
                ).fetchone()
                debug_logger.debug(f"AIAgentRepository.get_one | get_one system prompt for agent_id = ({agent_id}) | system_prompt = {row}")
            if not row:
                debug_logger.debug(
                    f"AIAgentRepository.get_one | {SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)} "
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=SystemPromptApiErrorMessages.SYSTEM_PROMPT_NOT_FOUND.value.format(agent_id)
                )
            debug_logger.debug(f"AIAgentRepository.get_one | db_response = {row}")
            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = PromptApiSuccessMessages.SYSTEM_PROMPT_FETCHED.value,
                        data = row
                    )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.get_one | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 