import psycopg
from psycopg_pool import ConnectionPool
from app.configs.config import ProjectConfigurations

from app.utils.logger import LoggerFactory

# Initialize the logger
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class PostgresConnectionManager:
    _pool: ConnectionPool | None = None

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        try:
            info_logger.info(f"PostgresConnectionManager.get_pool | making connection to db")
            if cls._pool is None:
                cls._pool = ConnectionPool(
                    conninfo=ProjectConfigurations.DB_CONNECTION_STRING.value,
                    min_size=1,
                    max_size=10,
                    open=True,
                )
            debug_logger.debug(f"PostgresConnectionManager.get_pool | cls._pool = {cls._pool}")
            return cls._pool
        except Exception as e:
            error_logger.error(f"PostgresConnectionManager.get_pool | {str(e)}")
            raise