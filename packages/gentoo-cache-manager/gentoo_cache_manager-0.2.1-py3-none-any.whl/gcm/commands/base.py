from pathlib import Path
from typing import Any

import click

from ..utils import pretty_name
from .context import Context
from .validators import validate_package_name

CCACHE_DIR = Path('/var/cache/ccache')
ENV_DIR = Path('/etc/portage/env')
PACKAGE_ENV_PATH = Path('/etc/portage/package.env')

ENABLE_TEXT = '{package}\t{package}/ccache.env\n'
DISABLE_TEXT = f'# {ENABLE_TEXT}'

PACKAGE_NAME = pretty_name('{package}')


def ccache_dir_env(package: str) -> dict[str, str]:
    return {'CCACHE_DIR': str(CCACHE_DIR / package)}


def get_package_env_path() -> Path:
    if not PACKAGE_ENV_PATH.exists():
        PACKAGE_ENV_PATH.mkdir()
    elif PACKAGE_ENV_PATH.is_file():
        return PACKAGE_ENV_PATH

    return PACKAGE_ENV_PATH / 'ccache'


def ensure_desired_env_line(desired: str, undesired: str) -> None:
    path = get_package_env_path()
    path.touch()
    with path.open('r+') as env:
        env.seek(0)
        lines = env.readlines()
        written = desired in lines
        if undesired in lines:
            env.seek(0)
            for line in lines:
                if line == undesired:
                    if not written:
                        env.write(desired)
                        written = True
                else:
                    env.write(line)
            env.truncate()
        elif not written:
            env.write(desired)


class Command(click.Command):
    INVOKE_MESSAGE: str

    context_class = Context

    @staticmethod
    def callback(package: str, *args: Any) -> int | None:
        raise NotImplementedError

    def __init__(self) -> None:
        name = self.__class__.__name__.lower()
        click.BaseCommand.__init__(self, name)

        params = list(self.params) if hasattr(self, 'params') else []
        params.append(
            click.Argument(['package'], callback=validate_package_name)
        )

        self.params = params
        self.help = self.__class__.__doc__
        self.epilog = None
        self.options_metavar = '[OPTIONS]'
        self.short_help = None
        self.add_help_option = True
        self.no_args_is_help = False
        self.hidden = False
        self.deprecated = False

    def invoke(self, ctx: Context) -> None:  # type: ignore[override]
        click.echo(self.INVOKE_MESSAGE.format(**ctx.params))
        code = super().invoke(ctx)
        if code:
            ctx.abort(code)
        click.echo(click.style('Done :-)', 'green'))
