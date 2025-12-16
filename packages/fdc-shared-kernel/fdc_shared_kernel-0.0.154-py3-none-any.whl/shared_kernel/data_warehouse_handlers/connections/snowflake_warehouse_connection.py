import time
import snowflake.connector
from contextlib import contextmanager
from snowflake.connector.errors import (
    OperationalError,
    ProgrammingError,
    InterfaceError,
    DatabaseError,
)

from shared_kernel.data_warehouse_handlers.utils import extract_snowflake_error_message
from shared_kernel.dataclasses.warehouse_configs import SnowflakeConfig
from shared_kernel.exceptions.http_exceptions import BadRequest
from shared_kernel.interfaces.warehouse_connection import DataWarehouseConnection
from shared_kernel.config import Config
from shared_kernel.logger import Logger

config = Config()
logger = Logger(config.get("APP_NAME"))


class SnowflakeWarehouseConnection(DataWarehouseConnection):
    LIST_SCHEMAS_QUERY: str = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('INFORMATION_SCHEMA','SNOWFLAKE')
        ORDER BY schema_name;
    """
    def __init__(self, source_config: SnowflakeConfig):
        self._conn = None
        self._cursor = None
        self._snowflake_config = source_config
        self.org_schema = None

        if self._snowflake_config and self._snowflake_config.schema:
            self.org_schema = self._snowflake_config.schema

    def _create_connection_with_retry(self, retries: int = 3, delay: int = 5):
        """Try to establish a connection with retry mechanism."""
        for attempt in range(retries):
            try:
                try:
                    cfg = self._snowflake_config
                    logger.debug(f"Snowflake connection configuration: {cfg.__dict__}")

                    self._conn = snowflake.connector.connect(
                        user=cfg.user,
                        password=cfg.password,
                        account=cfg.account,
                        database=cfg.database,
                        schema=cfg.schema,
                    )

                except (InterfaceError, OperationalError, ProgrammingError, DatabaseError) as e:
                    error_message = extract_snowflake_error_message(str(e))
                    raise BadRequest(f"Connection to warehouse failed: {error_message}")

                self._cursor = self._conn.cursor()

                if not self.is_valid_connection():
                    raise BadRequest("Connection validation failed")

            except BadRequest as e:
                logger.error(
                    f"Connection attempt {attempt + 1} failed: {str(e)}",
                    exc_info=True,
                )

                if attempt == retries - 1:
                    raise BadRequest(str(e)) from e

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
    def get_connection(self, retries: int = 3, delay: float = 5):
        """Context manager for database connections with retry mechanism"""
        if not (self._conn and self.is_valid_connection()):
            self._create_connection_with_retry(retries, delay)
        try:
            yield self._cursor
        except Exception as e:
            raise e
        finally:
            self._conn.commit()
        return

    def is_valid_connection(self) -> bool:
        """Validate connection with a simple query"""
        try:
            if self._cursor is None:
                return False
            self._cursor.execute(
                "SELECT current_user, current_database(), current_version();"
            )
            user, db, version = self._cursor.fetchone()
            logger.debug(
                f"Connected as {user} to {db}, version: {version}"
            )
            return True
        except (OperationalError, ProgrammingError, InterfaceError) as e:
            logger.error(f"Exception: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            raise Exception(f"Connection failed.")

    def close_connection(self):
        """Safely close database connection"""
        try:
            if self._cursor:
                self._cursor.close()
                logger.info(
                    f"Terminated warehouse cursor connection."
                )
            if self._conn:
                self._conn.close()
                logger.info(
                    f"Terminated warehouse connection."
                )
        except Exception as e:
            logger.error(
                f"Error closing connection: {str(e)}",
                exc_info=True,
            )
        finally:
            self._cursor = None
            self._conn = None
