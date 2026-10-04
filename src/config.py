from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
GENERATED_DIR = REPORTS_DIR / "generated"

DATA_URL = "http://go.criteo.net/criteo-research-uplift-v2.1.csv.gz"
DATA_PATH = RAW_DIR / "criteo-uplift-v2.1.csv.gz"
PARQUET_PATH = PROCESSED_DIR / "criteo-uplift-v2.1.parquet"
EXPECTED_BYTES = 311_422_618
FEATURES = [f"f{i}" for i in range(12)]
EXPECTED_TREATMENT_SHARE = 0.85
RANDOM_SEED = 220506


def ensure_output_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR, FIGURES_DIR, GENERATED_DIR):
        path.mkdir(parents=True, exist_ok=True)
