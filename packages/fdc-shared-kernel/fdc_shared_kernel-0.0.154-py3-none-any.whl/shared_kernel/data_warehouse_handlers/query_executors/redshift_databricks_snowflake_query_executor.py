import time

from typing import Any, Dict, List, Optional, Tuple
from redshift_connector.error import (
    InterfaceError as RedshiftInterfaceError,
    ProgrammingError as RedshiftProgrammingError,
    OperationalError as RedshiftOperationalError,
)

from shared_kernel.data_warehouse_handlers.utils import extract_error_message, get_column_info
from shared_kernel.interfaces.query_executor import DataWarehouseQueryExecutor
from shared_kernel.interfaces.warehouse_connection import DataWarehouseConnection
from shared_kernel.logger import Logger
from shared_kernel.config import Config


config = Config()
logger = Logger(config.get("APP_NAME"))


class RedshiftDatabricksSnowflakeQueryExecutor(DataWarehouseQueryExecutor):
    
    def __init__(self, warehouse_connection: DataWarehouseConnection) -> None:
        self.warehouse_connection = warehouse_connection

    def execute_query_and_get_metadata(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a query with automatic connection management"""
        with self.warehouse_connection.get_connection() as cursor:
            try:
                logger.info(f"Executing query: {query}")
                cursor.execute(query, params)
                metadata = get_column_info(cursor.ps["row_desc"])
                return metadata
            except (RedshiftOperationalError, RedshiftProgrammingError, RedshiftInterfaceError) as e:
                logger.error(
                    f"Failed to execute query: {query} due to exception {str(e)}",
                    exc_info=True,
                )
                user_friendly_msg = extract_error_message(str(e))
                raise Exception(f"RedshiftQuery execution failed: {user_friendly_msg}") from e
            except Exception as e:
                raise Exception(f"DataWarehouseQuery execution failed: {str(e)}") from e

    def fetch_results(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries"""
        with self.warehouse_connection.get_connection() as cursor:
            try:
                logger.info(f"Executing query: {query}")
                start_time = time.perf_counter()
                cursor.execute(query, params)
                time_taken = time.perf_counter() - start_time
                logger.info(
                    f"DataWarehouseQuery executed in {time_taken:.6f} seconds, {query}",
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            except Exception as e:
                user_friendly_msg = extract_error_message(str(e))
                raise Exception(f"Failed to fetch results: {user_friendly_msg}") from e

    
    def fetch_single_value(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query and return single value"""
        with self.warehouse_connection.get_connection() as cursor:
            try:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else None
            except Exception as e:
                user_friendly_msg = extract_error_message(str(e))
                raise Exception(
                    f"Failed to fetch single value: {user_friendly_msg}"
                ) from e

    
    def fetch_column_combinations(
        self, query: str, params: Optional[tuple] = None
    ) -> Tuple[List[tuple], List[str]]:
        """Execute query and return column combinations with headers"""
        with self.warehouse_connection.get_connection() as cursor:
            try:
                cursor.execute(query, params)
                return cursor.fetchall(), [col[0] for col in cursor.description]
            except Exception as e:
                user_friendly_msg = extract_error_message(str(e))
                raise Exception(
                    f"Failed to fetch column combinations: {user_friendly_msg}"
                ) from e

    
    def execute_distinct_column_value_query(self, query):
        try:
            with self.warehouse_connection.get_connection() as cursor:
                cursor.execute(query)
                distinct_values = [row[0] for row in cursor.fetchall()]
                return distinct_values
        except (RedshiftOperationalError, RedshiftProgrammingError, RedshiftInterfaceError) as e:
            logger.error(
                f"Failed to execute query: {query} due to exception {str(e)}",
                exc_info=True,
            )
            user_friendly_msg = extract_error_message(str(e))
            raise Exception(f"RedshiftQuery execution failed: {user_friendly_msg}") from e
        except Exception as e:
            raise Exception(f"DataWarehouseQuery execution failed: {str(e)}") from e
    

    def execute_query_get_columns_and_rows(self, query):
        try:
            with self.warehouse_connection.get_connection() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
        except (RedshiftOperationalError, RedshiftProgrammingError, RedshiftInterfaceError) as e:
            logger.error(
                f"Failed to execute query: {query} due to exception {str(e)}",
                exc_info=True,
            )
            user_friendly_msg = extract_error_message(str(e))
            raise Exception(f"RedshiftQuery execution failed: {user_friendly_msg}") from e
        except Exception as e:
            raise Exception(f"DataWarehouseQuery execution failed: {str(e)}") from e
            