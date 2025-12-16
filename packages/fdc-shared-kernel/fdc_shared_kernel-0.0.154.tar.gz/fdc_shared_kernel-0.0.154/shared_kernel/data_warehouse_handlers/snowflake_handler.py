from pypika import Query

from shared_kernel.data_warehouse_handlers.connections.snowflake_warehouse_connection import SnowflakeWarehouseConnection
from shared_kernel.data_warehouse_handlers.query_executors.redshift_databricks_snowflake_query_executor import RedshiftDatabricksSnowflakeQueryExecutor
from shared_kernel.dataclasses.warehouse_configs import SnowflakeConfig
from shared_kernel.interfaces.data_warehouse_handler import WarehouseHandler


class SnowflakeWarehouseHandler(WarehouseHandler):

    def __init__(self, payload: dict=None):
        super().__init__(payload)
        self.payload = payload or {}
        self.organization_license_type = self.payload.get("organization_license_type")
        self.organization_id = self.payload.get("organization_id")

    def get_config(self) -> SnowflakeConfig:
        return SnowflakeConfig(
            user=str(self.payload.get("user")).strip(),
            password=str(self.payload.get("password")).strip(),
            account=str(self.payload.get("account")).strip(),
            database=str(self.payload.get("database")).strip(),
            schema=str(self.payload.get("schema")).strip(),
            schema_list=self.payload.get("schema_list"),
        )    

    def get_connection_object(self) -> SnowflakeWarehouseConnection:
        self.connection = SnowflakeWarehouseConnection(
            source_config=self.get_config()
        )
        return self.connection
    
    def get_query_executor_object(self) -> RedshiftDatabricksSnowflakeQueryExecutor:
        self.query_executor = RedshiftDatabricksSnowflakeQueryExecutor(warehouse_connection=self.connection)
        return self.query_executor
    
    def get_query_object(self) -> Query:
        return Query
    