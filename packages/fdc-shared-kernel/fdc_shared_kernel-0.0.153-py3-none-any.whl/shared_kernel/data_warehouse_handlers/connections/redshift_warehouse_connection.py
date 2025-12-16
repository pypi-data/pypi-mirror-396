import time
import errno
import redshift_connector

from typing import Optional
from contextlib import contextmanager
from redshift_connector.error import InterfaceError, ProgrammingError, OperationalError

from shared_kernel.dataclasses.warehouse_configs import RedshiftConfig
from shared_kernel.interfaces.warehouse_connection import DataWarehouseConnection
from shared_kernel.exceptions.http_exceptions import BadRequest

from shared_kernel.logger import Logger
from shared_kernel.config import Config

config = Config()
logger = Logger(config.get("APP_NAME"))



class RedshiftWarehouseConnection(DataWarehouseConnection):

    LIST_SCHEMAS_QUERY = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('pg_catalog','information_schema') 
        ORDER BY schema_name;
    """

    def __init__(
        self,
        organization_license_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        source_config: Optional[RedshiftConfig] = None,
        set_default_schema: bool = True,
    ):
        """
        Initialize a data warehouse connection with appropriate configuration.

        Args:
            organization_license_type: The license type of the organization (e.g. "BI")
            organization_id: The ID of the organization or tenant
            redshift_config: The Redshift configuration to use for connections
            set_default_schema: Flag indicating if default schema is to be set
        """
        super().__init__(source_config)
        self._conn = None
        self._cursor = None
        self._redshift_config = source_config
        self.org_schema = None
        self.set_default_schema = set_default_schema

        if self._redshift_config and self._redshift_config.schema:
            self.org_schema = self._redshift_config.schema


    def is_redshift_maintenance_error(self, exc: Exception) -> bool:
        """Detect if error is likely due to Redshift maintenance or reboot."""
        err = exc
        while hasattr(err, "__cause__") and err.__cause__:
            err = err.__cause__

        if isinstance(err, ConnectionRefusedError):
            return err.errno in (errno.ECONNREFUSED, 10061)

        if isinstance(err, InterfaceError):
            if "ConnectionRefusedError" in str(err):
                return True

        return False

    @contextmanager
    def get_connection(self, retries: int = 3, delay: float = 5):
        """Context manager for database connections with retry mechanism"""
        if self._conn is not None and self.is_valid_connection():
            try:
                yield self._cursor
            except Exception as e:
                self._conn.rollback()
                raise e
            finally:
                self._conn.commit()
            return

        for attempt in range(retries):
            try:
                try:
                    cfg = self._redshift_config
                    logger.debug(
                        f"Redshift connection configuration: {cfg.__dict__}"
                    )
                    self._conn = redshift_connector.connect(
                        host=cfg.host,
                        database=cfg.database,
                        port=int(cfg.port),
                        user=cfg.username,
                        password=cfg.password,
                    )
                except (InterfaceError, OperationalError, ProgrammingError) as e:
                    # Handle errors due to maintenance/reeboot of redshift cluster
                    if self.is_redshift_maintenance_error(e):
                        last_error = Exception(
                            "Unable to connect to Redshift. The cluster might be unavailable or undergoing maintenance."
                        )
                        logger.warning(
                            f"Unable to connect to Redshift. The cluster might be unavailable or undergoing maintenance.: {e}"
                        )
                        if attempt < retries - 1:
                            time.sleep(delay)
                            delay += 5  # Incremental backoff
                            continue  # Retry
                        else:
                            raise last_error from e

                    error_dict: dict = e.args[0]
                    error_message = (
                        error_dict.get("M")
                        if isinstance(error_dict, dict)
                        else "Invalid connection details"
                    )
                    raise BadRequest(error_message.capitalize()) from e

                self._cursor = self._conn.cursor()

                if not self.is_valid_connection():
                    raise BadRequest("Connection validation failed")

                self._cursor.execute(
                    "SET enable_case_sensitive_identifier TO on;")

                if self.org_schema and self.set_default_schema:
                    # setting schema for query that does not have a schema in it.
                    logger.info(
                        f"Executing query in {self.org_schema}")
                    self._cursor.execute(
                        f"SET search_path TO {self.org_schema};")

                try:
                    yield self._cursor
                except Exception as e:
                    self._conn.rollback()
                    raise e
                finally:
                    self._conn.commit()
                    self.close_connection()
                return
            except Exception as e:
                raise e
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
                raise BadRequest(f"{str(e)}") from e

    def is_valid_connection(self) -> bool:
        """Validate connection with a simple query"""
        try:
            if self._cursor is None:
                return False
            self._cursor.execute(
                "SELECT current_user, current_database(), version();")
            user, db, version = self._cursor.fetchone()
            logger.debug(
                f"Connected as {user} to {db}, version: {version}")
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
