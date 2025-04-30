import click


@click.group()
def cli() -> None:
    pass

@cli.command()
def test_cli():
    """Prints a greeting."""
    click.echo("Success!")


def main_cli() -> None:
    cli()