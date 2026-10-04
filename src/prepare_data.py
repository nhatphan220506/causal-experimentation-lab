import duckdb

from src.config import DATA_PATH, PARQUET_PATH, ensure_output_dirs
from src.io_utils import require_data


def main() -> None:
    ensure_output_dirs()
    require_data()
    if PARQUET_PATH.exists():
        print(f"Prepared dataset already present: {PARQUET_PATH}")
        return
    source = str(DATA_PATH).replace("'", "''")
    destination = str(PARQUET_PATH).replace("'", "''")
    conn = duckdb.connect()
    conn.execute("SET threads TO 4")
    conn.execute("SET memory_limit = '4GB'")
    conn.execute(
        f"""
        COPY (
            SELECT row_number() OVER () AS row_id, *
            FROM read_csv_auto('{source}', header=true, compression='gzip')
        ) TO '{destination}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """
    )
    rows = conn.execute(f"SELECT count(*) FROM read_parquet('{destination}')").fetchone()[0]
    print(f"prepared_rows={rows:,}; path={PARQUET_PATH}")


if __name__ == "__main__":
    main()
