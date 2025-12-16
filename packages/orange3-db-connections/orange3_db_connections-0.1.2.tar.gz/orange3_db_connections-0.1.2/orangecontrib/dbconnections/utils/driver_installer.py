from importlib import import_module
from typing import Tuple, Dict, Any


def _check_module(modname: str) -> Tuple[bool, str]:
    try:
        import_module(modname)
        return True, f"Module {modname} tersedia."
    except Exception as e:
        return False, f"Module {modname} belum terpasang: {e}"


def ensure_driver(kind: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Pastikan driver Python untuk DB terkait sudah tersedia.

    Parameters
    ----------
    kind:
        Nama jenis DB, misal: "PostgreSQL", "MySQL", "SQLite",
        "SQL Server", "ClickHouse", "Oracle".

    Returns
    -------
    ok, log, extra
    """
    k = kind.lower()

    if "postgres" in k:
        return (*_check_module("psycopg2"), {})

    if "mysql" in k:
        return (*_check_module("pymysql"), {})

    if "sqlite" in k:
        return True, "SQLite builtin di Python.", {}

    if "sql server" in k or "mssql" in k or "pyodbc" in k:
        return (*_check_module("pyodbc"), {})

    if "clickhouse" in k:
        return (*_check_module("clickhouse_connect"), {})

    if "oracle" in k:
        return (*_check_module("cx_Oracle"), {})

    return False, f"Jenis DB tidak dikenali: {kind}", {}
