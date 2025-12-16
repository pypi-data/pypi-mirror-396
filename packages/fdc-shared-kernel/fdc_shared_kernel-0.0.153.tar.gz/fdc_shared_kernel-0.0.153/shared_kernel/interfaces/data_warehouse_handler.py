from abc import ABC, abstractmethod


class WarehouseHandler(ABC):
    """Base abstract class for data warehouse handlers."""

    def __init__(self, payload: dict = None):
        self.payload = payload or {}
        self.pagination = self.payload.get("pagination")

    @abstractmethod
    def get_config(self):
        """Return the configuration object for the specific warehouse."""
        pass

    @abstractmethod
    def get_connection_object(self):
        """Return the connection object for the warehouse."""
        pass

    @abstractmethod
    def get_query_executor_object(self):
        """Return the query executor for the warehouse."""
        pass

    @abstractmethod
    def get_query_object(self):
        """Return the query builder class for the warehouse."""
        pass
    