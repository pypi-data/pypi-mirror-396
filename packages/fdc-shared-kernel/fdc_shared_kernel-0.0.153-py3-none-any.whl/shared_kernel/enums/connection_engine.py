from enum import Enum


class ConnectionEngine(Enum):
    REDSHIFT = "redshift"
    MSSQL = "mssql"
    POSTGRES = "postgres"
    DATABRICKS = "databricks"
    MYSQL = "mysql"
    AZURESQL = "azuresql"
    SNOWFLAKE = "snowflake"
    FACTWEAVERS_DW = "factweavers-dw"
