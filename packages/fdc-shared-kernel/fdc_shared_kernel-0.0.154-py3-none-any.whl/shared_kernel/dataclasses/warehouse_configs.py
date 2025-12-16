"""Configuration dataclasses for data warehouse connections."""

from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BaseConfig(ABC):
    """Base configuration for all warehouse types."""
    schema: Optional[str]
    pagination: Optional[Dict]
    schema_list: Optional[List[str]]

    def __post_init__(self):
        if self.schema is None:
            self.schema = None
        if self.pagination is None:
            self.pagination = {}
        if self.schema_list is None:
            self.schema_list = []


@dataclass
class RedshiftConfig(BaseConfig):
    """Configuration for Amazon Redshift connections."""
    username: str
    password: str
    host: str
    database: str
    port: str
    default_schema: str = "public"


@dataclass
class MSSQLConfig(BaseConfig):
    """Configuration for Microsoft SQL Server connections."""
    username: str
    password: str
    host: str
    database: str
    port: str
    default_schema: str = "dbo"


@dataclass
class DatabricksConfig(BaseConfig):
    """Configuration for Databricks connections."""
    server_hostname: str
    http_path: str
    access_token: str
    catalog: str
    default_schema: str = "default"


@dataclass
class PostgreSQLConfig(BaseConfig):
    """Configuration for PostgreSQL connections."""
    username: str
    password: str
    host: str
    database: str
    port: str
    default_schema: str = "public"


@dataclass
class MySQLConfig(BaseConfig):
    """Configuration for MySQL connections."""
    username: str
    password: str
    host: str
    database: str
    port: str
    default_schema: str = None

    def __post_init__(self):
        super().__post_init__()
        # In MySQL, there is no separate schema, it is the same as database
        if self.schema is None:
            self.schema = self.database


@dataclass
class SnowflakeConfig:
    """Configuration for Snowflake connections."""
    user: str
    password: str
    account: str
    database: str
    schema: str = "PUBLIC"
    schema_list: Optional[List[str]] = None
