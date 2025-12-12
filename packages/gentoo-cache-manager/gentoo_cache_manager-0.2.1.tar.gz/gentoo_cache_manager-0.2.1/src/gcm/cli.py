import click

import gcm
from .commands import COMMANDS


@click.group(help=gcm.__name__, commands=COMMANDS)
@click.version_option(gcm.__version__, prog_name=gcm.__name__)
def cli() -> None:
    pass


if __name__ == '__main__':
    cli()
