"""Archive dated chip CSVs older than the newest KEEP_LATEST into a zip."""
import re
import zipfile
from pathlib import Path

KEEP_LATEST = 60
DATA_DIR = Path(__file__).resolve().parent / "data"
ARCHIVE_NAME = "history_chip_csvs.zip"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def archive_old_reports(data_dir: Path = DATA_DIR, keep: int = KEEP_LATEST) -> list[Path]:
    files = sorted(p for p in Path(data_dir).glob("*.csv") if DATE_RE.fullmatch(p.stem))
    if len(files) <= keep:
        print(f"[archive] {len(files)} dated CSVs <= {keep}, nothing to do")
        return []
    old = files[: len(files) - keep]
    archive_dir = Path(data_dir) / "archive"
    archive_dir.mkdir(exist_ok=True)
    zip_path = archive_dir / ARCHIVE_NAME
    with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as zf:
        existing = set(zf.namelist())
        for i, path in enumerate(old, 1):
            if path.name not in existing:
                zf.write(path, arcname=path.name)
            print(f"[archive] ({i}/{len(old)}) {path.name}")
    for path in old:
        path.unlink()
    print(f"[archive] archived {len(old)} files into {zip_path}")
    return old


if __name__ == "__main__":
    archive_old_reports()
