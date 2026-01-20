import psycopg
from app.configs.config import ProjectConfigurations
from app.utils.logger import LoggerFactory

# Initialize the logger
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class DatabaseBootstrap:
    @staticmethod
    def ensure_database_exists():
        """
        Connects to the postgres system DB and ensures
        the application database exists.
        """
        info_logger.info(f"DatabaseBootstrap.ensure_database_exists | Connects to the postgres system DB and ensures the application database exists")
        dsn = ProjectConfigurations.DB_CONNECTION_STRING.value
        debug_logger.debug(f"DatabaseBootstrap.ensure_database_exists | db_connection_string = {dsn}")

        # Extract DB name
        db_name = dsn.rsplit("/", 1)[-1]
        debug_logger.debug(f"DatabaseBootstrap.ensure_database_exists | db_name = {db_name}")

        # Connect to system database
        system_dsn = dsn.replace(f"/{db_name}", "/postgres")

        with psycopg.connect(system_dsn, autocommit=True) as conn:
            cur = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,)
            )
            exists = cur.fetchone()

            if not exists:
                debug_logger.debug(f"Creating database: {db_name}")
                conn.execute(f'CREATE DATABASE "{db_name}"')
            else:
                debug_logger.debug(f"Database already exists: {db_name}")
