import time
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, InterfaceError
from shared_kernel.data_warehouse_handlers.utils import get_column_info, make_json_serializable
from shared_kernel.interfaces.query_executor import DataWarehouseQueryExecutor
from shared_kernel.interfaces.warehouse_connection import DataWarehouseConnection
from shared_kernel.logger import Logger
from shared_kernel.config import Config


config = Config()
logger = Logger(config.get("APP_NAME"))

class SQLAlchemyQueryExecutor(DataWarehouseQueryExecutor):
    def __init__(self, warehouse_connection: DataWarehouseConnection) -> None:
        self.warehouse_connection = warehouse_connection

    def execute_query_and_get_metadata(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a query with automatic connection management"""
        with self.warehouse_connection.get_connection() as session:
            try:
                logger.info(f"Executing query: {query}")
                result = session.execute(text(query), params)
                metadata = get_column_info(result.keys())
                return metadata
            except (OperationalError, ProgrammingError, InterfaceError) as e:
                logger.error(
                    f"Failed to execute query: {query} due to exception {str(e)}",
                    exc_info=True,
                )
                raise Exception(f"Query execution failed: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Query execution failed: {str(e)}") from e


    def fetch_results(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries"""
        with self.warehouse_connection.get_connection() as session:
            try:
                logger.info(f"Executing query: {query}")
                start_time = time.perf_counter()
                result = session.execute(text(query), params)
                time_taken = time.perf_counter() - start_time
                logger.info(f"Query executed in {time_taken:.6f} seconds, {query}")
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
            except Exception as e:
                raise Exception(f"Failed to fetch results: {str(e)}") from e


    def fetch_single_value(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query and return single value"""
        with self.warehouse_connection.get_connection() as session:
            try:
                result = session.execute(text(query), params)
                row = result.fetchone()
                return row[0] if row else None
            except Exception as e:
                raise Exception(f"Failed to fetch single value: {str(e)}") from e


    def fetch_column_combinations(self, query: str, params: Optional[tuple] = None) -> Tuple[List[tuple], List[str]]:
        """Execute query and return column combinations with headers"""
        with self.warehouse_connection.get_connection() as session:
            try:
                result = session.execute(text(query), params)
                return result.fetchall(), result.keys()
            except Exception as e:
                raise Exception(f"Failed to fetch column combinations: {str(e)}") from e


    def execute_distinct_column_value_query(self, query: str) -> List[Any]:
        """Execute query and return distinct column values"""
        with self.warehouse_connection.get_connection() as session:
            try:
                result = session.execute(text(query))
                return [row[0] for row in result.fetchall()]
            except (OperationalError, ProgrammingError, InterfaceError) as e:
                logger.error(
                    f"Failed to execute query: {query} due to exception {str(e)}",
                    exc_info=True,
                )
                raise Exception(f"Query execution failed: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Query execution failed: {str(e)}") from e


    def execute_query_get_columns_and_rows(self, query: str) -> Dict[str, Any]:
        with self.warehouse_connection.get_connection() as session:
            try:
                result = session.execute(text(query))
                columns = [col for col in result.keys()]
                rows = result.fetchall()
                result_dict = {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
                return make_json_serializable(result_dict)
            except (OperationalError, ProgrammingError, InterfaceError) as e:
                logger.error(
                    f"Failed to execute query: {query} due to exception {str(e)}",
                    exc_info=True,
                )
                raise Exception(f"Query execution failed: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Query execution failed: {str(e)}") from e
            