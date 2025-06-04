from pathlib import Path

import click


from govdocs.marc import (
    extract_controlnos,
    select_bibs_on_controlnos,
    separate_mon_vs_ser,
)
from govdocs.analysis import (
    get_eres_df,
    produce_safe2delete_dups_report,
    produce_unsafe2delete_dups_report,
    produce_overwrite_review_needed_report,
)
from govdocs.utils import get_directory, unpack_zipfiles


@click.group()
def main_cli() -> None:
    pass


@main_cli.command()
@click.argument("src", type=click.Path(exists=True))
def get_controlnos(src: str) -> None:
    """
    Extracts OCLC control numbers from the 001 field of MARC records
    and writes them to a CSV file.

    Args:
        src (str): Path to the MARC file.
    """
    click.echo(f"Processing file: {src}...")
    src_path = Path(src)
    out = extract_controlnos(src_path)
    click.echo(f"OCLC control numbers extracted to: `{out}`.")


@main_cli.command()
@click.argument("csv_fh", type=click.Path(exists=True))
@click.argument("marc_fh", type=click.Path(exists=True))
def select_bibs(csv_fh: str, marc_fh: str) -> None:
    """
    Selects MARC records based on control numbers from a CSV file
    and writes the selected records to a new MARC file.

    Args:
        csv_fh (str): Path to the CSV file containing control numbers.
        marc_fh (str): Path to the MARC file.
    """
    controlNos_src = Path(csv_fh)
    marc_src = Path(marc_fh)
    click.echo(
        f"Selecting MARC records from {marc_src} using control numbers from "
        f"{controlNos_src}..."
    )

    select_bibs_on_controlnos(controlNos_src, marc_src)

    click.echo("MARC records selected successfully.")


@main_cli.command()
@click.argument("marc_fh", type=click.Path(exists=True))
def split_serials_and_mono(marc_fh: str):
    marcfile = Path(marc_fh)
    separate_mon_vs_ser(marcfile)
    click.echo(f"Separation of serials and monographs completed.")


@main_cli.command()
def pre_load_eres_reports() -> None:
    df = get_eres_df()
    produce_safe2delete_dups_report(df)
    produce_unsafe2delete_dups_report(df)
    produce_overwrite_review_needed_report(df)
    click.echo("Reports generated successfully.")
    click.echo(
        "See: safe2delete-dups.cvs, unsafe2delete-dups.csv, unsafe2overwrite-single.csv"
    )


@main_cli.command()
@click.argument("delivery_date", type=str)
def reconcile(delivery_date: str) -> None:
    """
    Prepares the files for a given delivery date for reconciliation with Sierra.
    New, updated, and merge records are modified accordingly. Deleted records are
    parsed to conveniently create a list in Sierra for global deletions.

    Args:
        delivery_date (str): The delivery date in YYYY-MM-DD format.
    """
    # create a list of OCLC # for deletions
    # prep new records (remove OCLC prefix, call #, etc.)
    # prep updated records (remove OCLC prefix, remove 6xx)
    # search Platform API for merged (remove OCLC prefix, remove 6xx, set matching point)
    delivery_dir = get_directory(delivery_date)
    click.echo(f"Unpacking zip files in {delivery_dir}...")
    unpacked_files = unpack_zipfiles(delivery_dir)
    click.echo(f"Unpacked files: {unpacked_files}")
    # click.echo(f"Preparing import files for delivery date: {delivery_date}...")
    # Placeholder for actual implementation
    # click.echo("Import files prepared successfully.")


@main_cli.command()
def test_cli():
    """Prints a greeting."""
    click.echo("Success!")


def cli() -> None:
    main_cli()
