import hashlib
import time
from psycopg.rows import dict_row

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

    def insert(self, agent_name: str) -> dict:
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
        return row

    def update(self, agent_id: str, new_name: str) -> dict:
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
        debug_logger.debug(f"AIAgentRepository.update | update agent_name | db_response = {row if row else None}")
        return row if row else None

    def delete(self, agent_id: str) -> bool:
        with self.pool.connection() as conn:
            cur = conn.execute(
                "DELETE FROM ai_agent_table WHERE ai_agent_id = %s",
                (agent_id,)
            )
        debug_logger.debug(f"AIAgentRepository.delete | delete agent_name | db_response = {cur.rowcount > 0}")
        return cur.rowcount > 0

    def get_one(self, agent_id: str = None, agent_name: str = None) -> dict | None:
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
        debug_logger.debug(f"AIAgentRepository.get_one | db_response = {row if row else None}")
        return row if row else None

    def get_all(self) -> list[dict]:
        with self.pool.connection() as conn:
            conn.row_factory = dict_row
            rows = conn.execute(
                "SELECT * FROM ai_agent_table ORDER BY created_at DESC"
            ).fetchall()
        debug_logger.debug(f"AIAgentRepository.get_all | get all db records | db_response = {[r for r in rows]}")
        return [r for r in rows]
