from .ow_pg_connection import OWPostgresConnection
from .ow_mysql_connection import OWMySQLConnection
from .ow_sqlite_connection import OWSQLiteConnection
from .ow_mssql_connection import OWMSSQLConnection
from .ow_clickhouse_connection import OWClickHouseConnection
from .ow_env_check import OWDbEnvCheck

__all__ = [
    "OWPostgresConnection",
    "OWMySQLConnection",
    "OWSQLiteConnection",
    "OWMSSQLConnection",
    "OWClickHouseConnection",
    "OWDbEnvCheck",
]

BACKGROUND = "#fdbc73"
ICON = "icons/addon_icon.png"
