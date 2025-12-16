from typing import Dict, Any
from ._base_connection import BaseDBConnectionWidget


class OWOracleConnection(BaseDBConnectionWidget):
    name = "Oracle"
    id = "dbconnections-oracle-connection"
    description = "Koneksi ke Oracle Database. Output: SQLAlchemy Engine."
    icon = "icons/oracle.png"

    DB_KIND = "Oracle"
    DEFAULT_PORT = 1521  # port default listener Oracle

    def _build_url(self, params: Dict[str, Any]) -> str:
        """
        Bangun SQLAlchemy URL untuk Oracle (cx_Oracle).

        Field "Database/Schema/Path" di form diisi dengan SERVICE_NAME,
        misalnya: ORCLPDB1
        """
        user = params.get("user") or ""
        pwd = params.get("password") or ""
        host = params.get("host") or "localhost"
        port = params.get("port") or 1521
        service = params.get("database") or ""  # SERVICE_NAME

        # auth
        auth = ""
        if user:
            if pwd:
                auth = f"{user}:{pwd}@"
            else:
                auth = f"{user}@"

        # easy connect dengan service_name
        if service:
            dsn = f"{host}:{port}/?service_name={service}"
        else:
            dsn = f"{host}:{port}"

        return f"oracle+cx_oracle://{auth}{dsn}"
