# orangecontrib/datahelpers/widgets/ow_data_overview.py
from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Input, Msg
from orangewidget.settings import Setting
from orangewidget import gui

import pandas as pd
import sqlalchemy as sa
from typing import Optional, List, Tuple


# =============== Utils ===============
def _dialect_name(engine: sa.Engine) -> str:
    try:
        return engine.url.get_backend_name()
    except Exception:
        return getattr(engine.dialect, "name", "unknown")


def _quote_fq(engine: sa.Engine, schema: Optional[str], table: str) -> str:
    """Fully-qualified name with proper quoting for the engine dialect."""
    prep = engine.dialect.identifier_preparer
    if schema and str(schema).strip():
        return f"{prep.quote_schema(schema)}.{prep.quote(table)}"
    return prep.quote(table)


def _df_to_qt_model(df: pd.DataFrame) -> QtCore.QAbstractTableModel:
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


# =============== Workers ===============
class ListTablesWorker(QThread):
    finished_ok = pyqtSignal(object)     # list[(schema, table)]
    failed = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, engine: sa.Engine, include_system: bool, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.include_system = include_system

    def run(self):
        try:
            with self.engine.connect() as con:
                name = _dialect_name(self.engine)
                self.status.emit(f"{name}: membaca daftar schema & tabel …")

                # === KHUSUS CLICKHOUSE (dialect clickhousedb / clickhouse) ===
                if name.startswith("clickhouse"):
                    # database saat ini dari URL
                    current_db = self.engine.url.database or ""

                    # Kalau mau cuma 1 DB (yang di-URL):
                    q = """
                    SELECT
                      database,
                      name
                    FROM system.tables
                    WHERE database = :db
                    ORDER BY database, name
                    """
                    rows = con.execute(sa.text(q), {"db": current_db}).mappings().all()
                    out = [(r["database"], r["name"]) for r in rows]
                    self.finished_ok.emit(out)
                    return

                # === generic untuk dialect lain ===
                insp = sa.inspect(con)
                schemas: List[str] = insp.get_schema_names()
                out: List[Tuple[str, str]] = []

                def _is_system(s: str) -> bool:
                    s_low = s.lower()
                    if name in ("postgresql", "postgres"):
                        return s_low.startswith("pg_") or s_low in {"information_schema"}
                    if name in ("mysql", "mariadb"):
                        return s_low in {"mysql", "information_schema", "performance_schema", "sys"}
                    if name in ("mssql", "pyodbc"):
                        return s_low in {"sys", "information_schema"}
                    # sqlite/clickhouse umumnya aman
                    return False

                for sch in schemas:
                    if not self.include_system and _is_system(sch):
                        continue
                    try:
                        tabs = insp.get_table_names(schema=sch)
                    except Exception:
                        tabs = []
                    for t in tabs:
                        out.append((sch or "", t))

                out.sort(key=lambda x: (x[0], x[1]))
                self.finished_ok.emit(out)
        except Exception as e:
            self.failed.emit(str(e))


class LoadOverviewWorker(QThread):
    finished_cols = pyqtSignal(object)   # DataFrame
    finished_sample = pyqtSignal(object) # DataFrame
    failed = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, engine: sa.Engine, schema: Optional[str], table: str, sample_limit: int, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.schema = schema or ""
        self.table = table
        self.sample_limit = max(0, int(sample_limit))

    def _read_df(self, con, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        res = con.execute(sa.text(sql), params or {})
        rows = res.mappings().all()
        return pd.DataFrame(rows)

    def _columns_df(self, con) -> pd.DataFrame:
        d = _dialect_name(self.engine)
        s, t = self.schema, self.table

        try:
            if d in ("postgresql", "postgres"):
                self.status.emit("Memuat metadata kolom (PostgreSQL)…")
                q = """
                SELECT
                  column_name   AS name,
                  data_type     AS type,
                  is_nullable   AS nullable,
                  column_default AS "default",
                  ordinal_position AS ord
                FROM information_schema.columns
                WHERE table_schema = :s AND table_name = :t
                ORDER BY ordinal_position
                """
                return self._read_df(con, q, {"s": s, "t": t})

            elif d in ("mysql", "mariadb"):
                self.status.emit("Memuat metadata kolom (MySQL)…")
                q = """
                SELECT
                  column_name   AS name,
                  column_type   AS type,
                  is_nullable   AS nullable,
                  column_default AS `default`,
                  ordinal_position AS ord
                FROM information_schema.columns
                WHERE table_schema = :s AND table_name = :t
                ORDER BY ordinal_position
                """
                return self._read_df(con, q, {"s": s, "t": t})

            elif d in ("mssql", "pyodbc"):
                self.status.emit("Memuat metadata kolom (SQL Server)…")
                q = """
                SELECT
                  COLUMN_NAME   AS name,
                  DATA_TYPE     AS type,
                  IS_NULLABLE   AS nullable,
                  COLUMN_DEFAULT AS [default],
                  ORDINAL_POSITION AS ord
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t
                ORDER BY ORDINAL_POSITION
                """
                return self._read_df(con, q, {"s": s, "t": t})

            elif d in ("sqlite", "sqlite3"):
                self.status.emit("Memuat metadata kolom (SQLite)…")
                # schema diabaikan; pakai PRAGMA table_info
                prep = self.engine.dialect.identifier_preparer
                qname = prep.quote(self.table)
                res = con.execute(sa.text(f"PRAGMA table_info({qname})"))
                rows = res.fetchall()
                if not rows:
                    return pd.DataFrame(columns=["name", "type", "nullable", "default", "ord"])
                colnames = [c[1] for c in rows]      # name
                coltypes = [c[2] for c in rows]      # type
                notnull  = [c[3] for c in rows]      # 1/0
                dflts    = [c[4] for c in rows]      # default
                ords     = [c[0] for c in rows]      # cid
                return pd.DataFrame({
                    "name": colnames,
                    "type": coltypes,
                    "nullable": ["NO" if x else "YES" for x in notnull],
                    "default": dflts,
                    "ord": ords
                }).sort_values("ord")

            elif d.startswith("clickhouse"):
                self.status.emit("Memuat metadata kolom (ClickHouse)…")

                # Di ClickHouse tidak ada kolom `null_allowed`.
                # Nullability bisa dilihat dari tipe: Nullable(T).
                # Kita juga pastikan TIDAK ada `;` di akhir query.
                db_name = (self.schema or self.engine.url.database) or ""

                q = """
                SELECT
                  name                              AS name,
                  type                              AS type,
                  multiIf(
                    type LIKE 'Nullable(%', 'YES',  -- kalau Nullable(T)
                    'NO'
                  )                                 AS nullable,
                  default_expression                AS "default",
                  position                          AS ord
                FROM system.columns
                WHERE database = :db AND table = :tbl
                ORDER BY ord
                """

                try:
                    return self._read_df(con, q, {"db": db_name, "tbl": t})
                except Exception:
                    pass

                # --- fallback generic inspector untuk DB lain / jika ClickHouse block gagal ---
                self.status.emit(f"Memuat metadata kolom (generic: {d})…")
                insp = sa.inspect(con)
                cols = insp.get_columns(self.table, schema=self.schema or None)
                rows = []
                for i, c in enumerate(cols, start=1):
                    rows.append({
                        "name": c.get("name"),
                        "type": str(c.get("type")),
                        "nullable": "YES" if c.get("nullable", True) else "NO",
                        "default": c.get("default"),
                        "ord": i
                    })
                return pd.DataFrame(rows)

            else:
                # generic inspector
                self.status.emit(f"Memuat metadata kolom (generic: {d})…")
                insp = sa.inspect(con)
                cols = insp.get_columns(self.table, schema=self.schema or None)
                rows = []
                for i, c in enumerate(cols, start=1):
                    rows.append({
                        "name": c.get("name"),
                        "type": str(c.get("type")),
                        "nullable": "YES" if c.get("nullable", True) else "NO",
                        "default": c.get("default"),
                        "ord": i
                    })
                return pd.DataFrame(rows)

        except Exception as e:
            raise

    def _sample_df(self, con) -> pd.DataFrame:
        if self.sample_limit == 0:
            return pd.DataFrame()

        fq = _quote_fq(self.engine, self.schema, self.table)
        d = _dialect_name(self.engine)
        self.status.emit(f"Memuat sample rows (LIMIT {self.sample_limit}) …")

        limit = int(self.sample_limit)

        if d in ("mssql", "pyodbc"):
            sql = f"SELECT TOP {limit} * FROM {fq}"
            res = con.execute(sa.text(sql))
            rows = res.mappings().all()
            return pd.DataFrame(rows)

        # KHUSUS ORACLE: pakai ROWNUM, bukan LIMIT
        if d.startswith("oracle"):
            # contoh: SELECT * FROM schema.table WHERE ROWNUM <= 100
            sql = f"SELECT * FROM {fq} WHERE ROWNUM <= {limit}"
            res = con.execute(sa.text(sql))
            rows = res.mappings().all()
            return pd.DataFrame(rows)

        # default: LIMIT (Postgres, MySQL, SQLite, ClickHouse, dll.)
        sql = f"SELECT * FROM {fq} LIMIT {limit}"
        res = con.execute(sa.text(sql))
        rows = res.mappings().all()
        return pd.DataFrame(rows)

    def run(self):
        try:
            with self.engine.connect() as con:
                cols = self._columns_df(con)
                self.finished_cols.emit(cols)
                sample = self._sample_df(con)
                self.finished_sample.emit(sample)
        except Exception as e:
            self.failed.emit(str(e))


# =============== Widget ===============
class OWHDataOverview(OWWidget):
    name = "Query Data Overview"
    id = "datahelpers-data-overview"
    description = "Lihat kolom & contoh baris (sample) untuk tabel yang dipilih."
    icon = "icons/data_overview.png"
    priority = 13
    want_main_area = True

    class Inputs:
        Connection = Input("Connection", object, auto_summary=False)

    # Settings
    include_system: bool = Setting(False)
    sample_limit: int = Setting(100)
    last_selected: str = Setting("")  # schema.table
    filter_text: str = Setting("")
    autorun_on_select: bool = Setting(True)

    class Error(OWWidget.Error):
        no_connection = Msg("Belum ada koneksi.")
        load_failed = Msg("Gagal memuat overview: {}")

    class Info(OWWidget.Information):
        status = Msg("{}")
        table = Msg("Tabel: {}")

    def __init__(self):
        super().__init__()

        # === Left controls ===
        box_conn = gui.widgetBox(self.controlArea, "Sumber")
        self.lbl_conn = QtWidgets.QLabel("-")
        self.lbl_conn.setTextInteractionFlags(Qt.TextSelectableByMouse)
        box_conn.layout().addWidget(self.lbl_conn)

        box_opts = gui.widgetBox(self.controlArea, "Daftar Tabel")
        gui.checkBox(box_opts, self, "include_system", "Tampilkan system schemas", callback=self._reload_tables)

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
        box_list = gui.widgetBox(self.controlArea, "Tabel (schema.table)")
        box_list.layout().addWidget(self.list_tables)
        
        self.list_tables.setTextElideMode(Qt.ElideNone)
        self.list_tables.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_tables.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        # sample options
        box_sample = gui.widgetBox(self.controlArea, "Sample")
        self.spin_limit = gui.spin(box_sample, self, "sample_limit", 0, 2_147_483_647, step=10, label="Limit rows (0 = none):")
        gui.checkBox(box_sample, self, "autorun_on_select", "Auto-load saat pilih tabel")

        # progress
        pbox = gui.widgetBox(self.controlArea, "Progress")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        pbox.layout().addWidget(self.progress)

        # === Right area: tabs for Columns / Sample Rows ===
        self.tabs = QtWidgets.QTabWidget(self.mainArea)
        if self.mainArea.layout() is None:
            self.mainArea.setLayout(QtWidgets.QVBoxLayout())
        self.mainArea.layout().addWidget(self.tabs)

        # Columns tab
        self.view_cols = QtWidgets.QTableView()
        tab_cols = QtWidgets.QWidget()
        lay_cols = QtWidgets.QVBoxLayout(tab_cols)
        lay_cols.addWidget(self.view_cols)
        self.tabs.addTab(tab_cols, "Columns")

        # Sample tab
        self.view_sample = QtWidgets.QTableView()
        tab_sample = QtWidgets.QWidget()
        lay_s = QtWidgets.QVBoxLayout(tab_sample)
        lay_s.addWidget(self.view_sample)
        self.tabs.addTab(tab_sample, "Sample Rows")

        # state
        self._engine: Optional[sa.Engine] = None
        self._all_tables: List[str] = []  # list of "schema.table"
        self._worker_list: Optional[ListTablesWorker] = None
        self._worker_over: Optional[LoadOverviewWorker] = None

    # ===== lifecycle =====
    def onDeleteWidget(self):
        self._kill_workers()
        super().onDeleteWidget()

    # ===== input =====
    @Inputs.Connection
    def set_engine(self, engine: Optional[object]):
        self._engine = engine if isinstance(engine, sa.Engine) else None
        self._kill_workers()
        self.view_cols.setModel(None)
        self.view_sample.setModel(None)
        self.list_tables.clear()
        self._all_tables.clear()
        self.Error.clear(); self.Info.clear()

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

        # load tables
        self._reload_tables()

    # ===== helpers =====
    def _kill_workers(self):
        for w in (self._worker_list, self._worker_over):
            if not w:
                continue
            try:
                w.finished.disconnect()
            except Exception:
                pass
            try:
                if w.isRunning():
                    getattr(w, "requestInterruption", lambda: None)()
                    w.quit(); w.wait(1500)
            except Exception:
                pass
        self._worker_list = None
        self._worker_over = None

    def _reload_tables(self):
        if not self._engine:
            return
        self.progress.setVisible(True); self.progress.setRange(0, 0)
        self.list_tables.clear()
        self._all_tables.clear()

        self._worker_list = ListTablesWorker(self._engine, self.include_system, parent=self)
        self._worker_list.status.connect(lambda m: self.Info.status(m))
        self._worker_list.finished_ok.connect(self._on_tables_loaded)
        self._worker_list.failed.connect(lambda e: self.Error.no_connection(str(e)))
        self._worker_list.finished.connect(lambda: self.progress.setVisible(False))
        self._worker_list.start()

    def _on_tables_loaded(self, rows: List[Tuple[str, str]]):
        # build full names
        items = []
        for sch, tab in rows:
            fq = f"{sch}.{tab}" if sch else tab
            items.append(fq)
        self._all_tables = items
        self._apply_filter()  # populate list by current filter

        # restore last selected if exists
        if self.last_selected and self.last_selected in self._all_tables:
            matches = self.list_tables.findItems(self.last_selected, Qt.MatchExactly)
            if matches:
                self.list_tables.setCurrentItem(matches[0])

    def _apply_filter(self):
        text = self.edit_filter.text().strip().lower()
        self.list_tables.clear()
        for fq in self._all_tables:
            if not text or text in fq.lower():
                item = QtWidgets.QListWidgetItem(fq)
                # tooltip
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
            self._load_overview_for(fq)

    def _split_schema_table(self, fq: str) -> Tuple[Optional[str], str]:
        if "." in fq:
            parts = fq.split(".", 1)
            return parts[0], parts[1]
        return None, fq

    def _load_overview_for(self, fq: str):
        if not self._engine:
            return
        schema, table = self._split_schema_table(fq)
        self.progress.setVisible(True); self.progress.setRange(0, 0)
        self.view_cols.setModel(None); self.view_sample.setModel(None)

        self._worker_over = LoadOverviewWorker(
            engine=self._engine,
            schema=schema,
            table=table,
            sample_limit=self.sample_limit,
            parent=self
        )
        self._worker_over.status.connect(lambda m: self.Info.status(m))
        self._worker_over.finished_cols.connect(self._on_cols_loaded)
        self._worker_over.finished_sample.connect(self._on_sample_loaded)
        self._worker_over.failed.connect(lambda e: self.Error.load_failed(e))
        self._worker_over.finished.connect(lambda: self.progress.setVisible(False))
        self._worker_over.start()

    # ===== callbacks =====
    def _on_cols_loaded(self, df: pd.DataFrame):
        self.view_cols.setModel(_df_to_qt_model(df))

    def _on_sample_loaded(self, df: pd.DataFrame):
        self.view_sample.setModel(_df_to_qt_model(df))
