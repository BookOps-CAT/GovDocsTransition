from datetime import datetime
from pathlib import Path
import zipfile


def unpack_zipfiles(delivery_dir: Path) -> list[str]:
    files = [
        entry
        for entry in delivery_dir.iterdir()
        if entry.is_file() and entry.suffix == ".zip"
    ]
    extracted_files = []
    for f in files:
        with zipfile.ZipFile(f, "r") as zip_file:
            extracted_file = zip_file.namelist()
            zip_file.extractall(path=delivery_dir)
            extracted_files.extend(extracted_file)
    return extracted_files


def get_directory(delivery_date: str) -> Path:
    delivery_date_obj = datetime.strptime(delivery_date, "%Y%m%d")
    delivery_dir = Path.cwd() / f"files/{delivery_date_obj:%Y-%m-%d}"
    return delivery_dir
