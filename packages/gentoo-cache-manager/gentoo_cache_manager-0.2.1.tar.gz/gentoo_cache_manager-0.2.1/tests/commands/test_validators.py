from unittest.mock import Mock, call, patch

import pytest

from gcm.commands.validators import (
    AMBIGUOUS_PACKAGE_NAME,
    PACKAGE_NOT_FOUND,
    validate_package_name,
)


@pytest.mark.parametrize(
    'name,expected',
    (
        ('foo', 'app-misc/foo'),
        ('foo:1', 'app-misc/foo'),
        ('app-misc/bar', 'app-misc/bar'),
        ('=net-misc/bar-1.0', 'net-misc/bar'),
    ),
)
def test_validate_package_name_valid(name, expected):
    package = validate_package_name(None, None, name)
    assert package == expected


@patch('click.echo')
def test_validate_package_name_ambiguous(echo):
    context = Mock()

    validate_package_name(context, None, 'bar')

    assert echo.call_args_list == [
        call('\x1b[33mThe short name "bar" is ambiguous:\x1b[0m'),
        call('    \x1b[32m\x1b[1mapp-misc/bar\x1b[0m'),
        call('    \x1b[32m\x1b[1mnet-misc/bar\x1b[0m'),
        call(
            '\x1b[33mPlease specify one of the above '
            'fully-qualified names instead.\x1b[0m'
        ),
    ]
    context.abort.assert_called_once_with(AMBIGUOUS_PACKAGE_NAME)


@patch('click.echo')
def test_validate_package_name_not_found(echo):
    context = Mock()

    validate_package_name(context, None, 'missing')

    echo.assert_called_once_with(
        '\x1b[33mThere are no packages to satisfy "missing".\x1b[0m'
    )
    context.abort.assert_called_once_with(PACKAGE_NOT_FOUND)
