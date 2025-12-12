from typing import NoReturn

import click


class Context(click.Context):
    def abort(self, code: int = 0) -> NoReturn:
        click.echo(click.style('Aborted!', 'red'), err=True)
        self.exit(code)
