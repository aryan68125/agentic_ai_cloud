import hashlib
import time
from psycopg.rows import dict_row

class AIAgentRepository:
    def __init__(self, pool):
        self.pool = pool
        self._init()

    def _init(self):
        with self.pool.connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_agent_table (
                id BIGSERIAL PRIMARY KEY,
                ai_agent_name TEXT NOT NULL UNIQUE,
                ai_agent_id TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ DEFAULT now()
            )
            """)

    def _generate_agent_id(self, agent_name: str) -> str:
        raw = f"{agent_name}_{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    # ---------- CRUD OPERATIONS ----------

    def insert(self, agent_name: str) -> dict:
        agent_id = self._generate_agent_id(agent_name)

        with self.pool.connection() as conn:
            conn.row_factory = dict_row
            row = conn.execute("""
                INSERT INTO ai_agent_table (ai_agent_name, ai_agent_id)
                VALUES (%s, %s)
                RETURNING id, ai_agent_name, ai_agent_id
            """, (agent_name, agent_id)).fetchone()

        return row

    def update(self, agent_id: str, new_name: str) -> dict:
        with self.pool.connection() as conn:
            conn.row_factory = dict_row
            row = conn.execute("""
                UPDATE ai_agent_table
                SET ai_agent_name = %s
                WHERE ai_agent_id = %s
                RETURNING id, ai_agent_name, ai_agent_id
            """, (new_name, agent_id)).fetchone()

        return row if row else None

    def delete(self, agent_id: str) -> bool:
        with self.pool.connection() as conn:
            cur = conn.execute(
                "DELETE FROM ai_agent_table WHERE ai_agent_id = %s",
                (agent_id,)
            )
            return cur.rowcount > 0

    def get_one(self, agent_id: str = None, agent_name: str = None) -> dict | None:
        with self.pool.connection() as conn:
            conn.row_factory = dict_row
            if agent_id:
                row = conn.execute(
                    "SELECT * FROM ai_agent_table WHERE ai_agent_id = %s",
                    (agent_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM ai_agent_table WHERE ai_agent_name = %s",
                    (agent_name,)
                ).fetchone()

        return row if row else None

    def get_all(self) -> list[dict]:
        with self.pool.connection() as conn:
            conn.row_factory = dict_row
            rows = conn.execute(
                "SELECT * FROM ai_agent_table ORDER BY created_at DESC"
            ).fetchall()

        return [r for r in rows]
