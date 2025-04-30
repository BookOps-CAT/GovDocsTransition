import click


@click.group()
def cli() -> None:
    pass

@cli.command()
def test_cli():
    """Prints a greeting."""
    click.echo("Hello, World!")


def main_cli() -> None:
    cli()