import importlib.util
import subprocess
import sys
from typing import Tuple, Optional

DRIVER_MATRIX = {
    "PostgreSQL": ("psycopg2", "psycopg2-binary"),
    "MySQL (PyMySQL)": ("pymysql", "pymysql"),
    "SQLite": ("sqlite3", None),
    "SQL Server (pyodbc)": ("pyodbc", "pyodbc"),  # butuh ODBC driver OS
    "ClickHouse": ("clickhouse_connect", "clickhouse-connect"),
}

def is_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None

def pip_install(pkg: Optional[str]) -> Tuple[bool, str]:
    if not pkg:
        return True, "No pip package required."
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return proc.returncode == 0, proc.stdout

def ensure_driver(db_kind: str) -> Tuple[bool, str, Optional[str]]:
    if db_kind not in DRIVER_MATRIX:
        return False, f"Unsupported DB type: {db_kind}", None
    module_name, pip_pkg = DRIVER_MATRIX[db_kind]
    if is_installed(module_name):
        return True, f"Driver {module_name} is available.", module_name
    ok, log = pip_install(pip_pkg)
    if ok and is_installed(module_name):
        return True, f"Installed {pip_pkg}.\n{log}", module_name
    return False, f"Failed installing {pip_pkg}.\n{log}", None
