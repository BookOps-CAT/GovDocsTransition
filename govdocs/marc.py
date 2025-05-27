from pathlib import Path
from typing import Generator

from pymarc import MARCReader, Record


def read_marc_file(file_path: Path) -> Generator[Record, None, None]:
    """
    Reads a MARC file and returns a list of MARC records.

    Args:
        file_path (str): Path to the MARC file.

    Returns:
        list: List of MARC records.
    """
    with open(file_path, "rb") as file:
        reader = MARCReader(file)
        for bib in reader:
            yield bib


def extract_controlnos(src_path: Path) -> Path:
    """
    Extracts OCLC control numbers from the 001 field of MARC records
    and writes them to a CSV file.

    Args:
        src_path (Path): Path to the MARC file.

    Returns:
        out_path (Path): Path to the output CSV file.
    """
    out_path = src_path.with_suffix(".csv")
    with open(out_path, "w") as out_file:
        for n, record in enumerate(read_marc_file(src_path)):
            controlno = record["001"].value().strip()
            if controlno:
                out_file.write(f"{controlno}\n")
            else:
                raise ValueError(f"Control number not found in record: {n + 1}")
    return out_path


def select_bibs_on_controlnos(controlNos_fh: Path, marc_fh: Path) -> None:
    """
    Selects MARC records based on control numbers from a CSV file
    and writes the selected records to a new MARC file.

    Args:
        controlNos_fh (Path): Path to the CSV file containing control numbers.
        marc_fh (Path): Path to the MARC file.
    """
    control_nos = set()
    with open(controlNos_fh, "r") as f:
        for line in f:
            control_nos.add(line.strip())

    with (
        open(marc_fh, "rb") as marc_file,
        open(marc_fh.with_suffix(".selected.mrc"), "ab") as out_file,
    ):
        reader = MARCReader(marc_file)
        for record in reader:
            if record["001"].value().strip() in control_nos:
                out_file.write(record.as_marc())
