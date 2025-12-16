from typing import Dict, Any

from AnyQt import QtWidgets
from Orange.widgets.widget import Msg
from orangewidget import gui
from orangewidget.settings import Setting

from ._base_connection import BaseDBConnectionWidget


class OWMSSQLConnection(BaseDBConnectionWidget):
    name = "SQL Server"
    id = "dbconnections-mssql-connection"
    description = "Koneksi ke Microsoft SQL Server via pyodbc."
    icon = "icons/msql.png"

    DB_KIND = "SQL Server (pyodbc)"
    DEFAULT_PORT = 1433

    integrated_auth: bool = Setting(False)
    odbc_driver: str = Setting("ODBC Driver 18 for SQL Server")
    trust_server_cert: bool = Setting(True)

    class Warning(BaseDBConnectionWidget.Warning):
        mssql_odbc_missing = Msg(
            "pyodbc terpasang, tetapi ODBC driver OS untuk SQL Server tidak ditemukan. "
            "Pasang 'Microsoft ODBC Driver 18 for SQL Server' di OS Anda."
        )

    def _extra_controls(self, box: QtWidgets.QGroupBox) -> None:
        gui.checkBox(box, self, "integrated_auth", "Login dengan AD / Integrated")
        gui.checkBox(box, self, "trust_server_cert", "Trust Server Certificate")
        gui.lineEdit(box, self, "odbc_driver", label="ODBC Driver:")

    def _params(self) -> Dict[str, Any]:
        p = super()._params()
        p.update({
            "integrated_auth": bool(self.integrated_auth),
            "odbc_driver": self.odbc_driver.strip(),
            "trust_server_cert": bool(self.trust_server_cert),
        })
        return p

    def _build_url(self, params: Dict[str, Any]) -> str:
        host = params.get("host") or ""
        port = params.get("port") or 1433
        db   = params.get("database") or ""
        user = params.get("user") or ""
        pwd  = params.get("password") or ""
        integrated = params.get("integrated_auth", False)
        odbc_driver = params.get("odbc_driver", "ODBC Driver 18 for SQL Server")
        extra = f"TrustServerCertificate={'yes' if params.get('trust_server_cert', True) else 'no'}"

        if not integrated:
            return (
                "mssql+pyodbc://"
                f"{user}:{pwd}@{host}:{port}/{db}"
                f"?driver={odbc_driver.replace(' ', '+')}&{extra}"
            )

        return (
            "mssql+pyodbc://@"
            f"{host}:{port}/{db}"
            f"?driver={odbc_driver.replace(' ', '+')}&Trusted_Connection=yes&{extra}"
        )

    def _on_connected_extra(self, engine) -> None:
        # cek ODBC driver OS
        try:
            import pyodbc  # type: ignore
            drivers = {d.lower() for d in pyodbc.drivers()}
            expected = self.odbc_driver.lower()
            if not any(expected in d for d in drivers):
                self.Warning.mssql_odbc_missing()
        except Exception:
            pass
