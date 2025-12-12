from .base import (
    DISABLE_TEXT,
    ENABLE_TEXT,
    PACKAGE_NAME,
    Command,
    ensure_desired_env_line,
)


class Disable(Command):
    """Disable ccache for a package.

    See https://wiki.gentoo.org/wiki//etc/portage/package.env
    for better understanding.
    """

    INVOKE_MESSAGE = f'Disabling ccache for {PACKAGE_NAME}'

    @staticmethod
    def callback(package: str) -> None:
        ensure_desired_env_line(
            desired=DISABLE_TEXT.format(package=package),
            undesired=ENABLE_TEXT.format(package=package),
        )
