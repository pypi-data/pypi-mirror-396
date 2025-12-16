import sys
import platform
from importlib import import_module

from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
)

from Orange.widgets.widget import OWWidget


# Daftar “tipe koneksi” yang ada di add-on DB Connections
# Fokus: modul Python & catatan OS/driver
CONNECTION_SPECS = [
    {
        "id": "mssql",
        "label": "SQL Server (pyodbc + ODBC)",
        "module": "pyodbc",
        "pip": "pyodbc",
        "note": "Butuh ODBC Driver 17/18 for SQL Server di Windows.",
    },
    {
        "id": "postgresql",
        "label": "PostgreSQL (psycopg2-binary)",
        "module": "psycopg2",
        "pip": "psycopg2-binary",
        "note": "Driver pure Python, tidak perlu client tambahan.",
    },
    {
        "id": "mysql",
        "label": "MySQL (pymysql)",
        "module": "pymysql",
        "pip": "pymysql",
        "note": "Driver pure Python, tidak perlu client tambahan.",
    },
    {
        "id": "sqlite",
        "label": "SQLite (builtin sqlite3)",
        "module": "sqlite3",
        "pip": None,
        "note": "Sudah bawaan Python, seharusnya selalu tersedia.",
    },
    {
        "id": "clickhouse",
        "label": "ClickHouse (clickhouse-connect)",
        "module": "clickhouse_connect",
        "pip": "clickhouse-connect",
        "note": "Tidak perlu client tambahan.",
    },
    {
        "id": "oracle",
        "label": "Oracle (cx-Oracle)",
        "module": "cx_Oracle",
        "pip": "cx-Oracle",
        "note": "Butuh Oracle Instant Client + konfigurasi PATH/ORACLE_HOME.",
    },
]


def _check_module(mod_name: str):
    """
    Coba import modul. Return (status, detail).
    status: 'OK' | 'Missing'
    """
    try:
        mod = import_module(mod_name)
        version = getattr(mod, "__version__", "?")
        return "OK", f"Terpasang (versi {version})"
    except Exception as e:
        return "Missing", f"Tidak ditemukan: {e.__class__.__name__}: {e}"


def _check_odbc():
    """
    Cek daftar ODBC driver (kalau pyodbc tersedia).
    """
    try:
        import pyodbc
    except ImportError:
        return "Missing", "pyodbc belum terpasang, tidak bisa cek ODBC driver.", []

    drivers = list(pyodbc.drivers())
    if not drivers:
        return (
            "Warning",
            "pyodbc ada, tapi tidak ada ODBC driver terdeteksi. "
            "Pastikan ODBC Driver 17 atau 18 for SQL Server sudah terinstal.",
            [],
        )

    return "OK", f"Ditemukan {len(drivers)} driver ODBC.", drivers


class OWDbEnvCheck(OWWidget):
    """
    Widget khusus DB Connections:
    - Menampilkan info Python/OS yang dipakai Orange
    - Mengecek modul driver DB (pyodbc, psycopg2, dll.)
    - Mengecek ODBC driver (kalau pyodbc tersedia)
    """

    name = "Env Check"
    description = "Cek environment untuk koneksi database (driver Python & ODBC)."
    icon = "icons/db_env_check.svg"  # ganti sementara ke icon yang ada kalau perlu
    priority = 100  # supaya muncul agak ke kanan di palette

    want_main_area = True
    want_control_area = False

    def __init__(self):
        super().__init__()

        # ---- Widgets UI ----
        self.btn_scan = QPushButton("🔍 Scan DB Environment")
        self.btn_scan.clicked.connect(self.scan_environment)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Connection", "Python Module", "Status", "Detail", "Cara Perbaikan"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(240)

        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setMinimumHeight(160)

        main = QVBoxLayout()
        main.addWidget(
            QLabel(
                "<b>Bidics DB Connections – Environment Check</b><br/>"
                "Scan modul Python & driver ODBC yang dibutuhkan oleh widget koneksi database."
            )
        )
        main.addWidget(self.btn_scan)
        main.addWidget(self.table)
        main.addWidget(QLabel("<b>Ringkasan</b>"))
        main.addWidget(self.txt_summary)

        w = QWidget()
        w.setLayout(main)
        self.mainArea.layout().addWidget(w)

    # --------------------------------------------------
    # HELPER
    # --------------------------------------------------
    def _build_fix_command(self, pip_name: str | None) -> str:
        """
        Perintah yang disarankan untuk memperbaiki.
        pip_name bisa None (untuk modul builtin seperti sqlite3).
        """
        python_exe = sys.executable
        if pip_name:
            return f'"{python_exe}" -m pip install {pip_name}'
        return "(builtin; kalau error, cek instalasi Python/Orange)."

    # --------------------------------------------------
    # MAIN ACTION
    # --------------------------------------------------
    def scan_environment(self):
        """
        Scan lengkap dan isi tabel + summary.
        """
        self.table.setRowCount(0)

        # Info Python & OS
        py_info_lines = [
            f"Python Executable : {sys.executable}",
            f"Python Version    : {sys.version.split()[0]}",
            f"Platform          : {platform.platform()}",
            f"Arch              : {platform.architecture()[0]}",
            "",
            "=== Status Driver Python ===",
        ]

        # Cek modul untuk tiap jenis koneksi
        rows = []
        for spec in CONNECTION_SPECS:
            status, detail = _check_module(spec["module"])
            fix_cmd = self._build_fix_command(spec["pip"])
            rows.append(
                (
                    spec["label"],
                    spec["module"],
                    status,
                    detail,
                    fix_cmd,
                )
            )
            py_info_lines.append(f"- {spec['label']}: {status} ({detail})")

        # Tambah info ODBC (khusus SQL Server)
        py_info_lines.append("")
        py_info_lines.append("=== Status ODBC (SQL Server) ===")
        odbc_status, odbc_detail, odbc_drivers = _check_odbc()
        py_info_lines.append(f"ODBC Drivers: {odbc_status} ({odbc_detail})")
        if odbc_drivers:
            py_info_lines.append("Daftar driver:")
            for drv in odbc_drivers:
                py_info_lines.append(f"  - {drv}")

        # Isi tabel
        for row_data in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                if c == 2:  # kolom Status
                    if value == "Missing":
                        item.setForeground(Qt.red)
                    elif value == "Warning":
                        item.setForeground(Qt.darkYellow)
                self.table.setItem(r, c, item)

        self.txt_summary.setText("\n".join(py_info_lines))
