from unittest.mock import MagicMock, call, patch

import pytest
from click.testing import CliRunner

from gcm.commands.base import CCACHE_DIR, DISABLE_TEXT, ENABLE_TEXT, ENV_DIR
from gcm.commands.enable import (
    CCACHE_CONF,
    ENV_CCACHE_CONF,
    Enable,
    ensure_file,
)

from ..base import DONE


def test_ensure_file():
    file_dir = MagicMock()
    file_name = 'dummy.txt'
    content = 'Lorem ipsum dolor sit amet'

    ensure_file(file_dir, file_name, content)

    file_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    file_dir.__truediv__.assert_called_once_with(file_name)

    file_path = file_dir.__truediv__.return_value
    file_path.open.assert_called_once_with('w')

    out = file_path.open.return_value.__enter__.return_value
    out.write.assert_called_once_with(content)


@pytest.mark.parametrize('max_size', ('512MiB', '2.0G', None))
@patch('gcm.commands.enable.ensure_desired_env_line')
@patch('gcm.commands.enable.ensure_file')
def test_enable(ensure_file, ensure_desired_env_line, max_size):
    if max_size:
        args = ['foo', '--max-size', max_size]
    else:
        args = ['foo']
        max_size = '1.0GiB'

    result = CliRunner().invoke(Enable(), args, color=True)

    package = 'app-misc/foo'
    assert result.exit_code == 0
    assert result.output == (
        f'Enabling ccache for \x1b[32m\x1b[1m{package}\x1b[0m\n{DONE}\n'
    )
    assert ensure_file.call_args_list == [
        call(
            file_dir=CCACHE_DIR / package,
            file_name='ccache.conf',
            content=CCACHE_CONF.format(max_size=max_size),
        ),
        call(
            file_dir=ENV_DIR / package,
            file_name='ccache.env',
            content=ENV_CCACHE_CONF.format(package=package),
        ),
    ]
    ensure_desired_env_line.assert_called_once_with(
        desired=ENABLE_TEXT.format(package=package),
        undesired=DISABLE_TEXT.format(package=package),
    )
