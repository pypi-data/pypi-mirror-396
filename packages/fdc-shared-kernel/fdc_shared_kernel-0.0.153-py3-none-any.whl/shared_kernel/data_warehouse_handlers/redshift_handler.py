from pypika import Query
from shared_kernel.data_warehouse_handlers.connections.redshift_warehouse_connection import RedshiftWarehouseConnection
from shared_kernel.data_warehouse_handlers.query_executors.redshift_databricks_snowflake_query_executor import RedshiftDatabricksSnowflakeQueryExecutor
from shared_kernel.dataclasses.warehouse_configs import RedshiftConfig
from shared_kernel.interfaces.data_warehouse_handler import WarehouseHandler




class RedshiftWarehouseHandler(WarehouseHandler):

    def __init__(self, payload: dict=None):
        super().__init__(payload)
        self.payload = payload or {}
        self.organization_license_type = self.payload.get("organization_license_type")
        self.organization_id = self.payload.get("organization_id")
        self.set_default_schema = self.payload.get("set_default_schema", True)

    def get_config(self) -> RedshiftConfig:
        return RedshiftConfig(
            username=str(self.payload.get("user")).strip(),
            password=str(self.payload.get("password")).strip(),
            host=str(self.payload.get("host")).strip(),
            database=str(self.payload.get("database")).strip(),
            port=str(self.payload.get("port")).strip(),
            schema=str(self.payload.get("schema")).strip() if self.payload.get("schema") else None,
            schema_list=self.payload.get("schema_list"),
            pagination=self.pagination
        )

    def get_connection_object(self) -> RedshiftWarehouseConnection:
        self.connection = RedshiftWarehouseConnection(
            organization_license_type=self.organization_license_type,
            organization_id=self.organization_id,
            source_config=self.get_config(),
            set_default_schema=self.set_default_schema
        )
        return self.connection
    
    def get_query_executor_object(self) -> RedshiftDatabricksSnowflakeQueryExecutor:
        self.query_executor = RedshiftDatabricksSnowflakeQueryExecutor(warehouse_connection=self.connection)
        return self.query_executor
    
    def get_query_object(self) -> Query:
        return Query
    