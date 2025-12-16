from pypika import Query

from shared_kernel.data_warehouse_handlers.connections.postgresql_warehouse_connection import PostgreSQLWarehouseConnection
from shared_kernel.data_warehouse_handlers.query_executors.sqlalchemy_query_executor import SQLAlchemyQueryExecutor
from shared_kernel.dataclasses.warehouse_configs import PostgreSQLConfig
from shared_kernel.interfaces.data_warehouse_handler import WarehouseHandler


class PostgreSQLWarehouseHandler(WarehouseHandler):

    def __init__(self, payload: dict=None):
        super().__init__(payload)
        self.payload = payload or {}
        self.organization_license_type = self.payload.get("organization_license_type")
        self.organization_id = self.payload.get("organization_id")

    def get_config(self) -> PostgreSQLConfig:
        return PostgreSQLConfig(
            username=str(self.payload.get("user")).strip(),
            password=str(self.payload.get("password")).strip(),
            host=str(self.payload.get("host")).strip(),
            database=str(self.payload.get("database")).strip(),
            port=str(self.payload.get("port")).strip(),
            schema=str(self.payload.get("schema")).strip(),
            schema_list=self.payload.get("schema_list"),
            pagination=self.pagination
        )

    def get_connection_object(self) -> PostgreSQLWarehouseConnection:
        self.connection = PostgreSQLWarehouseConnection(
            source_config=self.get_config()
        )
        return self.connection
    
    def get_query_executor_object(self) -> SQLAlchemyQueryExecutor:
        self.query_executor = SQLAlchemyQueryExecutor(warehouse_connection=self.connection)
        return self.query_executor
    
    def get_query_object(self) -> Query:
        return Query
    