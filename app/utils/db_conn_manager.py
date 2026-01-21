import psycopg
from psycopg_pool import ConnectionPool
from app.configs.config import ProjectConfigurations

class PostgresConnectionManager:
    _pool: ConnectionPool | None = None

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        if cls._pool is None:
            cls._pool = ConnectionPool(
                conninfo=ProjectConfigurations.DB_CONNECTION_STRING.value,
                min_size=1,
                max_size=10,
                open=True,
            )
        return cls._pool