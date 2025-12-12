from pathlib import Path

import click

from .base import (
    CCACHE_DIR,
    DISABLE_TEXT,
    ENABLE_TEXT,
    ENV_DIR,
    PACKAGE_NAME,
    Command,
    ensure_desired_env_line,
)

CCACHE_CONF = """# Maximum cache size to maintain
max_size = {max_size}

# Allow others to run 'ebuild' and share the cache.
umask = 002

# Don't include the current directory when calculating
# hashes for the cache. This allows re-use of the cache
# across different package versions, at the cost of
# slightly incorrect paths in debugging info.
# https://ccache.dev/manual/latest#_performance
hash_dir = false

# Preserve cache across GCC rebuilds and
# introspect GCC changes through GCC wrapper.
#
# We use -dumpversion here instead of -v,
# see https://bugs.gentoo.org/872971.
compiler_check = %compiler% -dumpversion
"""

ENV_CCACHE_CONF = """FEATURES="${{FEATURES}} ccache"
CCACHE_DIR="/var/cache/ccache/{package}"
"""


def ensure_file(file_dir: Path, file_name: str, content: str) -> None:
    file_dir.mkdir(parents=True, exist_ok=True)
    with (file_dir / file_name).open('w') as out:
        out.write(content)


class Enable(Command):
    """Enable ccache for a package.

    See https://wiki.gentoo.org/wiki//etc/portage/package.env
    for better understanding.
    """

    INVOKE_MESSAGE = f'Enabling ccache for {PACKAGE_NAME}'

    params = [
        click.Option(
            ['-m', '--max-size'],
            default='1.0GiB',
            show_default=True,
            help='Maximum ccache size for a package.',
        )
    ]

    @staticmethod
    def callback(package: str, max_size: str) -> None:
        ensure_file(
            file_dir=CCACHE_DIR / package,
            file_name='ccache.conf',
            content=CCACHE_CONF.format(max_size=max_size),
        )
        ensure_file(
            file_dir=ENV_DIR / package,
            file_name='ccache.env',
            content=ENV_CCACHE_CONF.format(package=package),
        )
        ensure_desired_env_line(
            desired=ENABLE_TEXT.format(package=package),
            undesired=DISABLE_TEXT.format(package=package),
        )
