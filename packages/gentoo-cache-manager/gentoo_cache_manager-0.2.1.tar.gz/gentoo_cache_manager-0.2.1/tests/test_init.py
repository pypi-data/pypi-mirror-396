import os
import sys
from unittest.mock import patch


@patch.dict(os.environ)
@patch.dict(sys.modules)
def test_init():
    assert os.environ['PORTAGE_CONFIGROOT'] == 'tests/data'

    del os.environ['PORTAGE_CONFIGROOT']
    sys.modules.pop('gcm', None)

    __import__('gcm')

    assert os.environ['PORTAGE_CONFIGROOT'] == '/'
