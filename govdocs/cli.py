import click


@click.group()
def main_cli() -> None:
    pass


@main_cli.command()
def test_cli():
    """Prints a greeting."""
    click.echo("Success!")


def cli() -> None:
    main_cli()
