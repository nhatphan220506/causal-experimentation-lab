import hashlib
import urllib.request

from src.config import DATA_PATH, DATA_URL, EXPECTED_BYTES, ensure_output_dirs


def sha256(path=DATA_PATH) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    ensure_output_dirs()
    if DATA_PATH.exists() and DATA_PATH.stat().st_size == EXPECTED_BYTES:
        print(f"Dataset already present: {DATA_PATH}")
    else:
        print("Downloading the official corrected Criteo uplift dataset...")
        urllib.request.urlretrieve(DATA_URL, DATA_PATH)
    size = DATA_PATH.stat().st_size
    if size != EXPECTED_BYTES:
        raise RuntimeError(f"Unexpected file size: {size:,}; expected {EXPECTED_BYTES:,}")
    print(f"bytes={size:,}")
    print(f"sha256={sha256()}")


if __name__ == "__main__":
    main()

