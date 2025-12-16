# orangecontrib/datahelpers/widgets/ow_query_loader.py

from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget.settings import Setting
from orangewidget import gui
from Orange.data.pandas_compat import table_from_frame
from Orange.data import Table


import pandas as pd
import sqlalchemy as sa
from typing import Optional, List, Dict, Any, Tuple
import os
import re

try:
    import yaml
except Exception:      # pragma: no cover
    yaml = None


# ========= Helper: model sederhana utk preview DataFrame =========
def df_to_qt_model(df: pd.DataFrame) -> QtCore.QAbstractTableModel:
    class _DFModel(QtCore.QAbstractTableModel):
        def __init__(self, df_: pd.DataFrame, parent=None):
            super().__init__(parent)
            self._df = df_.reset_index(drop=True)

        def rowCount(self, parent=QtCore.QModelIndex()):
            return 0 if parent.isValid() else len(self._df)

        def columnCount(self, parent=QtCore.QModelIndex()):
            return 0 if parent.isValid() else len(self._df.columns)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
                return None
            val = self._df.iat[index.row(), index.column()]
            return "" if pd.isna(val) else str(val)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                try:
                    return str(self._df.columns[section])
                except Exception:
                    return str(section)
            else:
                return str(section + 1)

    return _DFModel(df)


# ========= Struktur data query yang sudah di-load =========
class LoadedQuery:
    def __init__(
        self,
        name: str,
        sql: str,
        source_path: Optional[str] = None,
        description: str = "",
    ):
        self.name = name
        self.sql = sql
        self.source_path = source_path or ""
        self.description = description or ""
        self.status: str = "Ready"  # Ready / Running / OK / Error
        self.error: str = ""
        self.rows: int = 0
        self.df: Optional[pd.DataFrame] = None
        self.table: Optional[Table] = None 



# ========= Worker batch query =========
class BatchQueryWorker(QThread):
    status = pyqtSignal(str)                    # status text global
    query_started = pyqtSignal(int, str)        # idx, name
    query_done = pyqtSignal(int, object, int)   # idx, DataFrame, rows
    query_failed = pyqtSignal(int, str)         # idx, error
    progress = pyqtSignal(int, int)             # done, total

    def __init__(
        self,
        engine: sa.Engine,
        queries: List[Tuple[int, str, str]],  # (idx, name, sql)
        max_rows: Optional[int],
        parent=None,
    ):
        super().__init__(parent)
        self.engine = engine
        self.queries = queries
        self.max_rows = int(max_rows) if max_rows and max_rows > 0 else None

    def _prepare_sql(self, sql: str) -> str:
        s = sql.strip()
        if s.endswith(";"):
            s = s[:-1]
        if not self.max_rows:
            return s

        # heuristik sederhana: kalau belum ada LIMIT/TOP → tambahkan LIMIT
        lower = s.lower()
        if " limit " in lower or " top " in lower:
            return s

        # jangan terlalu canggih; cukup append LIMIT
        return f"{s}\nLIMIT {self.max_rows}"

    def run(self):
        total = len(self.queries)
        done = 0
        self.progress.emit(done, total)
        try:
            with self.engine.connect() as con:
                for idx, name, sql in self.queries:
                    if self.isInterruptionRequested():
                        self.status.emit("Dibatalkan oleh pengguna.")
                        return
                    self.query_started.emit(idx, name)
                    try:
                        q = self._prepare_sql(sql)
                        df = pd.read_sql(q, con)
                        rows = len(df)
                        self.query_done.emit(idx, df, rows)
                    except Exception as e:
                        self.query_failed.emit(idx, str(e))
                    done += 1
                    self.progress.emit(done, total)
        except Exception as e:
            # error besar di luar loop
            self.status.emit(f"Gagal menjalankan batch: {e}")


# ========= Widget utama =========
class OWHDataQueryLoader(OWWidget):
    name = "Query Loader"
    id = "datahelpers-query-loader"
    description = (
        "Memuat banyak query dari file .sql / .yml dan menjalankannya sebagai batch. "
        "Setiap hasil bisa dikirim ke Data Table."
    )
    icon = "icons/query_loader.png"
    priority = 12
    want_main_area = True

    class Inputs:
        Connection = Input("Connection", object, auto_summary=False)

    class Outputs:
        Data = Output("Data", Table, auto_summary=False)
        Results = Output("Results", object, auto_summary=False)  # <--- baru


    # Settings
    last_dir: str = Setting("")          # folder terakhir dipakai
    max_rows: int = Setting(5000)        # LIMIT otomatis
    autorun_on_load: bool = Setting(False)

    class Error(OWWidget.Error):
        no_connection = Msg("Belum ada koneksi.")
        load_failed = Msg("Gagal memuat file: {}")
        yaml_missing = Msg("PyYAML belum terpasang. Install 'PyYAML' untuk membaca .yml.")
        run_error = Msg("Batch gagal: {}")
    class Info(OWWidget.Information):
        conn = Msg("Terhubung ke database.")
        status = Msg("{}")
        loaded = Msg("Query ter-load: {} file, {} query.")
        query_status = Msg("Hasil: {} ({} baris).")
    class Warning(OWWidget.Warning):
        none = Msg("")

    def __init__(self):
        super().__init__()

        # ========= Control area =========
        # --- Info Koneksi ---
        cbox = gui.widgetBox(self.controlArea, "Koneksi")
        self.lbl_conn = QtWidgets.QLabel("-")
        self.lbl_conn.setTextInteractionFlags(Qt.TextSelectableByMouse)
        cbox.layout().addWidget(self.lbl_conn)

        # --- Sumber file ---
        fbox = gui.widgetBox(self.controlArea, "Sumber Query (.sql / .yml)")
        self.btn_load_files = gui.button(
            fbox, self, "Pilih File…", callback=self._choose_files
        )
        self.btn_load_dir = gui.button(
            fbox, self, "Pilih Folder…", callback=self._choose_dir
        )

        self.lbl_source = QtWidgets.QLabel("Belum ada file.")
        self.lbl_source.setWordWrap(True)
        fbox.layout().addWidget(self.lbl_source)

        # --- Opsi eksekusi ---
        obox = gui.widgetBox(self.controlArea, "Opsi Eksekusi")
        gui.spin(
            obox, self, "max_rows",
            1, 1_000_000, step=100, label="Limit baris per query:"
        )
        gui.checkBox(
            obox, self, "autorun_on_load",
            "Auto-run semua query setelah load"
        )

        # --- Daftar Query ---
        qbox = gui.widgetBox(self.controlArea, "Daftar Query")
        self.list_queries = QtWidgets.QListWidget()
        self.list_queries.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_queries.itemSelectionChanged.connect(self._on_query_selected)
        qbox.layout().addWidget(self.list_queries)

        btns = gui.widgetBox(qbox, orientation=Qt.Horizontal)
        self.btn_run_all = gui.button(btns, self, "Run All", callback=self._run_all)
        self.btn_run_sel = gui.button(btns, self, "Run Selected", callback=self._run_selected)

        # --- Progress ---
        pbox = gui.widgetBox(self.controlArea, "Progress")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        pbox.layout().addWidget(self.progress)

        # ========= Main area: preview hasil =========
        self.view_result = QtWidgets.QTableView(self.mainArea)
        if self.mainArea.layout() is None:
            self.mainArea.setLayout(QtWidgets.QVBoxLayout())
        self.mainArea.layout().addWidget(self.view_result)

        # state
        self._engine: Optional[sa.Engine] = None
        self._queries: List[LoadedQuery] = []
        self._worker: Optional[BatchQueryWorker] = None
        
            # ===== helper: kirim paket semua hasil ke output Results =====
    def _send_results_payload(self):
        items = []
        for idx, q in enumerate(self._queries):
            if q.table is not None:
                items.append({
                    "index": idx,
                    "name": q.name,
                    "rows": q.rows,
                    "table": q.table,
                    "description": q.description,
                    "source": q.source_path,
                    "status": q.status,
                    "error": q.error,
                })
        self.Outputs.Results.send(items if items else None)


    # ===== lifecycle =====
    def onDeleteWidget(self):
        self._safe_kill_worker()
        super().onDeleteWidget()

    # ===== input koneksi =====
    @Inputs.Connection
    def set_engine(self, engine: Optional[object]):
        self._engine = engine if isinstance(engine, sa.Engine) else None
        self.Error.clear(); self.Info.clear(); self.Warning.clear()

        if not self._engine:
            self.lbl_conn.setText("-")
            self.Error.no_connection()
            return

        try:
            url = self._engine.url
            host = getattr(url, "host", None) or "-"
            port = getattr(url, "port", None) or "-"
            dbnm = getattr(url, "database", None) or "-"
            info = f"{url.get_backend_name()} | {host}:{port} | DB: {dbnm}"
            self.lbl_conn.setText(info)
            self.Info.conn(info)
        except Exception:
            self.lbl_conn.setText("(koneksi aktif)")
            self.Info.conn("Koneksi aktif.")

    # ===== helper: manage worker =====
    def _safe_kill_worker(self):
        w = getattr(self, "_worker", None)
        if not w:
            return
        try:
            try: w.status.disconnect(self._on_worker_status)
            except Exception: pass
            try: w.query_started.disconnect(self._on_query_started)
            except Exception: pass
            try: w.query_done.disconnect(self._on_query_done)
            except Exception: pass
            try: w.query_failed.disconnect(self._on_query_failed)
            except Exception: pass
            try: w.progress.disconnect(self._on_worker_progress)
            except Exception: pass
        finally:
            try:
                if w.isRunning():
                    w.requestInterruption()
                    w.quit()
                    w.wait(2000)
            except Exception:
                pass
            try: w.setParent(None)
            except Exception: pass
            try: w.deleteLater()
            except Exception: pass
            self._worker = None

    def _toggle_busy(self, busy: bool):
        self.btn_run_all.setDisabled(busy)
        self.btn_run_sel.setDisabled(busy)
        self.btn_load_files.setDisabled(busy)
        self.btn_load_dir.setDisabled(busy)

    # ===== loading file / folder =====
    def _choose_files(self):
        dlg_dir = self.last_dir or os.getcwd()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Pilih file .sql / .yml",
            dlg_dir,
            "SQL/YAML Files (*.sql *.SQL *.yml *.yaml);;All Files (*)",
        )
        if not files:
            return
        self.last_dir = os.path.dirname(files[0])
        self._load_from_paths(files)

    def _choose_dir(self):
        dlg_dir = self.last_dir or os.getcwd()
        dirname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Pilih folder yang berisi .sql / .yml",
            dlg_dir
        )
        if not dirname:
            return
        self.last_dir = dirname
        # scan folder (non-recursive dulu; bisa dibuat recursive kalau mau)
        paths: List[str] = []
        for fn in os.listdir(dirname):
            full = os.path.join(dirname, fn)
            if not os.path.isfile(full):
                continue
            if fn.lower().endswith((".sql", ".yml", ".yaml")):
                paths.append(full)
        self._load_from_paths(paths)

    def _load_from_paths(self, paths: List[str]):
        self.Error.clear(); self.Info.clear(); self.Warning.clear()
        self._queries.clear()
        self.list_queries.clear()
        self.view_result.setModel(None)
        self.Outputs.Data.send(None)
        self.Outputs.Results.send(None)
        self.progress.setValue(0)

        if not paths:
            self.lbl_source.setText("Tidak ada file yang cocok.")
            return

        total_files = len(paths)
        total_queries = 0

        for p in paths:
            try:
                qlist = self._load_queries_from_file(p)
            except Exception as e:
                self.Error.load_failed(f"{os.path.basename(p)}: {e}")
                continue
            self._queries.extend(qlist)
            total_queries += len(qlist)

        self._refresh_query_list()

        src_text = f"{total_files} file, {total_queries} query."
        self.lbl_source.setText(src_text)
        self.Info.loaded(len(paths), total_queries)

        if self.autorun_on_load and self._queries and self._engine:
            self._run_all()

    def _load_queries_from_file(self, path: str) -> List[LoadedQuery]:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".sql":
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            name = os.path.basename(path)
            return [LoadedQuery(name=name, sql=sql, source_path=path)]

        if ext in (".yml", ".yaml"):
            if yaml is None:
                self.Error.yaml_missing()
                raise RuntimeError("PyYAML tidak tersedia.")
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            queries: List[LoadedQuery] = []

            # bentuk: {name: ..., sql: ..., description: ...}
            def _add_entry(entry: Dict[str, Any]):
                sql = entry.get("sql") or entry.get("query") or ""
                name = entry.get("name") or os.path.basename(path)
                desc = entry.get("description") or ""
                if not str(sql).strip():
                    return
                queries.append(
                    LoadedQuery(
                        name=name,
                        sql=str(sql),
                        source_path=path,
                        description=str(desc),
                    )
                )

            if isinstance(data, dict) and ("sql" in data or "query" in data):
                _add_entry(data)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        _add_entry(item)
            else:
                raise ValueError("Struktur YAML tidak dikenali. Harus mapping {name, sql} atau list of mapping.")

            return queries

        raise ValueError(f"Ekstensi file tidak didukung: {ext}")

    # ===== list query UI =====
    def _refresh_query_list(self):
        self.list_queries.clear()
        for q in self._queries:
            text = f"{q.name}  —  [{q.status}]"
            item = QtWidgets.QListWidgetItem(text)
            item.setToolTip((q.description or "") + (f"\n{q.source_path}" if q.source_path else ""))
            self.list_queries.addItem(item)

    def _update_query_item(self, idx: int):
        if idx < 0 or idx >= len(self._queries):
            return
        q = self._queries[idx]
        item = self.list_queries.item(idx)
        if not item:
            return
        text = f"{q.name}  —  [{q.status}]"
        if q.rows:
            text += f" ({q.rows} rows)"
        item.setText(text)
        tip = (q.description or "") + (f"\n{q.source_path}" if q.source_path else "")
        if q.error:
            tip += f"\nERROR: {q.error}"
        item.setToolTip(tip)

    def _on_query_selected(self):
        idx = self.list_queries.currentRow()
        if idx < 0 or idx >= len(self._queries):
            return
        q = self._queries[idx]
        if q.table is not None:
            self.view_result.setModel(df_to_qt_model(q.df))
            self.Outputs.Data.send(q.table)
            self.Info.query_status(q.name, q.rows)


    # ===== eksekusi batch =====
    def _run_all(self):
        if not self._engine:
            self.Error.no_connection()
            return
        if not self._queries:
            self.Info.status("Tidak ada query untuk dijalankan.")
            return
        self._start_worker(range(len(self._queries)))

    def _run_selected(self):
        if not self._engine:
            self.Error.no_connection()
            return
        idx = self.list_queries.currentRow()
        if idx < 0 or idx >= len(self._queries):
            self.Info.status("Pilih query terlebih dahulu.")
            return
        self._start_worker([idx])

    def _start_worker(self, indices):
        self.Error.clear(); self.Info.status("Menjalankan query…"); self.Warning.clear()
        self._safe_kill_worker()
        self._toggle_busy(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        # reset status untuk query yang akan dijalankan
        for i in indices:
            q = self._queries[i]
            q.status = "Ready"
            q.error = ""
            if len(indices) == 1:
                # untuk one-off, kita boleh clear hasil lama
                q.df = None
                q.rows = 0
            self._update_query_item(i)

        qlist: List[Tuple[int, str, str]] = [
            (i, self._queries[i].name, self._queries[i].sql) for i in indices
        ]

        self._worker = BatchQueryWorker(
            engine=self._engine,
            queries=qlist,
            max_rows=self.max_rows,
            parent=self,
        )
        self._worker.status.connect(self._on_worker_status)
        self._worker.query_started.connect(self._on_query_started)
        self._worker.query_done.connect(self._on_query_done)
        self._worker.query_failed.connect(self._on_query_failed)
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    # ===== callbacks worker =====
    def _on_worker_status(self, text: str):
        self.Info.status(text)

    def _on_worker_progress(self, done: int, total: int):
        if total <= 0:
            self.progress.setRange(0, 0)
            return
        self.progress.setRange(0, total)
        self.progress.setValue(done)

    def _on_query_started(self, idx: int, name: str):
        q = self._queries[idx]
        q.status = "Running"
        self._update_query_item(idx)

    def _on_query_done(self, idx: int, df: pd.DataFrame, rows: int):
        q = self._queries[idx]
        q.status = "OK"
        q.df = df
        q.rows = rows
        q.table = table_from_frame(df)    # <--- convert sekali saja
        self._update_query_item(idx)

        # kalau hanya satu query yang dijalankan, langsung tampilkan
        if self._worker and len(self._worker.queries) == 1:
            self.list_queries.setCurrentRow(idx)
            self.view_result.setModel(df_to_qt_model(df))
            self.Outputs.Data.send(table_from_frame(df))
            # kirim 2 argumen, sesuai Msg("Hasil: {} ({} baris).")
            self.Info.query_status(q.name, rows)
        
        self._send_results_payload()



    def _on_query_failed(self, idx: int, err: str):
        q = self._queries[idx]
        q.status = "Error"
        q.error = err
        self._update_query_item(idx)
        self._send_results_payload()


    def _on_worker_finished(self):
        self._toggle_busy(False)
        self._safe_kill_worker()
        self.Info.status("Batch selesai.")
