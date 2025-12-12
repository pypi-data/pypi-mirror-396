import io
import re
import subprocess

import click

from ..utils import warn
from .base import PACKAGE_NAME, Command, ccache_dir_env
from .exit_codes import CCACHE_BINARY_NOT_FOUND, OK

COLORS = {
    'Cacheable calls': ('yellow', 'magenta'),
    'Hits': ('green', 'yellow'),
    'Direct': ('bright_green', 'green'),
    'Preprocessed': ('bright_green', 'green'),
    'Misses': ('blue', 'yellow'),
    'Uncacheable calls': ('red', 'magenta'),
    'Local storage': ('white', ''),
    'Cache size (GiB)': ('cyan', 'magenta'),
    'Cache size (GB)': ('cyan', 'magenta'),
    'Cleanups': ('bright_black', ''),
}
STAT_REGEX = re.compile(r'(?P<indent> *)(?P<title>.*):(?P<data>.*)?\n')
DATA_REGEX = re.compile(
    r'(?P<spacing> +)(?P<value>[\d.]+) / '
    r'(?P<total> *[\d.]+) \((?P<percent>.*)\)'
)
STAT_TEMPLATE = '  {indent}{title}:{data}\n'
DATA_TEMPLATE = '{spacing}{value} / {total} ({percent})'


def colorize_data(data: str, stat_color: str, total_color: str) -> str:
    match = DATA_REGEX.match(data)
    if not match:
        return click.style(data, stat_color)

    values = match.groupdict()

    def colorize(key: str, color: str) -> None:
        values[key] = click.style(values[key], color)

    colorize('value', stat_color)
    colorize('total', total_color)
    colorize('percent', stat_color)

    return DATA_TEMPLATE.format(**values)


def show_stats(package: str) -> int:
    try:
        stdout: io.TextIOWrapper = subprocess.Popen(
            ['ccache', '-s'],
            env=ccache_dir_env(package),
            stdout=subprocess.PIPE,
            text=True,
        ).stdout  # type: ignore[assignment]
    except FileNotFoundError:
        warn('Unable to show stats due to missing ccache binary')
        return CCACHE_BINARY_NOT_FOUND

    stats = stdout.readlines()
    for line in stats:
        match = STAT_REGEX.match(line)
        if match:
            indent, title, data = match.groups()
            colors = COLORS.get(title)
            if colors:
                stat_color, total_color = colors
                title = click.style(title, stat_color)
                if data:
                    data = colorize_data(data, stat_color, total_color)
            line = STAT_TEMPLATE.format(indent=indent, title=title, data=data)
        else:
            line = f'  {line}'
        click.echo(line, nl=False)

    return OK


class Stats(Command):
    """Show ccache stats for a package."""

    INVOKE_MESSAGE = f'Showing ccache stats for {PACKAGE_NAME}'

    @staticmethod
    def callback(package: str) -> int:
        return show_stats(package)
