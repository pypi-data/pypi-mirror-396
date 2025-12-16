# orangecontrib/datahelpers/widgets/ow_query_table.py
from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal

from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget import gui
from orangewidget.settings import Setting

import pandas as pd
import sqlalchemy as sa
from typing import Optional, List, Tuple

from Orange.data.pandas_compat import table_from_frame
from Orange.data import Table


# =============== Utils ===============
def _dialect_name(engine: sa.Engine) -> str:
    try:
        return engine.url.get_backend_name()
    except Exception:
        return getattr(engine.dialect, "name", "unknown")


def _quote_fq(engine: sa.Engine, schema: Optional[str], table: str) -> str:
    """Fully-qualified name with proper quoting untuk schema.table."""
    prep = engine.dialect.identifier_preparer
    if schema and str(schema).strip():
        return f"{prep.quote_schema(schema)}.{prep.quote(table)}"
    return prep.quote(table)


# =============== Worker ===============
class LoadTableWorker(QThread):
    status = pyqtSignal(str)
    row_count = pyqtSignal(object)      # int atau None
    finished_df = pyqtSignal(object)    # pandas.DataFrame
    failed = pyqtSignal(str)

    def __init__(self, engine: sa.Engine, schema: Optional[str],
                 table: str, warn_threshold: int, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.schema = schema or ""
        self.table = table
        self.warn_threshold = max(0, int(warn_threshold))

    def _read_df(self, con, sql: str) -> pd.DataFrame:
        res = con.execute(sa.text(sql))
        rows = res.mappings().all()
        return pd.DataFrame(rows)

    def run(self):
        try:
            with self.engine.connect() as con:
                fq = _quote_fq(self.engine, self.schema, self.table)
                d = _dialect_name(self.engine)

                # --- Hitung jumlah baris dulu (kalau bisa) ---
                n_rows = None
                try:
                    self.status.emit("Menghitung jumlah baris …")
                    cnt_sql = f"SELECT COUNT(*) AS n FROM {fq}"
                    n_rows = con.execute(sa.text(cnt_sql)).scalar()
                    if n_rows is not None:
                        n_rows = int(n_rows)
                except Exception:
                    # Kalau gagal, lanjut saja tanpa info jumlah baris
                    n_rows = None
                self.row_count.emit(n_rows)

                # --- Load semua data (tanpa LIMIT) ---
                if n_rows is not None:
                    self.status.emit(f"Memuat semua baris (≈{n_rows} rows) …")
                else:
                    self.status.emit("Memuat semua baris …")

                # Tidak ada LIMIT di sini: sengaja full table
                sql = f"SELECT * FROM {fq}"
                df = self._read_df(con, sql)
                self.finished_df.emit(df)
        except Exception as e:
            self.failed.emit(str(e))


# =============== Widget ===============
class OWHQueryDataTable(OWWidget):
    name = "Query Data Table"
    id = "datahelpers-query-table"
    description = "Ambil seluruh isi tabel database sebagai Orange Table."
    icon = "icons/query_table.svg"
    priority = 14
    want_main_area = True

    class Inputs:
        Connection = Input("Connection", object, auto_summary=False)

    class Outputs:
        Data = Output("Data", Table, default=True)

    # Settings
    include_system: bool = Setting(False)
    last_selected: str = Setting("")  # schema.table
    filter_text: str = Setting("")
    autorun_on_select: bool = Setting(True)
    warn_threshold: int = Setting(1_000_000)  # warn jika > N baris

    class Error(OWWidget.Error):
        no_connection = Msg("Belum ada koneksi.")
        load_failed = Msg("Gagal memuat data: {}")

    class Info(OWWidget.Information):
        status = Msg("{}")
        table = Msg("Tabel: {}")

    class Warning(OWWidget.Warning):
        large_table = Msg(
            "Tabel besar (~{} baris). Proses load bisa memakan waktu, mohon menunggu."
        )

    def __init__(self):
        super().__init__()

        # === Left controls ===
        box_conn = gui.widgetBox(self.controlArea, "Sumber")
        self.lbl_conn = QtWidgets.QLabel("-")
        self.lbl_conn.setTextInteractionFlags(Qt.TextSelectableByMouse)
        box_conn.layout().addWidget(self.lbl_conn)

        box_opts = gui.widgetBox(self.controlArea, "Daftar Tabel")
        gui.checkBox(box_opts, self, "include_system", "Tampilkan system schemas",
                     callback=self._reload_tables)

        # filter + list
        f_layout = QtWidgets.QHBoxLayout()
        f_layout.addWidget(QtWidgets.QLabel("Filter:"))
        self.edit_filter = QtWidgets.QLineEdit(self.filter_text)
        f_layout.addWidget(self.edit_filter)
        box_opts.layout().addLayout(f_layout)
        self.edit_filter.textChanged.connect(self._apply_filter)

        self.list_tables = QtWidgets.QListWidget()
        self.list_tables.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_tables.itemSelectionChanged.connect(self._on_select_table)
        # biar nama tabel panjang tetap bisa terlihat
        self.list_tables.setTextElideMode(Qt.ElideNone)
        self.list_tables.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_tables.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        box_list = gui.widgetBox(self.controlArea, "Tabel (schema.table)")
        box_list.layout().addWidget(self.list_tables)

        # options untuk warning threshold
        box_warn = gui.widgetBox(self.controlArea, "Options")

        # label terpisah supaya bisa word wrap dan tidak terpotong
        lbl_warn = QtWidgets.QLabel("Warning jika rows > N (0 = off):")
        lbl_warn.setWordWrap(True)
        box_warn.layout().addWidget(lbl_warn)

        # spin tanpa label (label=None)
        gui.spin(
            box_warn, self, "warn_threshold",
            0, 2_147_483_647, step=100_000,
            label=None,
        )

        gui.checkBox(
            box_warn, self,
            "autorun_on_select",
            "Auto-load saat pilih tabel",
        )


        # progress
        pbox = gui.widgetBox(self.controlArea, "Progress")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        pbox.layout().addWidget(self.progress)

        # === Right: Data sample view (opsional, hanya untuk preview) ===
        self.view = QtWidgets.QTableView(self.mainArea)
        if self.mainArea.layout() is None:
            self.mainArea.setLayout(QtWidgets.QVBoxLayout())
        self.mainArea.layout().addWidget(self.view)

        # state
        self._engine: Optional[sa.Engine] = None
        self._all_tables: List[str] = []  # list of "schema.table"
        self._worker: Optional[LoadTableWorker] = None

    # ===== lifecycle =====
    def onDeleteWidget(self):
        self._kill_worker()
        super().onDeleteWidget()

    # ===== input =====
    @Inputs.Connection
    def set_engine(self, engine: Optional[object]):
        self._engine = engine if isinstance(engine, sa.Engine) else None
        self._kill_worker()
        self.view.setModel(None)
        self.list_tables.clear()
        self._all_tables.clear()
        self.Error.clear(); self.Info.clear(); self.Warning.clear()
        self.Outputs.Data.send(None)

        if not self._engine:
            self.lbl_conn.setText("-")
            self.Error.no_connection()
            return

        # show basic connection info
        try:
            url = self._engine.url
            host = getattr(url, "host", None) or "-"
            port = getattr(url, "port", None) or "-"
            dbnm = getattr(url, "database", None) or "-"
            self.lbl_conn.setText(f"{_dialect_name(self._engine)} | {host}:{port} | DB: {dbnm}")
        except Exception:
            self.lbl_conn.setText(f"{_dialect_name(self._engine)}")

        self._reload_tables()

    # ===== helpers =====
    def _kill_worker(self):
        w = self._worker
        if not w:
            return
        try:
            w.finished.disconnect()
        except Exception:
            pass
        try:
            if w.isRunning():
                getattr(w, "requestInterruption", lambda: None)()
                w.quit()
                w.wait(1500)
        except Exception:
            pass
        self._worker = None

    def _reload_tables(self):
        """Mirip dengan ListTablesWorker di widget lain, tapi synchronous & sederhana."""
        if not self._engine:
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.list_tables.clear()
        self._all_tables.clear()
        self.Warning.clear()
        self.Info.status("Membaca daftar schema & tabel …")

        try:
            with self._engine.connect() as con:
                name = _dialect_name(self._engine)

                # ClickHouse: ambil dari system.tables untuk DB aktif
                if name.startswith("clickhouse"):
                    current_db = self._engine.url.database or ""
                    q = """
                    SELECT
                      database,
                      name
                    FROM system.tables
                    WHERE database = :db
                    ORDER BY database, name
                    """
                    rows = con.execute(sa.text(q), {"db": current_db}).mappings().all()
                    pairs = [(r["database"], r["name"]) for r in rows]
                else:
                    insp = sa.inspect(con)
                    schemas: List[str] = insp.get_schema_names()
                    pairs: List[Tuple[str, str]] = []

                    def _is_system(s: str) -> bool:
                        s_low = s.lower()
                        if name in ("postgresql", "postgres"):
                            return s_low.startswith("pg_") or s_low in {"information_schema"}
                        if name in ("mysql", "mariadb"):
                            return s_low in {"mysql", "information_schema", "performance_schema", "sys"}
                        if name in ("mssql", "pyodbc"):
                            return s_low in {"sys", "information_schema"}
                        return False

                    for sch in schemas:
                        if not self.include_system and _is_system(sch):
                            continue
                        try:
                            tabs = insp.get_table_names(schema=sch)
                        except Exception:
                            tabs = []
                        for t in tabs:
                            pairs.append((sch or "", t))

                pairs.sort(key=lambda x: (x[0], x[1]))
                self._all_tables = [
                    f"{sch}.{tab}" if sch else tab for sch, tab in pairs
                ]
                self._apply_filter()
                self.Info.status(f"Total tabel: {len(self._all_tables)}")
        except Exception as e:
            self.Error.no_connection(str(e))
        finally:
            self.progress.setVisible(False)

    def _apply_filter(self):
        text = self.edit_filter.text().strip().lower()
        self.list_tables.clear()
        for fq in self._all_tables:
            if not text or text in fq.lower():
                item = QtWidgets.QListWidgetItem(fq)
                item.setToolTip(fq)
                self.list_tables.addItem(item)

    def _on_select_table(self):
        sel = self.list_tables.selectedItems()
        if not sel:
            return
        fq = sel[0].text()
        self.last_selected = fq
        self.Info.table(fq)
        if self.autorun_on_select:
            self._load_table_for(fq)

    def _split_schema_table(self, fq: str) -> Tuple[Optional[str], str]:
        if "." in fq:
            parts = fq.split(".", 1)
            return parts[0], parts[1]
        return None, fq

    def _load_table_for(self, fq: str):
        if not self._engine:
            return
        self._kill_worker()
        self.Error.clear(); self.Warning.clear()
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.view.setModel(None)
        self.Outputs.Data.send(None)

        schema, table = self._split_schema_table(fq)
        self._worker = LoadTableWorker(
            engine=self._engine,
            schema=schema,
            table=table,
            warn_threshold=self.warn_threshold,
            parent=self,
        )
        self._worker.status.connect(lambda m: self.Info.status(m))
        self._worker.row_count.connect(self._on_row_count)
        self._worker.finished_df.connect(self._on_df_ready)
        self._worker.failed.connect(lambda e: self.Error.load_failed(e))
        self._worker.finished.connect(lambda: self.progress.setVisible(False))
        self._worker.start()

    def _on_row_count(self, n_rows: Optional[int]):
        if n_rows is None or self.warn_threshold <= 0:
            self.Warning.clear()
            return
        if n_rows > self.warn_threshold:
            self.Warning.large_table(n_rows)
        else:
            self.Warning.clear()

    def _on_df_ready(self, df: pd.DataFrame):
        # tampilkan preview di sisi kanan
        class DFModel(QtCore.QAbstractTableModel):
            def __init__(self, df):
                super().__init__()
                self.df = df.reset_index(drop=True)

            def rowCount(self, parent=QtCore.QModelIndex()):
                return 0 if parent.isValid() else len(self.df)

            def columnCount(self, parent=QtCore.QModelIndex()):
                return 0 if parent.isValid() else len(self.df.columns)

            def data(self, index, role=Qt.DisplayRole):
                if not index.isValid() or role != Qt.DisplayRole:
                    return None
                val = self.df.iat[index.row(), index.column()]
                return "" if pd.isna(val) else str(val)

            def headerData(self, section, orientation, role=Qt.DisplayRole):
                if role != Qt.DisplayRole:
                    return None
                if orientation == Qt.Horizontal:
                    try:
                        return str(self.df.columns[section])
                    except Exception:
                        return str(section)
                else:
                    return str(section + 1)

        self.view.setModel(DFModel(df))

        # kirim ke workflow sebagai Orange Table penuh
        try:
            table = table_from_frame(df)
        except Exception as e:
            self.Error.load_failed(f"Konversi ke Orange Table gagal: {e}")
            self.Outputs.Data.send(None)
            return

        self.Outputs.Data.send(table)
