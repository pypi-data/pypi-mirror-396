"""Factory function for creating warehouse handlers based on connector type."""

from typing import Optional

from shared_kernel.data_warehouse_handlers.warehouse_handlers_map import warehouse_handlers
from shared_kernel.interfaces.data_warehouse_handler import WarehouseHandler


def get_warehouse_handler(connector_type: str, config: dict) -> WarehouseHandler:
    """
    Factory function to get the appropriate warehouse handler based on connector type.
    
    Args:
        connector_type: The type of warehouse connector (e.g., 'redshift', 'databricks', 'snowflake')
        config: Configuration dictionary for the warehouse connection
        
    Returns:
        WarehouseHandler: An instance of the appropriate warehouse handler
        
    Raises:
        ValueError: If the connector type is not supported
        
    """
    handler_class = warehouse_handlers.get(connector_type)
    
    if handler_class is None:
        supported_types = ', '.join(warehouse_handlers.keys())
        raise ValueError(
            f"Unsupported connector type: '{connector_type}'. "
            f"Supported types are: {supported_types}"
        )
    
    return handler_class(config)


def get_available_connectors() -> list[str]:
    """
    Get a list of all available connector types.
    
    Returns:
        list[str]: List of supported connector type names
    """
    return list(warehouse_handlers.keys())
