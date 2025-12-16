# orangecontrib/datahelpers/widgets/ow_save_big.py
from AnyQt import QtWidgets, QtCore
from AnyQt.QtCore import Qt, QThread, pyqtSignal
from Orange.widgets.widget import OWWidget, Input, Msg
from orangewidget import gui
from orangewidget.settings import Setting
from Orange.data import Table
from Orange.data.pandas_compat import table_to_frame

import os
import math
import gzip
import pandas as pd
from typing import Optional

# ---------- Optional dependencies ----------
# Parquet
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PARQUET = True
except Exception:
    HAS_PARQUET = False

# Excel writer (prefer xlsxwriter, fallback openpyxl)
try:
    import xlsxwriter  # noqa: F401
    EXCEL_ENGINE = "xlsxwriter"
except Exception:
    try:
        import openpyxl  # noqa: F401
        EXCEL_ENGINE = "openpyxl"
    except Exception:
        EXCEL_ENGINE = None


# ================== Worker ==================
class SaveWorker(QThread):
    status = pyqtSignal(str)
    progress_total = pyqtSignal(int)   # set max (jumlah baris)
    progress_value = pyqtSignal(int)   # set progress (baris tertulis)
    finished_ok = pyqtSignal(str)      # pesan sukses
    failed = pyqtSignal(str)

    def __init__(
        self,
        table: Table,
        out_dir: str,
        base_name: str,
        fmt: str,               # "CSV" | "Parquet" | "Excel (xlsx)"
        rows_per_chunk: int,    # baris per tulis
        split_files: bool,      # True -> bikin banyak file per chunk
        gzip_enabled: bool,     # CSV only
        csv_sep: str = ",",
        csv_header_each: bool = False,  # header tiap part saat split CSV
        parent=None,
    ):
        super().__init__(parent)
        self.table = table
        self.out_dir = out_dir
        self.base_name = base_name
        self.fmt = fmt
        self.rows_per_chunk = max(1, int(rows_per_chunk))
        self.split_files = bool(split_files)
        self.gzip_enabled = bool(gzip_enabled)
        self.csv_sep = csv_sep
        self.csv_header_each = bool(csv_header_each)

    # ---------- small helpers ----------
    def _ensure_dir(self, p: str):
        if not os.path.isdir(p):
            os.makedirs(p, exist_ok=True)

    def _csv_target(self, part_index: int, total_parts: int) -> str:
        ext = ".csv"
        if self.gzip_enabled:
            ext += ".gz"
        if self.split_files:
            return os.path.join(self.out_dir, f"{self.base_name}_{part_index+1:04d}-of-{total_parts:04d}{ext}")
        else:
            return os.path.join(self.out_dir, f"{self.base_name}{ext}")

    def _parquet_target(self, part_index: int, total_parts: int) -> str:
        ext = ".parquet"
        if self.split_files:
            return os.path.join(self.out_dir, f"{self.base_name}_{part_index+1:04d}-of-{total_parts:04d}{ext}")
        else:
            return os.path.join(self.out_dir, f"{self.base_name}{ext}")

    # ---------- CSV ----------
    def _save_as_csv(self):
        n = len(self.table)
        total_chunks = math.ceil(n / self.rows_per_chunk)
        self.progress_total.emit(n)
        written = 0
        self._ensure_dir(self.out_dir)

        if not self.split_files:
            target = self._csv_target(0, total_chunks)
            if os.path.exists(target):
                os.remove(target)

            if self.gzip_enabled:
                fobj = gzip.open(target, "wt", newline="")
            else:
                fobj = open(target, "w", newline="", encoding="utf-8")

            try:
                header_written = False
                for i in range(total_chunks):
                    if self.isInterruptionRequested():
                        self.failed.emit("Dibatalkan pengguna.")
                        return
                    start = i * self.rows_per_chunk
                    stop = min(n, start + self.rows_per_chunk)
                    df = table_to_frame(self.table[start:stop], include_metas=True)
                    df.to_csv(
                        fobj,
                        sep=self.csv_sep,
                        header=(not header_written),
                        index=False,
                        lineterminator="\n",  # kompatibel untuk pandas<1.5
                    )
                    header_written = True
                    written += len(df)
                    self.progress_value.emit(written)
                    self.status.emit(f"Tulis CSV: chunk {i+1}/{total_chunks} ({written}/{n})")
            finally:
                try:
                    fobj.close()
                except Exception:
                    pass

            self.finished_ok.emit(f"Selesai: {target}")
            return

        # split per file
        for i in range(total_chunks):
            if self.isInterruptionRequested():
                self.failed.emit("Dibatalkan pengguna.")
                return
            start = i * self.rows_per_chunk
            stop = min(n, start + self.rows_per_chunk)
            df = table_to_frame(self.table[start:stop], include_metas=True)
            target = self._csv_target(i, total_chunks)
            if self.gzip_enabled:
                with gzip.open(target, "wt", newline="") as f:
                    df.to_csv(
                        f,
                        sep=self.csv_sep,
                        header=True if self.csv_header_each else (i == 0),
                        index=False,
                        lineterminator="\n",
                    )
            else:
                df.to_csv(
                    target,
                    sep=self.csv_sep,
                    header=True if self.csv_header_each else (i == 0),
                    index=False,
                    lineterminator="\n",
                    encoding="utf-8",
                )
            written += len(df)
            self.progress_value.emit(written)
            self.status.emit(f"Tulis CSV: part {i+1}/{total_chunks} → {os.path.basename(target)}")

        self.finished_ok.emit(f"Selesai: {total_chunks} file CSV di {self.out_dir}")

    # ---------- Parquet ----------
    def _save_as_parquet(self):
        if not HAS_PARQUET:
            self.failed.emit("pyarrow belum terpasang. Install: pip install pyarrow")
            return

        n = len(self.table)
        total_chunks = math.ceil(n / self.rows_per_chunk)
        self.progress_total.emit(n)
        written = 0
        self._ensure_dir(self.out_dir)

        if not self.split_files:
            target = self._parquet_target(0, total_chunks)
            if os.path.exists(target):
                os.remove(target)

            writer = None
            try:
                for i in range(total_chunks):
                    if self.isInterruptionRequested():
                        self.failed.emit("Dibatalkan pengguna.")
                        return
                    start = i * self.rows_per_chunk
                    stop = min(n, start + self.rows_per_chunk)
                    df = table_to_frame(self.table[start:stop], include_metas=True)
                    table_pa = pa.Table.from_pandas(df, preserve_index=False)
                    if writer is None:
                        writer = pq.ParquetWriter(target, table_pa.schema, compression="snappy")
                    writer.write_table(table_pa)
                    written += len(df)
                    self.progress_value.emit(written)
                    self.status.emit(f"Tulis Parquet: chunk {i+1}/{total_chunks} ({written}/{n})")
            finally:
                try:
                    if writer is not None:
                        writer.close()
                except Exception:
                    pass

            self.finished_ok.emit(f"Selesai: {target}")
            return

        # split per file
        for i in range(total_chunks):
            if self.isInterruptionRequested():
                self.failed.emit("Dibatalkan pengguna.")
                return
            start = i * self.rows_per_chunk
            stop = min(n, start + self.rows_per_chunk)
            df = table_to_frame(self.table[start:stop], include_metas=True)
            target = self._parquet_target(i, total_chunks)
            pq.write_table(pa.Table.from_pandas(df, preserve_index=False), target, compression="snappy")
            written += len(df)
            self.progress_value.emit(written)
            self.status.emit(f"Tulis Parquet: part {i+1}/{total_chunks} → {os.path.basename(target)}")

        self.finished_ok.emit(f"Selesai: {total_chunks} file Parquet di {self.out_dir}")

    # ---------- Excel (xlsx) ----------
    def _save_as_excel(self):
        if EXCEL_ENGINE is None:
            self.failed.emit("Engine Excel tidak tersedia. Install salah satu: xlsxwriter atau openpyxl")
            return

        n = len(self.table)
        total_chunks = math.ceil(n / self.rows_per_chunk)
        self.progress_total.emit(n)
        written = 0
        self._ensure_dir(self.out_dir)

        EXCEL_MAX_ROWS = 1_048_576  # limit Excel per sheet (termasuk header)
        SHEET_BASE = "Sheet"

        if self.split_files:
            # setiap chunk jadi file excel baru
            for i in range(total_chunks):
                if self.isInterruptionRequested():
                    self.failed.emit("Dibatalkan pengguna.")
                    return
                start = i * self.rows_per_chunk
                stop = min(n, start + self.rows_per_chunk)
                df = table_to_frame(self.table[start:stop], include_metas=True)
                target = os.path.join(self.out_dir, f"{self.base_name}_{i+1:04d}-of-{total_chunks:04d}.xlsx")
                with pd.ExcelWriter(target, engine=EXCEL_ENGINE) as writer:
                    df.to_excel(writer, index=False, sheet_name=f"{SHEET_BASE}1")
                written += len(df)
                self.progress_value.emit(written)
                self.status.emit(f"Tulis Excel: file {i+1}/{total_chunks} → {os.path.basename(target)}")

            self.finished_ok.emit(f"Selesai: {total_chunks} file Excel di {self.out_dir}")
            return

        # single file: auto multi-sheet kalau melewati limit
        target = os.path.join(self.out_dir, f"{self.base_name}.xlsx")
        if os.path.exists(target):
            os.remove(target)

        with pd.ExcelWriter(target, engine=EXCEL_ENGINE) as writer:
            sheet_idx = 1
            curr_row = 0  # baris berikutnya untuk ditulis pada sheet aktif (0-based, 0=header)
            max_data_rows_per_sheet = EXCEL_MAX_ROWS - 1  # 1 baris untuk header

            # siapkan sheet pertama + header kolom
            def _ensure_sheet_header():
                nonlocal sheet_idx, curr_row
                if curr_row == 0:
                    sheet_name = f"{SHEET_BASE}{sheet_idx}"
                    # tulis header kosong agar kolom tercipta
                    df_head = table_to_frame(self.table[0:0], include_metas=True)
                    df_head.to_excel(writer, index=False, startrow=0, sheet_name=sheet_name)
                    curr_row = 1  # data mulai baris 1

            _ensure_sheet_header()

            while written < n:
                if self.isInterruptionRequested():
                    self.failed.emit("Dibatalkan pengguna.")
                    return

                start = written
                stop = min(n, start + self.rows_per_chunk)
                df = table_to_frame(self.table[start:stop], include_metas=True)

                # berapa sisa ruang data di sheet ini?
                remain = max_data_rows_per_sheet - (curr_row - 1)
                if remain <= 0:
                    # sheet penuh → sheet berikutnya
                    sheet_idx += 1
                    curr_row = 0
                    _ensure_sheet_header()
                    remain = max_data_rows_per_sheet

                # potong df agar pas di sheet
                take = min(len(df), remain)
                if take > 0:
                    df_head = df.iloc[:take]
                    df_head.to_excel(writer, index=False, header=False,
                                     startrow=curr_row, sheet_name=f"{SHEET_BASE}{sheet_idx}")
                    curr_row += take
                    written += take
                    self.progress_value.emit(written)
                    self.status.emit(f"Tulis Excel: sheet {sheet_idx} (row={curr_row-1}) total {written}/{n}")

                # sisa baris (kalau chunk lebih besar dari kapasitas sheet)
                remain_df = df.iloc[take:]
                while len(remain_df) > 0:
                    sheet_idx += 1
                    curr_row = 0
                    _ensure_sheet_header()
                    remain = max_data_rows_per_sheet
                    take2 = min(len(remain_df), remain)
                    part = remain_df.iloc[:take2]
                    part.to_excel(writer, index=False, header=False,
                                  startrow=curr_row, sheet_name=f"{SHEET_BASE}{sheet_idx}")
                    curr_row += take2
                    written += take2
                    self.progress_value.emit(written)
                    self.status.emit(f"Tulis Excel: sheet {sheet_idx} (row={curr_row-1}) total {written}/{n}")
                    remain_df = remain_df.iloc[take2:]

        self.finished_ok.emit(f"Selesai: {target}")

    # ---------- dispatcher ----------
    def run(self):
        try:
            if self.table is None:
                self.failed.emit("Tidak ada data.")
                return
            n = len(self.table)
            if n == 0:
                self.failed.emit("Tabel kosong.")
                return

            if self.fmt == "CSV":
                self._save_as_csv()
            elif self.fmt == "Parquet":
                self._save_as_parquet()
            elif self.fmt == "Excel (xlsx)":
                self._save_as_excel()
            else:
                self.failed.emit(f"Format tidak didukung: {self.fmt}")
        except Exception as e:
            self.failed.emit(str(e))


# ================== Widget ==================
class OWHDataSaveBig(OWWidget):
    name = "Save Big Data"
    id = "datahelpers-save-big"
    description = "Simpan data besar ke CSV/Parquet/Excel dengan chunking, split, dan progress."
    icon = "icons/save_data.png"
    priority = 12
    want_main_area = False

    class Inputs:
        Data = Input("Data", Table)

    # Settings
    out_dir: str = Setting(os.path.expanduser("~/Downloads"))
    base_name: str = Setting("dataset")
    fmt: str = Setting("CSV")  # "CSV" | "Parquet" | "Excel (xlsx)"
    rows_per_chunk: int = Setting(100_000)
    split_files: bool = Setting(False)
    gzip_enabled: bool = Setting(False)   # CSV only
    csv_sep: str = Setting(",")
    csv_header_each: bool = Setting(False)

    class Error(OWWidget.Error):
        no_data = Msg("Tidak ada data yang masuk.")
        save_failed = Msg("Gagal menyimpan: {}")
    class Info(OWWidget.Information):
        done = Msg("{}")
        rows = Msg("Baris: {}")
        status = Msg("{}")
        hint = Msg("Gunakan Parquet untuk cepat & hemat disk; Excel untuk berbagi.")
    class Warning(OWWidget.Warning):
        parquet_missing = Msg("pyarrow belum terpasang; Parquet tidak tersedia.")
        excel_missing = Msg("xlsxwriter/openpyxl belum terpasang; Excel tidak tersedia.")

    def __init__(self):
        super().__init__()

        # --- Input info ---
        ibox = gui.widgetBox(self.controlArea, "Input")
        self.lbl_rows = QtWidgets.QLabel("Baris: -")
        ibox.layout().addWidget(self.lbl_rows)
        self.Info.hint()

        # --- Target ---
        tbox = gui.widgetBox(self.controlArea, "Target")
        hb = QtWidgets.QHBoxLayout()
        self.edit_dir = QtWidgets.QLineEdit(self.out_dir)
        btn_browse = QtWidgets.QPushButton("Browse…")
        btn_browse.clicked.connect(self._pick_dir)
        hb.addWidget(QtWidgets.QLabel("Folder:"))
        hb.addWidget(self.edit_dir)
        hb.addWidget(btn_browse)
        tbox.layout().addLayout(hb)

        gui.lineEdit(tbox, self, "base_name", label="Base name:")
        gui.comboBox(
            tbox, self, "fmt",
            items=["CSV", "Parquet", "Excel (xlsx)"],
            label="Format:", sendSelectedValue=True, callback=self._on_fmt_changed
        )

        # --- Options ---
        obox = gui.widgetBox(self.controlArea, "Opsi")
        gui.spin(obox, self, "rows_per_chunk", 1_000, 10_000_000, step=10_000, label="Rows per chunk:")
        self.chk_split = gui.checkBox(obox, self, "split_files", "Split ke multi-file per chunk")
        self.chk_gzip = gui.checkBox(obox, self, "gzip_enabled", "Gzip (CSV)")
        self.edit_sep = gui.lineEdit(obox, self, "csv_sep", label="Separator (CSV):")
        self.chk_header_each = gui.checkBox(obox, self, "csv_header_each", "Header tiap file (split CSV)")

        # --- Run & Progress ---
        rbox = gui.widgetBox(self.controlArea, "Run")
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_save.clicked.connect(self._save)
        rbox.layout().addWidget(self.btn_save)

        pbox = gui.widgetBox(self.controlArea, "Progress")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        pbox.layout().addWidget(self.progress)

        # state
        self._data: Optional[Table] = None
        self._worker: Optional[SaveWorker] = None

        self._on_fmt_changed()

    # ===== Inputs =====
    @Inputs.Data
    def set_data(self, data: Optional[Table]):
        self._data = data
        self.Error.clear(); self.Info.clear(); self.Warning.clear()
        if data is None:
            self.lbl_rows.setText("Baris: -")
            self.Error.no_data()
            return
        n = len(data)
        self.lbl_rows.setText(f"Baris: {n}")
        self.Info.rows(n)

        if self.fmt == "Parquet" and not HAS_PARQUET:
            self.Warning.parquet_missing()
        if self.fmt == "Excel (xlsx)" and EXCEL_ENGINE is None:
            self.Warning.excel_missing()

    # ===== UI helpers =====
    def _pick_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Pilih Folder Output", self.edit_dir.text() or os.path.expanduser("~")
        )
        if d:
            self.edit_dir.setText(d)
            self.out_dir = d

    def _on_fmt_changed(self):
        is_csv = (self.fmt == "CSV")
        # enable/disable opsi khusus CSV
        self.chk_gzip.setEnabled(is_csv)
        self.edit_sep.setEnabled(is_csv)
        self.chk_header_each.setEnabled(is_csv)
        if not is_csv:
            self.gzip_enabled = False

        # warning ketergantungan
        self.Warning.clear()
        if self.fmt == "Parquet" and not HAS_PARQUET:
            self.Warning.parquet_missing()
        if self.fmt == "Excel (xlsx)" and EXCEL_ENGINE is None:
            self.Warning.excel_missing()

    def _toggle_busy(self, busy: bool):
        self.btn_save.setDisabled(busy)
        self.progress.setRange(0, 100)

    def _safe_kill_worker(self):
        w = getattr(self, "_worker", None)
        if not w:
            return
        try:
            try: w.status.disconnect(self._on_status)
            except Exception: pass
            try: w.progress_total.disconnect(self._on_total)
            except Exception: pass
            try: w.progress_value.disconnect(self._on_value)
            except Exception: pass
            try: w.finished_ok.disconnect(self._on_done)
            except Exception: pass
            try: w.failed.disconnect(self._on_failed)
            except Exception: pass
            try: w.finished.disconnect(self._on_finish)
            except Exception: pass
            if hasattr(w, "isRunning"):
                try:
                    if w.isRunning():
                        getattr(w, "requestInterruption", lambda: None)()
                        w.quit(); w.wait(2000)
                except RuntimeError:
                    pass
            try: w.setParent(None)
            except Exception: pass
            try: w.deleteLater()
            except Exception: pass
        finally:
            self._worker = None

    # ===== Run save =====
    def _save(self):
        self.Error.clear(); self.Info.clear(); self.Warning.clear()
        if self._data is None or len(self._data) == 0:
            self.Error.no_data()
            return

        self.out_dir = self.edit_dir.text().strip() or self.out_dir
        if not self.out_dir:
            self.Error.save_failed("Folder output kosong.")
            return
        if not self.base_name.strip():
            self.Error.save_failed("Base name kosong.")
            return

        # start worker
        self._toggle_busy(True)
        self.progress.setValue(0)

        self._safe_kill_worker()
        self._worker = SaveWorker(
            table=self._data,
            out_dir=self.out_dir,
            base_name=self.base_name.strip(),
            fmt=self.fmt,
            rows_per_chunk=self.rows_per_chunk,
            split_files=self.split_files,
            gzip_enabled=self.gzip_enabled,
            csv_sep=self.csv_sep or ",",
            csv_header_each=self.csv_header_each,
            parent=self
        )
        self._worker.status.connect(self._on_status)
        self._worker.progress_total.connect(self._on_total)
        self._worker.progress_value.connect(self._on_value)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_finish)
        self._worker.start()

    # ===== Callbacks =====
    def _on_status(self, text: str):
        self.Info.status(text)

    def _on_total(self, total: int):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

    def _on_value(self, value: int):
        if self._data is None or len(self._data) == 0:
            return
        pct = int((value / max(1, len(self._data))) * 100)
        self.progress.setValue(min(100, max(0, pct)))

    def _on_done(self, msg: str):
        self.progress.setValue(100)
        self.Info.done(msg)

    def _on_failed(self, err: str):
        self.progress.setValue(0)
        self.Error.save_failed(err)

    def _on_finish(self):
        self._toggle_busy(False)
        self._safe_kill_worker()
