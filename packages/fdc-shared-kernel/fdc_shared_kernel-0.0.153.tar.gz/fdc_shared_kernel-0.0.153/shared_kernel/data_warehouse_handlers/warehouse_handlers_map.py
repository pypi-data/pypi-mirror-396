"""Factory map for warehouse handlers based on connection engine type."""

from shared_kernel.data_warehouse_handlers.mssql_handler import MSSQLWarehouseHandler
from shared_kernel.data_warehouse_handlers.postgres_handler import PostgreSQLWarehouseHandler
from shared_kernel.data_warehouse_handlers.redshift_handler import RedshiftWarehouseHandler
from shared_kernel.data_warehouse_handlers.snowflake_handler import SnowflakeWarehouseHandler
from shared_kernel.enums.connection_engine import ConnectionEngine


warehouse_handlers = {
    ConnectionEngine.REDSHIFT.value: RedshiftWarehouseHandler,
    ConnectionEngine.MSSQL.value: MSSQLWarehouseHandler,
    ConnectionEngine.SNOWFLAKE.value: SnowflakeWarehouseHandler,
    ConnectionEngine.POSTGRES.value: PostgreSQLWarehouseHandler,
    ConnectionEngine.FACTWEAVERS_DW.value: RedshiftWarehouseHandler,
}
