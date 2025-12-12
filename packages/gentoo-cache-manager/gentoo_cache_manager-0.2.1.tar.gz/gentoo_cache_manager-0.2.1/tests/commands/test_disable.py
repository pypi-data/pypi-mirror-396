from unittest.mock import patch

import pytest

from gcm.commands import Disable
from gcm.commands.base import DISABLE_TEXT, ENABLE_TEXT


@patch('click.echo')
@patch('gcm.commands.disable.ensure_desired_env_line')
def test_disable(ensure_desired_env_line, echo):
    command = Disable()

    with pytest.raises(SystemExit):
        command(['foo'])

    package = 'app-misc/foo'
    echo.assert_any_call(
        'Disabling ccache for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m'
    )
    ensure_desired_env_line.assert_called_once_with(
        desired=DISABLE_TEXT.format(package=package),
        undesired=ENABLE_TEXT.format(package=package),
    )
