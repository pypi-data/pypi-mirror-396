import runpy
import sys
from unittest.mock import call, patch

import pytest
from click.testing import CliRunner

import gcm
from gcm.cli import cli

from .base import ABORTED, DONE


@pytest.mark.parametrize(
    'exit_code,outcome',
    (
        (None, call(DONE)),
        (0, call(DONE)),
        (1, call(ABORTED, err=True)),
    ),
)
@patch.dict(sys.modules)
@patch('sys.argv', ['gcm', 'enable', 'foo'])
@patch('click.echo')
@patch('gcm.commands.enable.Enable.callback')
def test_main(callback, echo, exit_code, outcome):
    callback.return_value = exit_code
    del sys.modules['gcm.cli']

    with pytest.raises(SystemExit):
        runpy.run_module('gcm.cli', run_name='__main__')

    callback.assert_called_once_with(package='app-misc/foo', max_size='1.0GiB')
    assert echo.call_args_list == [
        call('Enabling ccache for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m'),
        outcome,
    ]


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert result.output == f'{gcm.__name__}, version {gcm.__version__}\n'
