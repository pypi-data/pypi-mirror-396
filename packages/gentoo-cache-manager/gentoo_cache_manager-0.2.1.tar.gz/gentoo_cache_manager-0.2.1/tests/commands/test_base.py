import io
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gcm.commands.base import (
    CCACHE_DIR,
    PACKAGE_NAME,
    Command,
    ccache_dir_env,
    ensure_desired_env_line,
    get_package_env_path,
)

from ..base import ABORTED, DONE

DUMMY_ENV = """# foo
bar
# foo
# baz
"""


def test_ccache_dir_env():
    package = 'app-misc/foo'
    env = ccache_dir_env(package)
    assert env == {'CCACHE_DIR': str(CCACHE_DIR / package)}


@pytest.mark.parametrize(
    'exists,is_file',
    (
        (True, True),
        (True, False),
        (False, None),
    ),
)
@patch('gcm.commands.base.PACKAGE_ENV_PATH')
def test_get_package_env_path(mock, exists, is_file):
    mock.exists.return_value = exists
    mock.is_file.return_value = is_file

    new_path = object()
    truediv = mock.__truediv__
    truediv.return_value = new_path

    path = get_package_env_path()

    mock.exists.assert_called_once_with()

    if exists:
        mock.mkdir.assert_not_called()
        mock.is_file.assert_called_once_with()
    else:
        mock.mkdir.assert_called_once_with()
        mock.is_file.assert_not_called()

    if is_file:
        truediv.assert_not_called()
        assert path is mock
    else:
        truediv.assert_called_once_with('ccache')
        assert path is new_path


@pytest.mark.parametrize(
    'desired,undesired,expected',
    (
        ('foo\n', '# foo\n', 'foo\nbar\n# baz\n'),
        ('bar\n', '# bar\n', '# foo\nbar\n# foo\n# baz\n'),
        ('baz\n', '# baz\n', '# foo\nbar\n# foo\nbaz\n'),
        ('new\n', '# new\n', '# foo\nbar\n# foo\n# baz\nnew\n'),
        ('# foo\n', 'foo\n', '# foo\nbar\n# foo\n# baz\n'),
        ('# bar\n', 'bar\n', '# foo\n# bar\n# foo\n# baz\n'),
        ('# baz\n', 'baz\n', '# foo\nbar\n# foo\n# baz\n'),
        ('# new\n', 'new\n', '# foo\nbar\n# foo\n# baz\n# new\n'),
    ),
)
@patch('gcm.commands.base.get_package_env_path')
def test_ensure_desired_env_line(
    get_package_env_path, desired, undesired, expected
):
    env = io.StringIO(DUMMY_ENV)
    path = get_package_env_path.return_value
    path.open.return_value.__enter__.return_value = env

    ensure_desired_env_line(desired, undesired)

    path.touch.assert_called_once()
    path.open.assert_called_once_with('r+')
    assert env.getvalue() == expected


def test_command_callback_not_implemented():
    with pytest.raises(NotImplementedError):
        Command.callback('app-misc/foo')


class DummyCommand(Command):
    """Do nothing."""

    INVOKE_MESSAGE = f'Doing nothing with {PACKAGE_NAME}'

    callback_is_called = False

    def callback(self, package):
        self.callback_is_called = True
        assert package == 'app-misc/foo'
        return self.exit_code

    def __init__(self, exit_code=0) -> None:
        super().__init__()
        self.exit_code = exit_code


OUTPUT = 'Doing nothing with \x1b[32m\x1b[1mapp-misc/foo\x1b[0m\n{}\n'


@pytest.mark.parametrize('exit_code,outcome', ((0, DONE), (1, ABORTED)))
def test_command_invoke(exit_code, outcome):
    command = DummyCommand(exit_code)

    result = CliRunner().invoke(command, ['foo'], color=True)

    assert command.callback_is_called
    assert result.exit_code == exit_code
    assert result.output == OUTPUT.format(outcome)
