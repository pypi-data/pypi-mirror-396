from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("orange3-data-helpers")
except PackageNotFoundError:
    __version__ = "0.0.1"

NAME = "Data Helpers"
DESCRIPTION = "Widget untuk koneksi DB, query, struktur, dan ekspor data besar."
BACKGROUND = "#f6612d"
ICON = "icons/addon_icon.png"

import warnings

# Suppress FutureWarning dari pandas soal downcasting .fillna
warnings.filterwarnings(
    "ignore",
    message="Downcasting object dtype arrays on .fillna",
    category=FutureWarning,
)

# Suppress UserWarning ketika pandas tidak bisa infer format datetime
warnings.filterwarnings(
    "ignore",
    message="Could not infer format, so each element will be parsed individually",
    category=UserWarning,
)



