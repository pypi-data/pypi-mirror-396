"""Base interface for query executors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class DataWarehouseQueryExecutor(ABC):
    """Abstract base class for data warehouse query executors."""

    @abstractmethod
    def execute_query_and_get_metadata(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return metadata about the result columns."""
        pass

    @abstractmethod
    def fetch_results(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries."""
        pass

    @abstractmethod
    def fetch_single_value(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query and return a single value."""
        pass

    @abstractmethod
    def fetch_column_combinations(self, query: str, params: Optional[tuple] = None) -> Tuple[List[tuple], List[str]]:
        """Execute query and return column combinations with headers."""
        pass

    @abstractmethod
    def execute_distinct_column_value_query(self, query: str):
        """Execute a query to get distinct column values."""
        pass
