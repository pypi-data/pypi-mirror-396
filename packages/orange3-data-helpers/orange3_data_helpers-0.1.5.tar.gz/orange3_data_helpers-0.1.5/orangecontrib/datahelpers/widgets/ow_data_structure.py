# orangecontrib/datahelpers/widgets/ow_data_structure.py
from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget import gui
from orangewidget.settings import Setting
from Orange.data.pandas_compat import table_from_frame
from Orange.data import Table

import pandas as pd
import sqlalchemy as sa
from typing import Optional, List, Tuple


# --------------------- Worker ---------------------
class InspectWorker(QThread):
    status = pyqtSignal(str)
    progress_max = pyqtSignal(int)
    progress_val = pyqtSignal(int)
    finished_df = pyqtSignal(object)     # pandas.DataFrame
    failed = pyqtSignal(str)

    def __init__(self, engine: sa.Engine, mode: str, include_system: bool, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.mode = mode
        self.include_system = include_system

    # ------- Helpers -------
    def _dialect_name(self) -> str:
        try:
            return self.engine.url.get_backend_name()
        except Exception:
            return getattr(self.engine.dialect, 'name', 'unknown')

    def _read_df(self, con, sql: str) -> pd.DataFrame:
        """Compat reader for SA 2.x + pandas: execute text and build DataFrame."""
        res = con.execute(sa.text(sql))
        rows = res.mappings().all()
        return pd.DataFrame(rows)

    # PostgreSQL
    def _pg_list(self, con) -> pd.DataFrame:
        self.status.emit("PostgreSQL: membaca daftar schema/tabel …")
        filt = "" if self.include_system else "AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_%'"
        q = f"""
        SELECT n.nspname AS schema, c.relname AS "table",
               pg_total_relation_size(c.oid) AS bytes_total,
               c.reltuples AS row_estimate
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','p','m') {filt}
        ORDER BY 1,2;
        """
        df = self._read_df(con, q)
        if self.mode == "exact":
            self.status.emit("PostgreSQL: menghitung COUNT(*) per tabel …")
            self.progress_max.emit(len(df))
            counts = []
            for i, r in df.iterrows():
                if self.isInterruptionRequested():
                    raise RuntimeError("Dibatalkan pengguna.")
                sch, tab = r["schema"], r["table"]
                try:
                    cnt = con.execute(sa.text(f'SELECT COUNT(*) FROM "{sch}"."{tab}"')).scalar()
                except Exception:
                    cnt = None
                counts.append(cnt)
                self.progress_val.emit(i+1)
            df["rows"] = counts
        elif self.mode == "estimate":
            df["rows"] = df["row_estimate"].astype("Int64")
        else:
            df["rows"] = pd.NA
        df["size_bytes"] = df["bytes_total"].astype("Int64")
        return df[["schema","table","rows","size_bytes"]]

    # MySQL / MariaDB
    def _mysql_list(self, con) -> pd.DataFrame:
        self.status.emit("MySQL: membaca information_schema.tables …")
        filt = "" if self.include_system else "AND table_schema NOT IN ('mysql','information_schema','performance_schema','sys')"
        q = f"""
        SELECT table_schema AS schema,
               table_name AS `table`,
               table_rows AS row_estimate,
               data_length + index_length AS size_bytes
        FROM information_schema.tables
        WHERE table_type='BASE TABLE' {filt}
        ORDER BY 1,2;
        """
        df = self._read_df(con, q)
        if self.mode == "exact":
            self.status.emit("MySQL: menghitung COUNT(*) per tabel …")
            self.progress_max.emit(len(df))
            counts = []
            for i, r in df.iterrows():
                if self.isInterruptionRequested():
                    raise RuntimeError("Dibatalkan pengguna.")
                sch, tab = r["schema"], r["table"]
                try:
                    cnt = con.execute(sa.text(f"SELECT COUNT(*) FROM `{sch}`.`{tab}`")).scalar()
                except Exception:
                    cnt = None
                counts.append(cnt)
                self.progress_val.emit(i+1)
            df["rows"] = counts
        elif self.mode == "estimate":
            df["rows"] = df["row_estimate"].astype("Int64")
        else:
            df["rows"] = pd.NA
        df["size_bytes"] = df["size_bytes"].astype("Int64")
        return df[["schema","table","rows","size_bytes"]]

    # SQLite
    def _sqlite_list(self, con) -> pd.DataFrame:
        self.status.emit("SQLite: membaca sqlite_master …")
        q = "SELECT '' AS schema, name AS `table` FROM sqlite_master WHERE type='table' ORDER BY 2;"
        df = self._read_df(con, q)
        if self.mode == "exact":
            self.progress_max.emit(len(df))
            counts = []
            for i, r in df.iterrows():
                tab = r["table"]
                try:
                    cnt = con.execute(sa.text(f'SELECT COUNT(*) FROM "{tab}"')).scalar()
                except Exception:
                    cnt = None
                counts.append(cnt)
                self.progress_val.emit(i+1)
            df["rows"] = counts
        else:
            df["rows"] = pd.NA
        df["size_bytes"] = pd.NA
        return df[["schema","table","rows","size_bytes"]]

    # SQL Server
        # SQL Server
    def _mssql_list(self, con) -> pd.DataFrame:
        self.status.emit("SQL Server: membaca sys.tables/sys.schemas …")
        filt = "" if self.include_system else "AND s.name NOT IN ('sys','INFORMATION_SCHEMA')"
        q = f"""
        SELECT
          s.name AS [schema],
          t.name AS [table],
          SUM(p.rows) AS rows,
          SUM(a.total_pages) * 8 * 1024 AS size_bytes
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0,1)
        JOIN sys.allocation_units a ON p.partition_id = a.container_id
        WHERE 1=1 {filt}
        GROUP BY s.name, t.name
        ORDER BY s.name, t.name
        """
        df = self._read_df(con, q)
        if self.mode == "none":
            df["rows"] = pd.NA
        return df[["schema","table","rows","size_bytes"]]
    
        # Oracle
    def _oracle_list(self, con) -> pd.DataFrame:
        self.status.emit("Oracle: membaca ALL_TABLES …")

        # filter schema system kalau include_system=False
        if self.include_system:
            filt = ""
        else:
            filt = """
              AND owner NOT IN (
                'SYS','SYSTEM','XDB','MDSYS','CTXSYS','ORDSYS','OLAPSYS',
                'WMSYS','EXFSYS','OUTLN','DBSNMP','APPQOSSYS','AUDSYS',
                'GSMADMIN_INTERNAL','DVSYS','LBACSYS','OJVMSYS'
              )
            """

        q = f"""
        SELECT
          owner      AS schema,
          table_name AS "table",
          num_rows   AS row_estimate
        FROM all_tables
        WHERE 1 = 1 {filt}
        ORDER BY owner, table_name
        """
        df = self._read_df(con, q)

        # mode hitung rows
        if self.mode == "exact":
            self.status.emit("Oracle: menghitung COUNT(*) per tabel …")
            self.progress_max.emit(len(df))
            counts = []
            for i, r in df.iterrows():
                if self.isInterruptionRequested():
                    raise RuntimeError("Dibatalkan pengguna.")

                sch = r["schema"]
                tab = r["table"]
                # nama schema/tabel di ALL_TABLES biasanya UPPER → aman pakai kutip standar Oracle
                fq = f'"{sch}"."{tab}"'
                try:
                    cnt = con.execute(sa.text(f"SELECT COUNT(*) FROM {fq}")).scalar()
                except Exception:
                    cnt = None
                counts.append(cnt)
                self.progress_val.emit(i + 1)
            df["rows"] = counts

        elif self.mode == "estimate":
            # pakai NUM_ROWS dari ALL_TABLES (hasil analisis statistik, bisa NULL)
            df["rows"] = df["row_estimate"].astype("Int64")
        else:
            df["rows"] = pd.NA

        # untuk sekarang size_bytes kita set NA dulu (butuh akses ALL_SEGMENTS/DBA_SEGMENTS)
        df["size_bytes"] = pd.NA
        return df[["schema", "table", "rows", "size_bytes"]]



        # ClickHouse
    def _ch_list(self, con) -> pd.DataFrame:
        self.status.emit("ClickHouse: membaca system.tables …")

        # filter DB system kalau include_system=False
        filt = "" if self.include_system else "AND database NOT IN ('system')"

        q = f"""
        SELECT
          database    AS schema,
          name        AS `table`,
          total_rows  AS rows,
          total_bytes AS size_bytes
        FROM system.tables
        WHERE engine != 'View' {filt}
        ORDER BY database, name
        """  # <- TIDAK ada `;` di akhir

        df = self._read_df(con, q)
        if self.mode == "none":
            df["rows"] = pd.NA
        return df[["schema", "table", "rows", "size_bytes"]]


    def run(self):
        try:
            with self.engine.connect() as con:
                name = self._dialect_name()
                if name in ("postgresql", "postgres"):
                    df = self._pg_list(con)
                elif name in ("mysql", "mariadb"):
                    df = self._mysql_list(con)
                elif name in ("sqlite", "sqlite3"):
                    df = self._sqlite_list(con)
                elif name in ("mssql", "pyodbc"):
                    df = self._mssql_list(con)
                elif name.startswith("clickhouse"):
                    df = self._ch_list(con)
                elif name.startswith("oracle"):
                    df = self._oracle_list(con)
                else:
                    self.failed.emit(f"Dialect {name} belum didukung penuh.")
                    return
            self.finished_df.emit(df)
        except Exception as e:
            self.failed.emit(str(e))


# --------------------- Widget ---------------------
class OWHDataStructure(OWWidget):
    name = "Query Structure"
    id = "datahelpers-data-structure"
    description = "Ringkasan schema, table, dan jumlah baris per table."
    icon = "icons/table_structure.png"
    priority = 12
    want_main_area = True

    class Inputs:
        Connection = Input("Connection", object, auto_summary=False)

    class Outputs:
        Summary = Output("Summary", Table, default=True)

    mode: str = Setting("estimate")  # estimate | exact | none
    include_system: bool = Setting(False)
    sort_by: str = Setting("rows_desc")

    class Error(OWWidget.Error):
        no_connection = Msg("Belum ada koneksi.")
        run_failed = Msg("Gagal membaca struktur: {}")

    class Info(OWWidget.Information):
        summary = Msg("Schemas: {} | Tables: {}")
        status = Msg("{}")

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, "Options")
        gui.comboBox(box, self, "mode", items=["estimate","exact","none"],
                     sendSelectedValue=True, label="Row count mode:")
        gui.checkBox(box, self, "include_system", "Tampilkan system schemas")
        gui.comboBox(box, self, "sort_by", items=["rows_desc","rows_asc","schema_table"],
                     sendSelectedValue=True, label="Urutkan:")
        self.btn_run = gui.button(box, self, "Scan", callback=self._run)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(True)
        gui.widgetBox(self.controlArea, "Progress").layout().addWidget(self.progress)

        self.view = QtWidgets.QTableView(self.mainArea)
        if self.mainArea.layout() is None:
            self.mainArea.setLayout(QtWidgets.QVBoxLayout())
        self.mainArea.layout().addWidget(self.view)

        self._engine: Optional[sa.Engine] = None
        self._worker: Optional[InspectWorker] = None
        self._df: Optional[pd.DataFrame] = None

    @Inputs.Connection
    def set_engine(self, engine: Optional[object]):
        self._engine = engine if isinstance(engine, sa.Engine) else None
        if not self._engine:
            self.Error.no_connection()
            return
        self._run()

    def _run(self):
        if not self._engine:
            self.Error.no_connection()
            return
        self._worker = InspectWorker(self._engine, self.mode, self.include_system, parent=self)
        self._worker.status.connect(lambda m: self.Info.status(m))
        self._worker.progress_max.connect(lambda m: self.progress.setRange(0,m))
        self._worker.progress_val.connect(lambda v: self.progress.setValue(v))
        self._worker.finished_df.connect(self._on_done)
        self._worker.failed.connect(lambda e: self.Error.run_failed(e))
        self._worker.start()

    def _on_done(self, df: pd.DataFrame):
        if self.sort_by == "rows_desc":
            df = df.sort_values(by=["rows"], ascending=[False], na_position="last")
        elif self.sort_by == "rows_asc":
            df = df.sort_values(by=["rows"], ascending=[True], na_position="first")
        else:
            df = df.sort_values(by=["schema","table"])
        self._df = df.reset_index(drop=True)

        class DFModel(QtCore.QAbstractTableModel):
            def __init__(self, df): super().__init__(); self.df=df
            def rowCount(self,p=QtCore.QModelIndex()): return len(self.df)
            def columnCount(self,p=QtCore.QModelIndex()): return len(self.df.columns)
            def data(self, idx, role):
                if not idx.isValid() or role!=Qt.DisplayRole: return None
                val=self.df.iat[idx.row(), idx.column()]
                return "" if pd.isna(val) else str(val)
            def headerData(self,sec,ori,role):
                if role!=Qt.DisplayRole: return None
                return str(self.df.columns[sec]) if ori==Qt.Horizontal else str(sec+1)

        self.view.setModel(DFModel(self._df))
        self.Outputs.Summary.send(table_from_frame(self._df))
        schemas = int(self._df["schema"].nunique(dropna=True))
        tables = len(self._df)
        self.Info.summary(schemas, tables)
