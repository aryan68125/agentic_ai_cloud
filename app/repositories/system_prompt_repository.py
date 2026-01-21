import hashlib
import time
from psycopg.rows import dict_row

class SystemPromptRepository:
    def __init__(self, pool):
        self.pool = pool
        self._init()

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
    
    def insert():
        pass