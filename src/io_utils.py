import json
from pathlib import Path

import duckdb

from src.config import DATA_PATH, PARQUET_PATH


def require_data() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run `python -m src.download_data` first.")


def relation_sql() -> str:
    if PARQUET_PATH.exists():
        escaped = str(PARQUET_PATH).replace("'", "''")
        return f"read_parquet('{escaped}')"
    escaped = str(DATA_PATH).replace("'", "''")
    return f"read_csv_auto('{escaped}', header=true, compression='gzip')"


def connection():
    require_data()
    conn = duckdb.connect()
    conn.execute("SET threads TO 4")
    conn.execute("SET memory_limit = '4GB'")
    return conn


def write_json(payload, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
