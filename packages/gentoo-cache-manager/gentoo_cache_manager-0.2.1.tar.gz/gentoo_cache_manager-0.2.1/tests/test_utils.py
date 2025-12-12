from unittest.mock import patch

import pytest
from portage.exception import AmbiguousPackageName, PackageNotFound

from gcm.utils import normalize_package_name, pretty_name, warn


@patch('click.echo')
def test_warn(echo):
    warn('Attention!')
    echo.assert_called_once_with('\x1b[33mAttention!\x1b[0m')


def test_pretty_name():
    name = pretty_name('app-misc/foo')
    assert name == '\x1b[32m\x1b[1mapp-misc/foo\x1b[0m'


@pytest.mark.parametrize(
    'name,expected',
    (
        ('foo', 'app-misc/foo'),
        ('foo:1', 'app-misc/foo'),
        ('app-misc/bar', 'app-misc/bar'),
        ('=net-misc/bar-1.0', 'net-misc/bar'),
    ),
)
def test_normalize_package_name_valid(name, expected):
    package = normalize_package_name(name)
    assert package == expected


def test_normalize_package_name_ambiguous():
    with pytest.raises(AmbiguousPackageName):
        normalize_package_name('bar')


def test_normalize_package_name_not_found():
    with pytest.raises(PackageNotFound):
        normalize_package_name('missing')
