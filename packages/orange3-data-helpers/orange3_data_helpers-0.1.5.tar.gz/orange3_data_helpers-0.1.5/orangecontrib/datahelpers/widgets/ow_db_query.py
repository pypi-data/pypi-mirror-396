# orangecontrib/datahelpers/widgets/ow_db_query.py
from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget.settings import Setting
from orangewidget import gui
from Orange.data.pandas_compat import table_from_frame
from Orange.data import Table

import pandas as pd
import sqlalchemy as sa
import time
import re
from typing import Optional, List


# ================== Regex helpers untuk deteksi SELECT ==================
# Lewati whitespace, kurung pembuka, dan komentar SQL; cek kata pertama
_SELECT_HEAD = re.compile(
    r"""^\s*(?:\(\s*)*(?:--[^\n]*\n|/\*.*?\*/\s*)*(select|with)\b""",
    re.IGNORECASE | re.DOTALL,
)

# Heuristik SELECT ... INTO <table> (anggap non-SELECT karena tidak mengembalikan resultset)
_SELECT_INTO = re.compile(
    r"""^\s*(?:\(\s*)*(?:--[^\n]*\n|/\*.*?\*/\s*)*select\b(?:(?!from\b).)*\binto\b""",
    re.IGNORECASE | re.DOTALL,
)


# ================== Worker ==================
class QueryWorker(QThread):
    # Signals
    status = pyqtSignal(str)                 # status text (small updates)
    progress_total = pyqtSignal(int)         # set total rows (for progressbar max)
    progress_value = pyqtSignal(int)         # set rows loaded so far
    finished_select = pyqtSignal(object)     # DataFrame
    finished_exec = pyqtSignal(int)          # affected rows (non-SELECT)
    failed = pyqtSignal(str)

    def __init__(
        self,
        engine: sa.Engine,
        sql: str,
        limit: Optional[int],
        chunksize: int,
        estimate_count: bool,
        parent=None
    ):
        super().__init__(parent)
        self.engine = engine
        self.sql = (sql or "").strip()
        self.limit = limit
        self.chunksize = max(1000, int(chunksize))
        self.estimate_count = bool(estimate_count)

    def _is_select_like(self, s: str) -> bool:
        return bool(_SELECT_HEAD.match(s))

    def _is_select_into(self, s: str) -> bool:
        return bool(_SELECT_INTO.match(s))

    def _strip_trailing_semicolon(self, s: str) -> str:
        return s[:-1] if s.endswith(";") else s

    def _wrap_count(self, sql: str) -> str:
        # hitung total baris untuk SELECT tanpa LIMIT (bisa mahal)
        return f"SELECT COUNT(*) AS __cnt FROM ({sql}) AS _t"

    def run(self):
        if not self.sql:
            self.failed.emit("SQL kosong.")
            return
        try:
            with self.engine.connect() as con:
                # --- Klasifikasi query ---
                q = self._strip_trailing_semicolon(self.sql)
                is_select_head = self._is_select_like(q)
                is_select_into = self._is_select_into(q)
                is_select = is_select_head and not is_select_into  # SELECT INTO diperlakukan non-SELECT

                # --- LIMIT auto (hanya untuk SELECT biasa, tidak untuk SELECT INTO) ---
                q_lower = q.lower()
                if is_select and self.limit and (" limit " not in q_lower) and (" top " not in q_lower):
                    q = f"{q}\nLIMIT {int(self.limit)}"

                if is_select:
                    # Estimasi total baris (opsional; mahal untuk query kompleks)
                    total_rows = None
                    if self.estimate_count and (" limit " not in q_lower):
                        try:
                            self.status.emit("Mengestimasi total baris… (COUNT)")
                            cnt_sql = self._wrap_count(self._strip_trailing_semicolon(self.sql))
                            r = con.execute(sa.text(cnt_sql)).fetchone()
                            total_rows = int(r[0]) if r and r[0] is not None else None
                            if total_rows is not None:
                                self.progress_total.emit(total_rows)
                        except Exception:
                            total_rows = None  # gagal estimasi → progress indeterminate

                    # Streaming fetch
                    self.status.emit("Mengambil data (streaming)…")
                    rows_loaded = 0
                    frames: List[pd.DataFrame] = []
                    start = time.time()

                    for chunk in pd.read_sql(q, con, chunksize=self.chunksize):
                        frames.append(chunk)
                        rows_loaded += len(chunk)
                        if total_rows:
                            self.progress_value.emit(min(rows_loaded, total_rows))
                        else:
                            self.progress_value.emit(rows_loaded)

                        if self.isInterruptionRequested():
                            self.failed.emit("Dibatalkan pengguna.")
                            return

                    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
                    dur = time.time() - start
                    self.status.emit(f"Selesai. {len(df)} baris dalam {dur:.2f}s")
                    self.finished_select.emit(df)

                else:
                    # Non-SELECT / DDL / SELECT INTO
                    self.status.emit("Menjalankan perintah non-SELECT…")
                    res = con.exec_driver_sql(q)
                    try:
                        rowcount = res.rowcount if res.rowcount is not None else -1
                    except Exception:
                        rowcount = -1
                    self.finished_exec.emit(rowcount)

        except Exception as e:
            self.failed.emit(str(e))


# ================== Widget ==================
class OWHDataDBQuery(OWWidget):
    name = "DB Query"
    id = "datahelpers-db-query"
    description = "Jalankan SQL terhadap koneksi dari widget DB Connection."
    icon = "icons/db_query.png"
    priority = 11
    want_main_area = True

    class Inputs:
        Connection = Input("Connection", object, auto_summary=False)

    class Outputs:
        Data = Output("Data", Table, default=True, auto_summary=False)

    # Settings
    sql_text: str = Setting("SELECT current_database() AS db, current_user AS usr")
    autorun_on_input: bool = Setting(False)
    max_rows: int = Setting(5000)          # LIMIT auto utk SELECT (best-effort)
    chunksize: int = Setting(50000)        # fetching per n rows
    estimate_count: bool = Setting(False)  # jalankan COUNT(*) untuk progress deterministik

    class Error(OWWidget.Error):
        query_error = Msg("Query gagal: {}")
        no_connection = Msg("Belum ada koneksi.")
    class Info(OWWidget.Information):
        rows = Msg("SELECT OK. Rows: {}")
        exec_ok = Msg("Perintah non-SELECT OK. Affected rows: {} (bisa -1 jika tidak diketahui)")
        conn = Msg("Terhubung: {}")
        status = Msg("{}")
    class Warning(OWWidget.Warning):
        none = Msg("")

    def __init__(self):
        super().__init__()

        # ===== Connection Info =====
        cbox = gui.widgetBox(self.controlArea, "Koneksi Aktif")
        self.lbl_conn = QtWidgets.QLabel("-")
        self.lbl_conn.setTextInteractionFlags(Qt.TextSelectableByMouse)
        cbox.layout().addWidget(self.lbl_conn)

        # ===== SQL Editor =====
        editor_box = gui.widgetBox(self.controlArea, "SQL")
        self.sql_edit = QtWidgets.QPlainTextEdit()
        self.sql_edit.setPlainText(self.sql_text or "")
        self.sql_edit.setMinimumHeight(180)
        font = self.sql_edit.font()
        font.setFamily("Monospace"); font.setStyleHint(font.TypeWriter)
        self.sql_edit.setFont(font)
        editor_box.layout().addWidget(self.sql_edit)
        self.sql_edit.textChanged.connect(self._sync_sql)

        # ===== Options =====
        opt_box = gui.widgetBox(self.controlArea, "Opsi")
        gui.checkBox(opt_box, self, "autorun_on_input", "Auto-run saat koneksi masuk/berubah")
        gui.spin(opt_box, self, "max_rows", 1, 1_000_000, step=100, label="Limit baris (SELECT):")
        gui.spin(opt_box, self, "chunksize", 1000, 5_000_000, step=10_000, label="Chunk size (stream):")
        gui.checkBox(opt_box, self, "estimate_count", "Estimasi total baris (jalankan COUNT – bisa lambat)")

        # ===== Run & Progress =====
        btn_box = gui.widgetBox(self.controlArea, orientation=Qt.Horizontal)
        self.btn_run = gui.button(btn_box, self, "Run", callback=self._run)

        pbox = gui.widgetBox(self.controlArea, "Progress")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setValue(0)
        pbox.layout().addWidget(self.progress)

        # ===== Result Preview =====
        self.result_view = QtWidgets.QTableView(self.mainArea)
        if self.mainArea.layout() is None:
            self.mainArea.setLayout(QtWidgets.QVBoxLayout())
        self.mainArea.layout().addWidget(self.result_view)

        self._engine: Optional[sa.Engine] = None
        self._worker: Optional[QueryWorker] = None

    # ===== lifecycle =====
    def onDeleteWidget(self):
        self._safe_kill_worker()
        super().onDeleteWidget()

    # ===== inputs =====
    @Inputs.Connection
    def set_engine(self, engine: Optional[object]):
        self._engine = engine if isinstance(engine, sa.Engine) else None
        self.Error.clear(); self.Info.clear(); self.Warning.clear()

        if self._engine is None:
            self.lbl_conn.setText("-")
            self.Error.no_connection()
            return

        # tampilkan info koneksi (ringan + informatif)
        try:
            url = self._engine.url
            host = getattr(url, "host", None) or "-"
            port = getattr(url, "port", None) or "-"
            dbnm = getattr(url, "database", None) or "-"
            user = getattr(url, "username", None) or "-"

            with self._engine.connect() as con:
                row = con.execute(sa.text("select current_database() as db, current_user as usr")).mappings().first()
                dbnm2 = row["db"] if row and "db" in row else dbnm
                user2 = row["usr"] if row and "usr" in row else user
                try:
                    ver = con.exec_driver_sql("select version()").scalar()
                except Exception:
                    ver = "-"

            info_text = f"Host: {host}:{port} | DB: {dbnm2} | User: {user2} | Server: {ver}"
            self.lbl_conn.setText(info_text)
            self.Info.conn(info_text)
        except Exception as e:
            self.lbl_conn.setText(f"(gagal ambil info koneksi: {e})")

        if self.autorun_on_input:
            self._run()

    # ===== helpers =====
    def _sync_sql(self):
        self.sql_text = self.sql_edit.toPlainText()

    def _toggle_busy(self, busy: bool, indeterminate: bool = False):
        self.btn_run.setDisabled(busy)
        if indeterminate:
            self.progress.setRange(0, 0)  # marquee
        else:
            self.progress.setRange(0, 100)  # default; akan diset ulang saat total diketahui

    def _safe_kill_worker(self):
        w = getattr(self, "_worker", None)
        if not w:
            return
        try:
            try: w.status.disconnect(self._on_status)
            except Exception: pass
            try: w.progress_total.disconnect(self._on_progress_total)
            except Exception: pass
            try: w.progress_value.disconnect(self._on_progress_value)
            except Exception: pass
            try: w.finished_select.disconnect(self._on_select_done)
            except Exception: pass
            try: w.finished_exec.disconnect(self._on_exec_done)
            except Exception: pass
            try: w.failed.disconnect(self._on_failed)
            except Exception: pass
            try: w.finished.disconnect(self._on_worker_finished)
            except Exception: pass
            if hasattr(w, "isRunning"):
                try:
                    if w.isRunning():
                        getattr(w, "requestInterruption", lambda: None)()
                        w.quit()
                        w.wait(2000)
                except RuntimeError:
                    pass
            try: w.setParent(None)
            except Exception: pass
            try: w.deleteLater()
            except Exception: pass
        finally:
            self._worker = None

    # ===== run =====
    def _run(self):
        self.Error.clear(); self.Info.clear(); self.Warning.clear()
        self.progress.setValue(0)

        if not self._engine:
            self.Error.no_connection()
            return
        sql = (self.sql_text or "").strip()
        if not sql:
            self.Error.query_error("SQL kosong.")
            return

        # kalau user tidak ingin estimate_count → indeterminate progress
        self._toggle_busy(True, indeterminate=(not self.estimate_count))

        self._safe_kill_worker()
        self._worker = QueryWorker(
            engine=self._engine,
            sql=sql,
            limit=self.max_rows,
            chunksize=self.chunksize,
            estimate_count=self.estimate_count,
            parent=self
        )
        # sambungkan sinyal
        self._worker.status.connect(self._on_status)
        self._worker.progress_total.connect(self._on_progress_total)
        self._worker.progress_value.connect(self._on_progress_value)
        self._worker.finished_select.connect(self._on_select_done)
        self._worker.finished_exec.connect(self._on_exec_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    # ===== callbacks =====
    def _on_worker_finished(self):
        self._toggle_busy(False)
        self._safe_kill_worker()

    def _on_status(self, text: str):
        self.Info.status(text)

    def _on_progress_total(self, total: int):
        # set progress bar determinate
        self.progress.setRange(0, max(1, int(total)))
        self.progress.setValue(0)

    def _on_progress_value(self, value: int):
        # jika determinate → value relatif ke total; jika indeterminate → ignore (UI marquee)
        if self.progress.maximum() > 0:
            self.progress.setValue(min(value, self.progress.maximum()))

    def _on_select_done(self, df: pd.DataFrame):
        # tampilkan preview & kirim output
        class _DFModel(QtCore.QAbstractTableModel):
            def __init__(self, df: pd.DataFrame, parent=None):
                super().__init__(parent); self._df = df.reset_index(drop=True)
            def rowCount(self, parent=QtCore.QModelIndex()): return 0 if parent.isValid() else len(self._df)
            def columnCount(self, parent=QtCore.QModelIndex()): return 0 if parent.isValid() else len(self._df.columns)
            def data(self, idx, role=QtCore.Qt.DisplayRole):
                if not idx.isValid() or role not in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole): return None
                val = self._df.iat[idx.row(), idx.column()]
                return "" if pd.isna(val) else str(val)
            def headerData(self, sec, ori, role=QtCore.Qt.DisplayRole):
                if role != QtCore.Qt.DisplayRole: return None
                return str(self._df.columns[sec]) if ori == QtCore.Qt.Horizontal else str(sec+1)

        self.result_view.setModel(_DFModel(df))
        self.Outputs.Data.send(table_from_frame(df))
        self.Info.rows(len(df))

    def _on_exec_done(self, rowcount: int):
        # tampil selesai untuk non-SELECT
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.result_view.setModel(None)
        self.Outputs.Data.send(None)
        self.Info.exec_ok(rowcount)

    def _on_failed(self, err: str):
        self.result_view.setModel(None)
        self.Outputs.Data.send(None)
        self.Error.query_error(err)
