from typing import Dict, Any
from ._base_connection import BaseDBConnectionWidget


class OWMySQLConnection(BaseDBConnectionWidget):
    name = "MySQL"
    id = "dbconnections-mysql-connection"
    description = "Koneksi ke MySQL/MariaDB via PyMySQL."
    icon = "icons/mysql.png"

    DB_KIND = "MySQL"
    DEFAULT_PORT = 3306

    def _build_url(self, params: Dict[str, Any]) -> str:
        user = params.get("user") or ""
        pwd = params.get("password") or ""
        host = params.get("host") or ""
        port = params.get("port") or 3306
        db = params.get("database") or ""
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"
