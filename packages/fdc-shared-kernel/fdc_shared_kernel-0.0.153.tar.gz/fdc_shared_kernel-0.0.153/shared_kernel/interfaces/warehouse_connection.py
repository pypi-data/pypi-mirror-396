"""Base interface for data warehouse connections."""

from abc import ABC, abstractmethod


class DataWarehouseConnection(ABC):
    """Abstract base class for data warehouse connections."""

    def __init__(self, source_config=None) -> None:
        super().__init__()
        self.page = None
        self.limit = None
        self.search = None

        if source_config and getattr(source_config, "pagination", None):
            self.page = source_config.pagination.get("page")
            self.limit = source_config.pagination.get("limit")
            self.search = source_config.pagination.get("search")

    @abstractmethod
    def get_connection(self, retries: int, delay: int):
        """Get a database connection with retry logic."""
        pass

    @abstractmethod
    def is_valid_connection(self):
        """Validate the current connection."""
        pass

    @abstractmethod
    def close_connection(self):
        """Close the database connection."""
        pass
