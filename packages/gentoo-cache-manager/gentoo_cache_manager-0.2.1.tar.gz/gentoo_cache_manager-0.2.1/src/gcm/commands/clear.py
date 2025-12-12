import subprocess

import click

from ..utils import warn
from .base import PACKAGE_NAME, Command, ccache_dir_env
from .exit_codes import (
    CCACHE_BINARY_NOT_FOUND,
    OK,
    PERMISSION_DENIED,
    UNKNOWN_ERROR,
)


def clear_stats(package: str, keep_stats: bool) -> int:
    args = ['ccache', '-C']
    if not keep_stats:
        args.append('-z')

    try:
        result = subprocess.run(
            args,
            stderr=subprocess.PIPE,
            env=ccache_dir_env(package),
            text=True,
        )
    except FileNotFoundError:
        warn('Unable to clear ccache data due to missing ccache binary')
        return CCACHE_BINARY_NOT_FOUND

    if result.returncode:
        click.echo(f'\n{result.stderr}', nl=False, err=True)
        if 'Permission denied' in result.stderr:
            warn('Unable to clear ccache data due to a lack of permissions')
            return PERMISSION_DENIED

        warn('Unknown error, please submit a bug report!')
        return UNKNOWN_ERROR

    return OK


class Clear(Command):
    """Clear ccache data for a package."""

    INVOKE_MESSAGE = f'Clearing ccache data for {PACKAGE_NAME}'

    params = [
        click.Option(
            ['-k', '--keep-stats'],
            is_flag=True,
            help='Keep statistics counters.',
        )
    ]

    @staticmethod
    def callback(package: str, keep_stats: bool) -> int:
        return clear_stats(package, keep_stats)
