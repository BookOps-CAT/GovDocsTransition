from datetime import datetime
from pathlib import Path
import zipfile


def unpack_zipfiles(delivery_dir: Path) -> list[str]:
    with zipfile.ZipFile(delivery_dir, "r") as zip_files:
        extracted_files = zip_files.namelist()
        zip_files.extractall(path=delivery_dir)
    return extracted_files


def get_directory(delivery_date: str) -> Path:
    delivery_obj = datetime.strptime(delivery_date, "%Y%m%d")
    delivery_dir = Path.cwd() / f"files/{delivery_obj:%Y-%m-%d}"
    return delivery_dir
