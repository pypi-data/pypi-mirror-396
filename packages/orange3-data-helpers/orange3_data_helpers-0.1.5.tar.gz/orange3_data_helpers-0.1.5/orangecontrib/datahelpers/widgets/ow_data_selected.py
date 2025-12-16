# orangecontrib/datahelpers/widgets/ow_selected_data.py

from AnyQt import QtWidgets
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget import gui
from orangewidget.settings import Setting
from Orange.data import Table

from typing import List, Dict, Any, Optional


# ================== Konfigurasi jumlah slot maksimum ==================
# User akan memilih sendiri berapa slot aktif di dalam rentang 1..MAX_SLOTS.
MAX_SLOTS = 10


class _SourceItem:
    """Representasi satu sumber data (query loader / input lain)."""

    def __init__(
        self,
        key: str,
        name: str,
        table: Table,
        rows: Optional[int] = None,
        description: str = "",
        source: str = "",
        kind: str = "unknown",
    ):
        self.key = key                  # unique id internal
        self.name = name                # nama sumber (file/query)
        self.table = table              # Orange Table
        self.rows = rows if rows is not None else len(table)
        self.description = description  # deskripsi opsional
        self.source = source            # path/file asal bila ada
        self.kind = kind                # "query_loader" / "input_data"


class OWHDataSelected(OWWidget):
    """
    Selected Data:
    - Input:
        * Results: list[dict] dari Query Loader (banyak query)
        * Data: Table (multiple=True) dari widget lain (File, dsb.)
    - Menampilkan semua sumber dalam satu daftar.
    - Menyediakan hingga MAX_SLOTS slot output (Data 1..Data N).
    - User menentukan berapa slot yang aktif melalui spinbox.
    - Tiap slot aktif memilih satu sumber sebagai output.
    """

    name = "Selected Data"
    id = "datahelpers-selected-data"
    description = (
        "Memilih sumber data (hasil query atau file) dan memetakan ke beberapa output "
        "untuk widget seperti Join Data, Concatenate, dll."
    )
    icon = "icons/select_row.png"
    priority = 14
    want_main_area = False

    # ====== IO ======
    class Inputs:
        Results = Input("Results", object, auto_summary=False)
        Data = Input("Data", Table, multiple=True, auto_summary=False)

    class Outputs:
        # Output Data1..DataN akan diisi di akhir file (di luar kelas).
        pass

    # ====== Settings ======
    # Berapa slot yang aktif (1..MAX_SLOTS), user bisa ubah di UI
    active_slots: int = Setting(3)

    # Indeks sumber yang dipilih tiap slot, panjang list = MAX_SLOTS
    slot_indices: List[int] = Setting(list(range(MAX_SLOTS)))

    class Error(OWWidget.Error):
        no_sources = Msg("Belum ada sumber data yang tersedia.")
    class Info(OWWidget.Information):
        status = Msg("{}")

    # ====== init ======
    def __init__(self):
        super().__init__()

        # sumber data dari Query Loader & input lain
        self._result_sources: List[_SourceItem] = []
        self._data_sources: Dict[Any, _SourceItem] = {}  # key = input id
        self._sources: List[_SourceItem] = []            # gabungan keduanya

        # Normalisasi setting agar konsisten dengan MAX_SLOTS
        self._normalize_settings()
        self._normalize_active_slots()

        # --- daftar semua sumber ---
        box_list = gui.widgetBox(self.controlArea, "Sumber Data")
        self.list_view = QtWidgets.QListWidget()
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        box_list.layout().addWidget(self.list_view)

        # --- pengaturan jumlah slot aktif ---
        box_cfg = gui.widgetBox(self.controlArea, "Pengaturan Slot")
        self.spin_slots = gui.spin(
            box_cfg, self, "active_slots",
            1, MAX_SLOTS, step=1,
            label="Jumlah data aktif:",
            callback=self._on_active_slots_changed,
        )

        # --- konfigurasi slot output ---
        box_slots = gui.widgetBox(self.controlArea, "Konfigurasi Data Output")

        # meta untuk tiap slot: {index, slot_no, group_box, combo}
        self._slots_meta: List[Dict[str, Any]] = []

        for idx in range(MAX_SLOTS):
            slot_no = idx + 1
            group = gui.widgetBox(box_slots, f"Data {slot_no}")
            form = QtWidgets.QFormLayout()
            group.layout().addLayout(form)

            # ComboBox untuk pilih sumber
            combo = QtWidgets.QComboBox()
            combo.setMinimumWidth(220)
            combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
            form.addRow("Sumber:", combo)

            meta = {
                "index": idx,
                "slot_no": slot_no,
                "group": group,
                "combo": combo,
            }
            self._slots_meta.append(meta)

            # connect perubahan combo
            def _make_combo_cb(i: int):
                def _on_combo_changed(new_idx: int):
                    if 0 <= i < len(self.slot_indices):
                        self.slot_indices[i] = new_idx
                        self._update_outputs_and_status()
                return _on_combo_changed

            combo.currentIndexChanged.connect(_make_combo_cb(idx))

        # Atur visibilitas awal sesuai active_slots
        self._apply_active_slots_visibility()

        self.Info.status("Menunggu data dari Query Loader atau input lain…")

    # ====== helper setting ======
    def _normalize_settings(self):
        """Pastikan slot_indices panjangnya = MAX_SLOTS."""
        inds = list(self.slot_indices)
        if len(inds) < MAX_SLOTS:
            inds += list(range(len(inds), MAX_SLOTS))
        elif len(inds) > MAX_SLOTS:
            inds = inds[:MAX_SLOTS]
        self.slot_indices = inds

    def _normalize_active_slots(self):
        """Clamp active_slots ke range 1..MAX_SLOTS."""
        if self.active_slots < 1:
            self.active_slots = 1
        elif self.active_slots > MAX_SLOTS:
            self.active_slots = MAX_SLOTS

    # ====== Input handlers ======
    @Inputs.Results
    def set_results(self, results: Optional[object]):
        """Dipanggil ketika Query Loader mengirim / mengubah Results."""
        self._result_sources.clear()

        if results and isinstance(results, list):
            for i, item in enumerate(results):
                if not isinstance(item, dict):
                    continue
                tbl = item.get("table")
                if not isinstance(tbl, Table):
                    continue
                name = item.get("name") or f"Query {i+1}"
                rows = item.get("rows")
                desc = item.get("description") or ""
                src = item.get("source") or ""
                key = f"result:{i}"
                self._result_sources.append(
                    _SourceItem(
                        key=key,
                        name=name,
                        table=tbl,
                        rows=rows,
                        description=desc,
                        source=src,
                        kind="query_loader",
                    )
                )

        self._rebuild_sources()

    @Inputs.Data
    def set_data(self, data: Optional[Table], id: Any = None):
        """Dipanggil untuk setiap connection dari widget lain (multiple=True)."""
        if id is None:
            id = "default"

        if data is None:
            # koneksi diputus → hapus sumber terkait
            if id in self._data_sources:
                del self._data_sources[id]
            self._rebuild_sources()
            return

        base_name = getattr(data, "name", None) or f"Input {id}"
        key = f"input:{id}"
        self._data_sources[id] = _SourceItem(
            key=key,
            name=base_name,
            table=data,
            rows=len(data),
            description="",
            source="(Input Data)",
            kind="input_data",
        )
        self._rebuild_sources()

    # ====== event: ubah jumlah slot aktif ======
    def _on_active_slots_changed(self):
        self._normalize_active_slots()
        self._apply_active_slots_visibility()
        self._update_outputs_and_status()

    def _apply_active_slots_visibility(self):
        """Tampilkan hanya slot 1..active_slots, sisanya disembunyikan."""
        for i, meta in enumerate(self._slots_meta):
            group: QtWidgets.QGroupBox = meta["group"]
            visible = (i < self.active_slots)
            group.setVisible(visible)

    # ====== rebuild & UI update ======
    def _rebuild_sources(self):
        """Gabungkan semua sumber, update UI & output slot."""
        self._sources = list(self._result_sources) + list(self._data_sources.values())

        # update list view
        self.list_view.clear()
        for src in self._sources:
            text = f"{src.name}  —  ({src.rows} rows)"
            item = QtWidgets.QListWidgetItem(text)
            tip_parts = []
            if src.description:
                tip_parts.append(src.description)
            if src.source:
                tip_parts.append(str(src.source))
            if src.kind == "input_data":
                tip_parts.append("[dari input Data]")
            elif src.kind == "query_loader":
                tip_parts.append("[dari Query Loader]")
            if tip_parts:
                item.setToolTip("\n".join(tip_parts))
            self.list_view.addItem(item)

        # update isi combo
        labels = [f"{s.name} ({s.rows} rows)" for s in self._sources]
        for meta in self._slots_meta:
            combo: QtWidgets.QComboBox = meta["combo"]
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(labels)
            combo.blockSignals(False)

        if not self._sources:
            self.Error.no_sources()
            # semua output None
            self._send_outputs([None] * MAX_SLOTS)
            self.Info.status("Belum ada sumber data.")
            return
        else:
            self.Error.clear()

        # normalisasi index slot terhadap jumlah sumber
        self._normalize_slot_indices_against_sources()

        # set current index combo sesuai slot_indices
        for meta in self._slots_meta:
            i = meta["index"]
            combo: QtWidgets.QComboBox = meta["combo"]
            idx_val = self.slot_indices[i] if 0 <= i < len(self.slot_indices) else 0
            if 0 <= idx_val < len(self._sources):
                combo.setCurrentIndex(idx_val)
            elif self._sources:
                combo.setCurrentIndex(0)

        # highlight sumber yang dipakai slot pertama (kalau ada)
        idx_first = self.slot_indices[0] if self.slot_indices else 0
        if 0 <= idx_first < len(self._sources):
            self.list_view.setCurrentRow(idx_first)
        elif self._sources:
            self.list_view.setCurrentRow(0)

        self._update_outputs_and_status()

    def _normalize_slot_indices_against_sources(self):
        """Pastikan nilai slot_indices selalu di rentang sumber yang ada."""
        n = len(self._sources)
        if n <= 0:
            return

        new_inds: List[int] = []
        for i, old in enumerate(self.slot_indices):
            if 0 <= old < n:
                new_inds.append(old)
            else:
                pref = i if i < n else 0
                new_inds.append(pref)
        self.slot_indices = new_inds

    # ====== output helpers ======
    def _get_source_for_index(self, idx: int) -> Optional[_SourceItem]:
        if 0 <= idx < len(self._sources):
            return self._sources[idx]
        return None

    def _send_outputs(self, tables: List[Optional[Table]]):
        """Kirim list table panjang MAX_SLOTS ke output Data1..DataN."""
        for i in range(MAX_SLOTS):
            tbl = tables[i] if i < len(tables) else None
            out = getattr(self.Outputs, f"Data{i+1}", None)
            if out is not None:
                out.send(tbl)

    def _update_outputs_and_status(self):
        """Kirim tabel ke tiap slot dan update status info."""
        if not self._sources:
            self._send_outputs([None] * MAX_SLOTS)
            self.Info.status("Belum ada sumber data.")
            return

        tables: List[Optional[Table]] = [None] * MAX_SLOTS
        parts: List[str] = []

        for meta in self._slots_meta:
            i = meta["index"]
            slot_no = meta["slot_no"]

            if i >= self.active_slots:
                # slot di luar jumlah aktif → tetap None, tidak ikut status
                continue

            idx_src = (
                self.slot_indices[i]
                if 0 <= i < len(self.slot_indices)
                else 0
            )
            src = self._get_source_for_index(idx_src)

            if src is None:
                tables[i] = None
                parts.append(f"Data {slot_no}: -")
            else:
                tables[i] = src.table
                parts.append(f"Data {slot_no}: {src.name}")

        # kirim semua output (slot aktif berisi Table, slot non-aktif None)
        self._send_outputs(tables)

        if parts:
            self.Info.status(" | ".join(parts))
        else:
            self.Info.status("Tidak ada slot aktif.")

# ====== Buat output Data1..DataN berdasarkan MAX_SLOTS ======
for i in range(1, MAX_SLOTS + 1):
    out_name = f"Data{i}"
    title = f"Data {i}"
    default = (i == 1)
    setattr(
        OWHDataSelected.Outputs,
        out_name,
        Output(title, Table, default=default, auto_summary=False),
    )
