from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Output, Msg
from orangewidget.settings import Setting
from orangewidget import gui

import sqlalchemy as sa
from typing import Dict, Any, Optional, Callable


class ConnectWorker(QThread):
    finished_ok = pyqtSignal(object)   # engine
    failed = pyqtSignal(str)

    def __init__(
        self,
        driver_kind: str,
        params: Dict[str, Any],
        build_url: Callable[[Dict[str, Any]], str],
        parent=None,
    ):
        super().__init__(parent)
        from orangecontrib.dbconnections.utils import ensure_driver

        self.driver_kind = driver_kind
        self.params = params
        self.build_url = build_url
        self._ensure_driver = ensure_driver

    def run(self):
        ok, log, _ = self._ensure_driver(self.driver_kind)
        if not ok:
            self.failed.emit(
                f"Driver Python belum tersedia untuk {self.driver_kind}.\n{log}\n"
                "Catatan: beberapa DB juga butuh ODBC/Client di OS."
            )
            return

        try:
            url = self.build_url(self.params)
            engine = sa.create_engine(url, pool_pre_ping=True)

            with engine.connect() as con:
                # pilih test query sesuai dialect
                try:
                    dname = engine.dialect.name.lower()
                except Exception:
                    dname = ""

                test_sql = "SELECT 1"
                if "oracle" in dname:
                    test_sql = "SELECT 1 FROM DUAL"

                con.exec_driver_sql(test_sql)

            self.finished_ok.emit(engine)
        except Exception as e:
            self.failed.emit(str(e))

class BaseDBConnectionWidget(OWWidget, openclass=True):
    """Base class untuk semua widget koneksi database.

    Subclass wajib set:
      - DB_KIND
      - DEFAULT_PORT
      - name, id, description, icon
      - override :meth:`_build_url`
      - optional override :meth:`_extra_controls`, :meth:`_on_connected_extra`
    """

    DB_KIND: str = "Generic DB"
    DEFAULT_PORT: int = 0

    icon = "icons/db_connection.svg"
    priority = 10
    want_main_area = False

    class Outputs:
        Connection = Output("Connection", object, auto_summary=False)

    # settings umum
    host: str = Setting("localhost")
    port: int = Setting(0)
    database: str = Setting("")
    user: str = Setting("")
    remember_password: bool = Setting(False)

    _password_mem: str = ""  # tidak disimpan sebagai Setting

    class Error(OWWidget.Error):
        connect_error = Msg("Gagal konek: {}")

    class Info(OWWidget.Information):
        connected = Msg("Terkoneksi ke database.")
        hint = Msg("Password tidak disimpan kecuali centang Remember.")

    class Warning(OWWidget.Warning):
        generic_warn = Msg("{}")

    def __init__(self):
        super().__init__()

        # --- form umum ---
        box = gui.widgetBox(self.controlArea, "Koneksi")

        gui.lineEdit(box, self, "host", label="Host:")
        gui.spin(box, self, "port", 0, 65535, label="Port:", step=1)
        gui.lineEdit(box, self, "database", label="Database/Schema/Path:")
        gui.lineEdit(box, self, "user", label="Username:")
        gui.lineEdit(
            box, self, "_password_mem",
            label="Password:",
            echoMode=QtWidgets.QLineEdit.Password,
        )
        gui.checkBox(box, self, "remember_password", "Remember password (plaintext)")

        # area ekstra untuk subclass
        self._extra_controls(box)

        btns = gui.widgetBox(box, orientation=QtCore.Qt.Horizontal)
        self.btn_connect = gui.button(btns, self, "Connect", callback=self._connect)

        self.Info.hint()
        self._worker: Optional[ConnectWorker] = None

        if not self.port:
            self._apply_default_port()

    # ===== hooks untuk subclass =====
    def _extra_controls(self, box: QtWidgets.QGroupBox) -> None:
        """Override di subclass kalau butuh field tambahan."""
        return None

    def _apply_default_port(self):
        self.port = getattr(self, "DEFAULT_PORT", 0)

    def _params(self) -> Dict[str, Any]:
        return {
            "host": self.host.strip(),
            "port": int(self.port),
            "database": self.database.strip(),
            "user": self.user.strip(),
            "password": self._password_mem or "",
        }

    def _build_url(self, params: Dict[str, Any]) -> str:
        """Override di subclass, return SQLAlchemy URL."""
        raise NotImplementedError

    def _driver_kind(self) -> str:
        return getattr(self, "DB_KIND", "Generic DB")

    # ===== lifecycle =====
    def onDeleteWidget(self):
        self._safe_kill_worker()
        super().onDeleteWidget()

    # ===== worker handling =====
    def _toggle_busy(self, busy: bool):
        self.btn_connect.setDisabled(busy)

    def _safe_kill_worker(self):
        w = getattr(self, "_worker", None)
        if not w:
            return
        try:
            try:
                w.finished_ok.disconnect(self._on_connected)
            except Exception:
                pass
            try:
                w.failed.disconnect(self._on_failed)
            except Exception:
                pass
            try:
                w.finished.disconnect(self._on_worker_finished)
            except Exception:
                pass

            if hasattr(w, "isRunning"):
                try:
                    if w.isRunning():
                        getattr(w, "requestInterruption", lambda: None)()
                        w.quit()
                        w.wait(2000)
                except RuntimeError:
                    pass

            try:
                w.setParent(None)
            except Exception:
                pass
            try:
                w.deleteLater()
            except Exception:
                pass
        finally:
            self._worker = None

    # ===== actions =====
    def _connect(self):
        self._safe_kill_worker()
        self.Error.clear()
        self.Info.clear()
        self.Warning.clear()
        self._toggle_busy(True)

        params = self._params()
        self._worker = ConnectWorker(
            driver_kind=self._driver_kind(),
            params=params,
            build_url=self._build_url,
            parent=self,
        )
        self._worker.finished_ok.connect(self._on_connected)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_finished(self):
        self._toggle_busy(False)
        self._safe_kill_worker()

    def _on_connected_extra(self, engine) -> None:
        """Subclass boleh override untuk cek tambahan setelah connect."""
        return None

    def _on_connected(self, engine):
        self._on_connected_extra(engine)

        if not self.remember_password:
            self._password_mem = ""

        self.Info.connected()
        self.Outputs.Connection.send(engine)

    def _on_failed(self, err: str):
        self.Outputs.Connection.send(None)
        self.Error.connect_error(err)
