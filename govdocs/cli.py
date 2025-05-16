from pathlib import Path

import click


from govdocs.marc import extract_controlnos
from govdocs.analysis import (
    get_eres_df,
    produce_safe2delete_dups_report,
    produce_unsafe2delete_dups_report,
    produce_overwrite_review_needed_report,
)


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
def test_cli():
    """Prints a greeting."""
    click.echo("Success!")


def cli() -> None:
    main_cli()
