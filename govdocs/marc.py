from pathlib import Path
from typing import Generator, Optional
import warnings

from pymarc import MARCReader, Record, Field, Subfield, Indicators
from bookops_marc import SierraBibReader
from bookops_marc.models import OclcNumber


def determine_material_type(record: Record) -> Optional[str]:
    """
    Determines the material type of a MARC record based on its leader.

    Args:
        record (Record): The MARC record to analyze.

    Returns:
        str: The material type.
    """
    leader = record.leader
    if leader[6] in ("a", "s", "b", "t"):
        t008 = record.get("008")
        if t008:
            if t008.data[23] == " ":
                # regular print
                return "a"
            elif t008.data[23] == "d":
                # large print
                return "d"
            elif t008.data[23] in ("a", "b", "c"):
                # microform
                return "h"
            elif t008.data[23] in ("o", "s"):
                # web resource
                return "w"
            elif t008.data[23] == "q":
                return "m"
            else:
                warnings.warn(
                    f"{record.control_number} : unknown material type 008/06 '{t008.data[23]}'"
                )
                return None
        else:
            return None
    elif leader[6] == "e":
        # map
        return "e"
    elif leader[6] == "g":
        t008 = record.get("008")
        if t008:
            if t008.data[28] == "b":
                return "o"
            elif t008.data[28] in ("i", "k", "l", "n"):
                return "k"
            elif t008.data[28] == ("v"):
                return "v"
            else:
                return None
        else:
            return None
    elif leader[6] == "k":
        # picture
        return "k"
    elif leader[6] == "o":
        # kit
        return "o"
    elif leader[6] == "m":
        # computer file
        return "m"
    else:
        warnings.warn(
            f"{record.control_number} : unknown material type leader '{leader[6]}'"
        )
        return None


def is_serial(leader: str) -> bool:
    if leader[7] in ("s", "b"):
        return True
    else:
        return False


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
        reader = SierraBibReader(marc_file, library="nypl")
        for bib in reader:
            controlNo = OclcNumber(bib.control_number).without_prefix
            if controlNo in control_nos:
                out_file.write(bib.as_marc())


def separate_mon_vs_ser(marcfile: Path) -> tuple:
    with (
        open(marcfile, "rb") as src,
        open(marcfile.with_suffix(".SERIAL.mrc"), "ab") as out_ser,
        open(marcfile.with_suffix(".MONO.mrc"), "ab") as out_mon,
    ):
        reader = MARCReader(src)
        for record in reader:
            if is_serial(record.leader):
                out_ser.write(record.as_marc())
            else:
                out_mon.write(record.as_marc())
        return src, out_ser, out_mon


def add_url_label_to_856(record: Record) -> None:
    """
    Adds a URL label in the subfield $z to the 856 field of a MARC record.

    Args:
        record (Record): The MARC record to modify.
    """
    for field in record.get_fields("856"):
        if field.indicators == Indicators("4", "0"):
            field.delete_subfield("z")
            field.add_subfield(code="z", value="Full text available via FDLP")
        elif field.indicators == Indicators("4", "1"):
            field.delete_subfield("z")
            field.add_subfield(code="z", value="Online version of the resource")


def add_call_number(record: Record, prefix: str) -> None:
    """
    Adds a call number in the 099 field to the MARC record if it is not already present.

    Args:
        record (Record): The MARC record to modify.
    """
    for field in record.get_fields("086"):
        gpo_class = field.value().strip()
        record.add_field(
            Field(
                tag="099",
                indicators=Indicators(" ", "9"),
                subfields=[Subfield(code="a", value=f"{prefix}{gpo_class}")],
            )
        )


def prep_for_sierra_load(marcfile: Path) -> Path:
    """
    Prepares MARC records for Sierra load.

    Args:
        marcfile (Path): Path to the MARC file.
    """
    out_file = marcfile.with_suffix(".SIERRA-LOAD-READY.mrc")
    with (
        open(marcfile, "rb") as src,
        open(out_file, "ab") as out,
    ):
        reader = SierraBibReader(src, library="nypl")
        for bib in reader:
            bib.normalize_oclc_control_number()
            bib.remove_unsupported_subjects()
            add_url_label_to_856(bib)
            if "ERES." in marcfile.name:
                add_url_label_to_856(bib)
                if ".new." in marcfile.name:
                    add_call_number(bib, prefix="GPO Internet ")
            elif ".new." in marcfile.name and "PRINT." in marcfile.name:
                pass  # to be implemented
            else:
                # initial load for print
                matType = determine_material_type(bib)
                if matType and matType != "a":
                    bib.add_field(
                        Field(
                            tag="949",
                            indicators=Indicators(" ", " "),
                            subfields=[Subfield(code="a", value=f"*b2={matType};")],
                        )
                    )
            out.write(bib.as_marc())
    return out_file
