from unittest.mock import Mock, patch

from gcm.commands.context import Context


@patch('click.Context.exit')
@patch('click.echo')
def test_context_abort(echo, exit):
    context = Context(Mock())
    code = 42

    context.abort(code)

    echo.assert_called_once_with('\x1b[31mAborted!\x1b[0m', err=True)
    exit.assert_called_once_with(code)
