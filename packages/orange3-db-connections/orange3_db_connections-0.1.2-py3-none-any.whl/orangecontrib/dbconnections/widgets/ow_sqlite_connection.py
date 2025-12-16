from typing import Dict, Any
from AnyQt import QtWidgets
from orangewidget import gui

from ._base_connection import BaseDBConnectionWidget


class OWSQLiteConnection(BaseDBConnectionWidget):
    name = "SQLite"
    id = "dbconnections-sqlite-connection"
    description = "Koneksi ke SQLite file / :memory:."
    icon = "icons/sqlite.png"

    DB_KIND = "SQLite"
    DEFAULT_PORT = 0  # tidak dipakai

    def _extra_controls(self, box: QtWidgets.QGroupBox) -> None:
        gui.widgetLabel(
            box,
            "Isikan 'Database/Schema/Path' dengan path file SQLite atau ':memory:'."
        )

    def _params(self) -> Dict[str, Any]:
        return {
            "database": self.database.strip() or ":memory:",
            "user": "",
            "password": self._password_mem or "",
            "host": "",
            "port": 0,
        }

    def _build_url(self, params: Dict[str, Any]) -> str:
        db = (params.get("database") or "").strip()
        if db == ":memory:":
            return "sqlite:///:memory:"
        return f"sqlite:///{db}"
