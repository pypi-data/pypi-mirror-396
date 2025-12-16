from typing import Dict, Any
from ._base_connection import BaseDBConnectionWidget


class OWClickHouseConnection(BaseDBConnectionWidget):
    name = "ClickHouse"
    id = "dbconnections-clickhouse-connection"
    description = "Koneksi ke ClickHouse (driver native)."
    icon = "icons/clickhouse.png"

    DB_KIND = "ClickHouse"
    DEFAULT_PORT = 8123  # HTTP port (clickhouse-connect)

    def _build_url(self, params: Dict[str, Any]) -> str:
        user = params.get("user") or ""
        pwd = params.get("password") or ""
        host = params.get("host") or "localhost"
        port = params.get("port") or 8123
        db = params.get("database") or ""

        auth = ""
        if user:
            if pwd:
                auth = f"{user}:{pwd}@"
            else:
                auth = f"{user}@"

        # Dialect milik clickhouse-connect
        return f"clickhousedb://{auth}{host}:{port}/{db}"
        # atau kalau mau eksplisit:
        # return f"clickhousedb+connect://{auth}{host}:{port}/{db}"

