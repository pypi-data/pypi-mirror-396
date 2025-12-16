from pypika import MSSQLQuery
from shared_kernel.interfaces.data_warehouse_handler import WarehouseHandler

from shared_kernel.dataclasses.warehouse_configs import MSSQLConfig
from shared_kernel.data_warehouse_handlers.connections.mssql_warehouse_connection import MSSQLWarehouseConnection
from shared_kernel.data_warehouse_handlers.query_executors.sqlalchemy_query_executor import SQLAlchemyQueryExecutor


class MSSQLWarehouseHandler(WarehouseHandler):

    def __init__(self, payload: dict=None):
        super().__init__(payload)
        self.payload = payload or {}
        self.organization_license_type = self.payload.get("organization_license_type")
        self.organization_id = self.payload.get("organization_id")

    def get_config(self) -> MSSQLConfig:
        return MSSQLConfig(
            username=str(self.payload.get("user")).strip(),
            password=str(self.payload.get("password")).strip(),
            host=str(self.payload.get("host")).strip(),
            database=str(self.payload.get("database")).strip(),
            port=str(self.payload.get("port")).strip(),
            schema=str(self.payload.get("schema")).strip() if self.payload.get("schema") else None,
            schema_list=self.payload.get("schema_list"),
            pagination=self.pagination
        )

    def get_connection_object(self) -> MSSQLWarehouseConnection:
        self.connection = MSSQLWarehouseConnection(
            source_config=self.get_config()
        )
        return self.connection
    
    def get_query_executor_object(self) -> SQLAlchemyQueryExecutor:
        self.query_executor = SQLAlchemyQueryExecutor(warehouse_connection=self.connection)
        return self.query_executor
    
    def get_query_object(self) -> MSSQLQuery:
        return MSSQLQuery
    