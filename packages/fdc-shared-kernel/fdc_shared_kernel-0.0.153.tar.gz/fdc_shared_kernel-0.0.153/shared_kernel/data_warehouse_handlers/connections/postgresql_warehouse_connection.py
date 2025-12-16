import time
from urllib.parse import quote
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError, InterfaceError

from shared_kernel.constants.constants import get_constant
from shared_kernel.dataclasses.warehouse_configs import PostgreSQLConfig
from shared_kernel.exceptions.http_exceptions import BadRequest
from shared_kernel.config import Config
from shared_kernel.interfaces.warehouse_connection import DataWarehouseConnection
from shared_kernel.logger import Logger

config = Config()
logger = Logger(config.get("APP_NAME"))


class PostgreSQLWarehouseConnection(DataWarehouseConnection):
    LIST_SCHEMAS_QUERY = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1', 'pg_toast_temp_1') 
        ORDER BY schema_name;
    """
    def __init__(self, source_config: PostgreSQLConfig):
        super().__init__(source_config)
        self._engine = None
        self._session = None
        self._postgres_config = source_config
        self.org_schema = None

        if self._postgres_config and self._postgres_config.schema:
            self.org_schema = self._postgres_config.schema

    def _create_connection_with_retry(self, retries: int = 3, delay: int = 5):
        """Try to establish a connection with retry mechanism."""
        for attempt in range(retries):
            try:
                try:
                    cfg = self._postgres_config
                    logger.debug(f"PostgreSQL connection configuration: {cfg.__dict__}")

                    host = cfg.host
                    port = int(cfg.port)
                    database = cfg.database
                    username = cfg.username
                    password = quote(cfg.password)

                    connection_string = get_constant(
                        "mssql", "CONNECTION_STRING"
                    ).format(username, password, host, port, database)

                    self._engine = create_engine(connection_string)
                    self._session = sessionmaker(bind=self._engine)()

                except (OperationalError, ProgrammingError, InterfaceError) as e:
                    raise BadRequest(f"Connection to warehouse failed: {str(e)}")

                if not self.is_valid_connection():
                    raise BadRequest("Connection validation failed")

            except BadRequest as e:
                logger.error(
                    f"Connection attempt {attempt + 1} failed: {str(e)}",
                    exc_info=True,
                )
                if attempt == retries - 1:
                    raise

            except Exception as e:
                logger.error(
                    f"Connection attempt {attempt + 1} failed: {str(e)}",
                    exc_info=True,
                )
                if attempt == retries - 1:
                    raise BadRequest(
                        f"Failed to connect after {retries} attempts due to {str(e)}"
                    ) from e

                time.sleep(delay)
                self.close_connection()

    @contextmanager
    def get_connection(self, retries: int = 3, delay: int = 5):
        """Context manager for database connections with retry mechanism"""
        if not (self._session and self.is_valid_connection()):
            self._create_connection_with_retry(retries, delay)
        try:
            yield self._session
        except Exception as e:
            self._session.rollback()
            raise e
        finally:
            self._session.commit()
            self.close_connection()

    def is_valid_connection(self) -> bool:
        """Validate connection with a simple query."""
        try:
            if self._session is None:
                return False
            
            result = self._session.execute(
                text("SELECT current_user, current_database(), version();")
            )
            user, db, version = result.fetchone()
            logger.debug(
                f"Connected as {user} to {db}, version: {version}"
            )
            return True
        except (OperationalError, ProgrammingError, InterfaceError) as e:
            logger.error(
                f"Connection validation error: {str(e)}"
            )
            raise e
        except Exception as e:
            logger.error(
                f"Unexpected validation failure: {str(e)}"
            )
            raise Exception(
                f"Connection validation failed."
            )

    def close_connection(self):
        """Safely close database connection"""
        try:
            if self._session:
                self._session.close()
                logger.info(f"Terminated PostgreSQL session.")
            if self._engine:
                self._engine.dispose()
                logger.info(f"Disposed PostgreSQL engine.")
        except Exception as e:
            logger.error(
                f"Error closing PostgreSQL connection: {str(e)}",
                exc_info=True,
            )
        finally:
            self._session = None
            self._engine = None
