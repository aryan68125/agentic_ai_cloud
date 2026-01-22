import hashlib
import time
from psycopg.rows import dict_row

# import messages
from app.utils.success_messages import AiAgentApiSuccessMessage
from app.utils.error_messages import AgentApiErrorMessages

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

class AIAgentRepository:
    def __init__(self, pool):
        self.pool = pool
        self._init()
        debug_logger.debug(f"AIAgentRepository.__init__ | AIAgentRepository initialized | pool = {self.pool}")

    def _init(self):
        with self.pool.connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_agent_table (
                id BIGSERIAL PRIMARY KEY,
                ai_agent_name TEXT NOT NULL UNIQUE,
                ai_agent_id TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            )
            """)
        debug_logger.debug(f"AIAgentRepository.__init__ | create ai_agent_table if not exist in the database")

    def _generate_agent_id(self, agent_name: str) -> str:
        raw = f"{agent_name}_{time.time()}"
        ai_agent_id = hashlib.sha256(raw.encode()).hexdigest()
        debug_logger.debug(f"AIAgentRepository._generate_agent_id | generate ai_agent_id | ai_agent_id = {ai_agent_id}")
        return ai_agent_id

    # ---------- CRUD OPERATIONS ----------

    def insert(self, agent_name: str) -> RepositoryClassResponse:
        try:
            agent_id = self._generate_agent_id(agent_name)
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute("""
                    INSERT INTO ai_agent_table (
                        ai_agent_name,
                        ai_agent_id,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, now(), now())
                    RETURNING id, ai_agent_name, ai_agent_id, created_at, updated_at
                """, (agent_name, agent_id)).fetchone()
            debug_logger.debug(f"AIAgentRepository.insert | insert agent_name | db_response = {row}")
            return RepositoryClassResponse(
                status = True,
                status_code = status.HTTP_200_OK,
                message = AiAgentApiSuccessMessage.AGENT_NAME_INSERTED.value,
                data = row
            )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.insert | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )

    def update(self, agent_id: str, new_name: str) -> RepositoryClassResponse:
        try:
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                row = conn.execute("""
                    UPDATE ai_agent_table
                    SET
                        ai_agent_name = %s,
                        updated_at = now()
                    WHERE ai_agent_id = %s
                    RETURNING id, ai_agent_name, ai_agent_id, created_at, updated_at
                """, (new_name, agent_id)).fetchone()

            if not row:
                debug_logger.debug(
                    f"AIAgentRepository.update | agent not found in database | agent_id = {agent_id}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"AIAgentRepository.update | update agent_name | db_response = {row}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = AiAgentApiSuccessMessage.AGENT_NAME_UPDATED.value,
                    data = row
                )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.update | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            ) 

    def delete(self, agent_id: str) -> RepositoryClassResponse:
        try:
            with self.pool.connection() as conn:
                cur = conn.execute(
                    "DELETE FROM ai_agent_table WHERE ai_agent_id = %s",
                    (agent_id,)
                )
            debug_logger.debug(f"AIAgentRepository.delete | delete agent_name | db_response = {cur.rowcount > 0}")
            if cur.rowcount > 0:
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = AiAgentApiSuccessMessage.AGENT_NAME_DELETED.value,
                    data = {}
                ) 
            else:
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                ) 
        except Exception as e:
            error_logger.error(f"AIAgentRepository.delete | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 

    def get_one(self, agent_id: str = None, agent_name: str = None) -> RepositoryClassResponse:
        try:
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                if agent_id:
                    debug_logger.debug(f"AIAgentRepository.get_one | get_one agent_id | agent_id = {agent_id}")
                    row = conn.execute(
                        "SELECT * FROM ai_agent_table WHERE ai_agent_id = %s",
                        (agent_id,)
                    ).fetchone()
                else:
                    debug_logger.debug(f"AIAgentRepository.get_one | get_one agent_name | agent_name = {agent_name}")
                    row = conn.execute(
                        "SELECT * FROM ai_agent_table WHERE ai_agent_name = %s",
                        (agent_name,)
                    ).fetchone()
            if not row:
                debug_logger.debug(
                    f"AIAgentRepository.get_one | agent not found in database | agent_id = {agent_id}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"AIAgentRepository.get_one | db_response = {row}")
            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value,
                        data = row
                    )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.get_one | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 
        
    def _count_all(self) -> int:
        with self.pool.connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM ai_agent_table"
            ).fetchone()
        debug_logger.debug(f"AIAgentRepository._count_all | db_response = {row}")
        return row["count"]

    def get_all(self, page : int = 1, page_size : int = 10) -> RepositoryClassResponse:
        try:
            offset = (page - 1) * page_size
            with self.pool.connection() as conn:
                conn.row_factory = dict_row
                rows = conn.execute(
                    """
                        SELECT *
                        FROM ai_agent_table
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """, (page_size, offset)
                ).fetchall()
            total_records = self._count_all()
            total_pages = (total_records + page_size - 1) // page_size
            debug_logger.debug(
                "AIAgentRepository.get_all | "
                f"page={page}, page_size={page_size}, "
                f"returned_rows={len(rows)}, total_records={total_records}, total_pages={total_pages}"
            )
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_200_OK,
                message=AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value,
                data={
                    "items": rows,
                    "page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages
                }
            )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.get_all | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 
