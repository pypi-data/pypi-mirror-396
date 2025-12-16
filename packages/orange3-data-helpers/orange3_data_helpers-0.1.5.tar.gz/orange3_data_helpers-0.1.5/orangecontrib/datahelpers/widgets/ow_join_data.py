from AnyQt import QtWidgets
from AnyQt.QtCore import Qt
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from orangewidget import gui
from orangewidget.settings import Setting
from Orange.data import Table, Domain
from Orange.data.pandas_compat import table_to_frame, table_from_frame

from typing import Optional, List
import pandas as pd


# ------------------------------------------------------------
# Helper: ambil nama kolom dari Orange Table
# ------------------------------------------------------------
def _column_names(table: Optional[Table]) -> List[str]:
    """
    Ambil daftar nama kolom dari Orange Table (features, class_vars, metas).
    """
    if table is None:
        return []
    dom = table.domain
    cols = []
    for var in list(dom.attributes) + list(dom.class_vars) + list(dom.metas):
        cols.append(var.name)
    # hilangkan duplikat dengan urutan terjaga
    seen = set()
    uniq = []
    for c in cols:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


# ------------------------------------------------------------
# Widget: Join Data
# ------------------------------------------------------------
class OWDataJoin(OWWidget):
    """
    Join dua Table Orange menggunakan pandas (inner/left/right/outer),
    mendukung multi-key join dengan pasangan key eksplisit:
        (left_col1 ↔ right_col1), (left_col2 ↔ right_col2), dst.
    """

    name = "Join Data"
    id = "datahelpers-join-data"
    description = "Menggabungkan dua tabel (left/right/inner/outer join) berbasis kolom kunci."
    icon = "icons/join_data.svg"   # siapkan icon sendiri
    priority = 13
    want_main_area = False

    class Inputs:
        Left = Input("Left Data", Table)
        Right = Input("Right Data", Table)

    class Outputs:
        Data = Output("Data", Table)

    # ----- settings disimpan di workflow -----
    join_type: str = Setting("inner")       # "inner", "left", "right", "outer"
    suffix_left: str = Setting("_x")
    suffix_right: str = Setting("_y")
    auto_commit: bool = Setting(True)
    # daftar pasangan key, disimpan sebagai string "left_col|right_col"
    key_pairs: list = Setting([])

    class Error(OWWidget.Error):
        no_left = Msg("Data kiri belum dihubungkan.")
        no_right = Msg("Data kanan belum dihubungkan.")
        no_key = Msg("Kolom key join belum dipilih.")
        join_failed = Msg("Gagal melakukan join: {}")

    class Info(OWWidget.Information):
        left_rows = Msg("Left: {} baris, {} kolom.")
        right_rows = Msg("Right: {} baris, {} kolom.")
        out_rows = Msg("Output: {} baris, {} kolom.")

    class Warning(OWWidget.Warning):
        empty_result = Msg("Hasil join kosong (0 baris).")

    def __init__(self):
        super().__init__()

        # state data
        self._left: Optional[Table] = None
        self._right: Optional[Table] = None

        # ------------------------------------------------
        # UI: Input info
        # ------------------------------------------------
        box_in = gui.widgetBox(self.controlArea, "Input")
        self.lbl_left = QtWidgets.QLabel("Left: -")
        self.lbl_right = QtWidgets.QLabel("Right: -")
        box_in.layout().addWidget(self.lbl_left)
        box_in.layout().addWidget(self.lbl_right)

        # ------------------------------------------------
        # UI: Pengaturan join
        # ------------------------------------------------
        box_join = gui.widgetBox(self.controlArea, "Pengaturan Join")

        # tipe join
        gui.comboBox(
            box_join, self, "join_type",
            label="Tipe join:",
            items=["inner", "left", "right", "outer"],
            sendSelectedValue=True,
            callback=self._on_param_changed,
        )

        # ---- Key pair editor ----
        pair_box = gui.widgetBox(box_join, "Key Pairs")

        hl_top = QtWidgets.QHBoxLayout()
        pair_box.layout().addLayout(hl_top)

        # combo left
        v_left = QtWidgets.QVBoxLayout()
        hl_top.addLayout(v_left)
        v_left.addWidget(QtWidgets.QLabel("Left column:"))
        self.cb_left_key = QtWidgets.QComboBox()
        v_left.addWidget(self.cb_left_key)

        # combo right
        v_right = QtWidgets.QVBoxLayout()
        hl_top.addLayout(v_right)
        v_right.addWidget(QtWidgets.QLabel("Right column:"))
        self.cb_right_key = QtWidgets.QComboBox()
        v_right.addWidget(self.cb_right_key)

        # tombol add/remove pair
        btns = QtWidgets.QVBoxLayout()
        hl_top.addLayout(btns)
        self.btn_add_pair = QtWidgets.QPushButton("Add pair")
        self.btn_add_pair.clicked.connect(self._on_add_pair)
        btns.addWidget(self.btn_add_pair)

        self.btn_remove_pair = QtWidgets.QPushButton("Remove selected")
        self.btn_remove_pair.clicked.connect(self._on_remove_pair)
        btns.addWidget(self.btn_remove_pair)

        btn_clear = QtWidgets.QPushButton("Clear all")
        btn_clear.clicked.connect(self._on_clear_pairs)
        btns.addWidget(btn_clear)

        btns.addStretch(1)

        # list pasangan
        self.lst_pairs = QtWidgets.QListWidget()
        pair_box.layout().addWidget(self.lst_pairs)

        # ------------------------------------------------
        # UI: Penanganan kolom bentrok
        # ------------------------------------------------
        box_suf = gui.widgetBox(self.controlArea, "Penanganan Kolom Bentrok")
        gui.lineEdit(box_suf, self, "suffix_left",
                     label="Suffix kolom dari Left:", callback=self._on_param_changed)
        gui.lineEdit(box_suf, self, "suffix_right",
                     label="Suffix kolom dari Right:", callback=self._on_param_changed)

        # ------------------------------------------------
        # Auto-commit / Apply
        # ------------------------------------------------
        box_run = gui.widgetBox(self.controlArea, "Run")
        gui.auto_commit(
            box_run, self, "auto_commit", "Apply",
            checkbox_label="Auto-commit",
            commit=self.commit
        )

        # setelah semua siap, refresh pilihan kolom/pairs (jika ada setting lama)
        self._refresh_key_lists()

    # ====================== Inputs ======================

    @Inputs.Left
    def set_left(self, data: Optional[Table]):
        self._left = data
        self._update_input_info()
        self._refresh_key_lists()
        self._maybe_commit()

    @Inputs.Right
    def set_right(self, data: Optional[Table]):
        self._right = data
        self._update_input_info()
        self._refresh_key_lists()
        self._maybe_commit()

    # ====================== UI helpers ======================

    def _update_input_info(self):
        self.Error.clear()
        self.Info.clear()
        self.Warning.clear()

        if self._left is None:
            self.lbl_left.setText("Left: (tidak ada data)")
        else:
            dom = self._left.domain
            ncols = len(dom.attributes) + len(dom.class_vars) + len(dom.metas)
            self.lbl_left.setText(f"Left: {len(self._left)} baris, {ncols} kolom")
            self.Info.left_rows(len(self._left), ncols)

        if self._right is None:
            self.lbl_right.setText("Right: (tidak ada data)")
        else:
            dom = self._right.domain
            ncols = len(dom.attributes) + len(dom.class_vars) + len(dom.metas)
            self.lbl_right.setText(f"Right: {len(self._right)} baris, {ncols} kolom")
            self.Info.right_rows(len(self._right), ncols)

    def _refresh_key_lists(self):
        """
        Update combo left/right berdasarkan kolom di tabel input,
        lalu refresh tampilan list pasangan.
        """
        # isi combo dari kolom table
        left_cols = _column_names(self._left)
        right_cols = _column_names(self._right)

        # left combo
        self.cb_left_key.blockSignals(True)
        self.cb_left_key.clear()
        for c in left_cols:
            self.cb_left_key.addItem(c, c)
        self.cb_left_key.blockSignals(False)

        # right combo
        self.cb_right_key.blockSignals(True)
        self.cb_right_key.clear()
        for c in right_cols:
            self.cb_right_key.addItem(c, c)
        self.cb_right_key.blockSignals(False)

        # daftar pasangan
        self._refresh_pairs_view()

    def _refresh_pairs_view(self):
        self.lst_pairs.clear()
        for s in self.key_pairs:
            try:
                l, r = s.split("|", 1)
            except ValueError:
                continue
            item = QtWidgets.QListWidgetItem(f"{l}  ↔  {r}")
            item.setData(Qt.UserRole, (l, r))
            self.lst_pairs.addItem(item)

    def _on_add_pair(self):
        l = self.cb_left_key.currentData()
        r = self.cb_right_key.currentData()
        if not l or not r:
            return
        pair_str = f"{l}|{r}"
        if pair_str not in self.key_pairs:
            self.key_pairs.append(pair_str)
            self._refresh_pairs_view()
            self._on_param_changed()

    def _on_remove_pair(self):
        rows = [i.row() for i in self.lst_pairs.selectedIndexes()]
        if not rows:
            return
        for idx in sorted(rows, reverse=True):
            if 0 <= idx < len(self.key_pairs):
                self.key_pairs.pop(idx)
        self._refresh_pairs_view()
        self._on_param_changed()

    def _on_clear_pairs(self):
        if not self.key_pairs:
            return
        self.key_pairs = []
        self._refresh_pairs_view()
        self._on_param_changed()

    def _on_param_changed(self):
        self._maybe_commit()

    def _maybe_commit(self):
        if self.auto_commit:
            self.commit()

    # ====================== Core join logic ======================

    def commit(self):
        self.Error.clear()
        self.Warning.clear()
        self.Info.out_rows.clear()

        if self._left is None:
            self.Error.no_left()
            self.Outputs.Data.send(None)
            return
        if self._right is None:
            self.Error.no_right()
            self.Outputs.Data.send(None)
            return

        if not self.key_pairs:
            self.Error.no_key()
            self.Outputs.Data.send(None)
            return

        # bangun left_keys & right_keys dari pasangan
        left_keys: List[str] = []
        right_keys: List[str] = []
        for s in self.key_pairs:
            try:
                l, r = s.split("|", 1)
            except ValueError:
                continue
            left_keys.append(l)
            right_keys.append(r)

        if not left_keys or not right_keys:
            self.Error.no_key()
            self.Outputs.Data.send(None)
            return

        try:
            df_left = table_to_frame(self._left, include_metas=True)
            df_right = table_to_frame(self._right, include_metas=True)

            # pastikan semua key ada di dataframe
            for k in left_keys:
                if k not in df_left.columns:
                    raise KeyError(f"Kolom '{k}' tidak ada di Left.")
            for k in right_keys:
                if k not in df_right.columns:
                    raise KeyError(f"Kolom '{k}' tidak ada di Right.")

            # samakan dtype pasangan key (kalau beda → cast ke string)
            for lk, rk in zip(left_keys, right_keys):
                if df_left[lk].dtype != df_right[rk].dtype:
                    df_left[lk] = df_left[lk].astype(str)
                    df_right[rk] = df_right[rk].astype(str)

            # lakukan join
            df_out = pd.merge(
                df_left,
                df_right,
                how=self.join_type,
                left_on=left_keys,
                right_on=right_keys,
                suffixes=(self.suffix_left or "", self.suffix_right or ""),
            )

            if df_out.empty:
                self.Warning.empty_result()

            # kolom meta untuk info key join
            join_pairs_str = ", ".join(
                [f"{lk}={rk}" for lk, rk in zip(left_keys, right_keys)]
            )
            df_out["_join_keys"] = join_pairs_str

            out_table = table_from_frame(df_out)
            self.Outputs.Data.send(out_table)

            dom: Domain = out_table.domain
            ncols = len(dom.attributes) + len(dom.class_vars) + len(dom.metas)
            self.Info.out_rows(len(out_table), ncols)

        except Exception as e:
            self.Outputs.Data.send(None)
            self.Error.join_failed(str(e))
