import subprocess
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gcm.commands.base import ccache_dir_env
from gcm.commands.clear import Clear
from gcm.commands.exit_codes import (
    CCACHE_BINARY_NOT_FOUND,
    OK,
    PERMISSION_DENIED,
    UNKNOWN_ERROR,
)

from ..base import ABORTED, DONE

OUTPUT = 'Clearing ccache data for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m\n{}{}\n'


@pytest.mark.parametrize(
    'args,run_args',
    (
        (['foo'], ['ccache', '-C', '-z']),
        (['foo', '-k'], ['ccache', '-C']),
        (['foo', '--keep-stats'], ['ccache', '-C']),
    ),
)
@patch('subprocess.run')
def test_clear_ok(run, args, run_args):
    run.return_value.returncode = 0

    result = CliRunner().invoke(Clear(), args, color=True)

    package = 'app-misc/foo'
    run.assert_called_once_with(
        run_args,
        env=ccache_dir_env(package),
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.exit_code == OK
    assert result.output == OUTPUT.format('', DONE)


@patch('subprocess.run', side_effect=FileNotFoundError)
def test_clear_no_ccache(run):
    result = CliRunner().invoke(Clear(), ['foo'], color=True)

    run.accert_called_once()
    assert result.exit_code == CCACHE_BINARY_NOT_FOUND
    assert result.output == OUTPUT.format(
        '\x1b[33mUnable to clear ccache data '
        'due to missing ccache binary\x1b[0m\n',
        ABORTED,
    )


@patch('subprocess.run')
def test_clear_permission_denied(run):
    stderr = 'ccache: error: Permission denied\n'

    run.return_value.returncode = 1
    run.return_value.stderr = stderr

    result = CliRunner().invoke(Clear(), ['foo'], color=True)

    run.accert_called_once()
    assert result.exit_code == PERMISSION_DENIED
    assert result.output == OUTPUT.format(
        f'\n{stderr}'
        '\x1b[33mUnable to clear ccache data '
        'due to a lack of permissions\x1b[0m\n',
        ABORTED,
    )


@patch('subprocess.run')
def test_clear_unknown_error(run):
    stderr = 'ccache: error: Something went wrong\n'

    run.return_value.returncode = 1
    run.return_value.stderr = stderr

    result = CliRunner().invoke(Clear(), ['foo'], color=True)

    run.accert_called_once()
    assert result.exit_code == UNKNOWN_ERROR
    assert result.output == OUTPUT.format(
        f'\n{stderr}'
        '\x1b[33mUnknown error, please submit a bug report!\x1b[0m\n',
        ABORTED,
    )
