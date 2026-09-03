import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CHECKSUM_MANIFEST = PROJECT_ROOT / "data" / "raw_checksums.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_raw_csv_files_match_the_inspected_snapshot() -> None:
    expected = {
        Path(relative_path): checksum
        for checksum, relative_path in (
            line.split(maxsplit=1)
            for line in CHECKSUM_MANIFEST.read_text(encoding="utf-8").splitlines()
        )
    }
    actual_paths = {
        path.relative_to(PROJECT_ROOT) for path in RAW_DATA_DIR.glob("*.csv")
    }

    assert actual_paths == set(expected)
    assert {
        path: sha256(PROJECT_ROOT / path) for path in sorted(actual_paths)
    } == expected
