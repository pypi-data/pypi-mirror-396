from typing import Dict, Any
from ._base_connection import BaseDBConnectionWidget


class OWPostgresConnection(BaseDBConnectionWidget):
    name = "PostgreSQL"
    id = "dbconnections-postgresql-connection"
    description = "Koneksi ke PostgreSQL. Output: SQLAlchemy Engine."
    icon = "icons/postgres.png"

    DB_KIND = "PostgreSQL"
    DEFAULT_PORT = 5432

    def _build_url(self, params: Dict[str, Any]) -> str:
        user = params.get("user") or ""
        pwd = params.get("password") or ""
        host = params.get("host") or ""
        port = params.get("port") or 5432
        db = params.get("database") or ""
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
