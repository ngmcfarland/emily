"""Shared fixtures for test modules"""

import sys
import os

from emily import start_emily
import pytest

curdir = os.path.dirname(__file__)
data_dir = os.path.join(curdir,'data')


@pytest.fixture
def app():
    more_brains = [os.path.join(data_dir,'tests.json')]
    session_vars_path = os.path.join(data_dir,'session_vars_test.json')
    app = start_emily(more_brains=more_brains,disable_emily_defaults=True,session_vars_path=session_vars_path,emily_port=8008)
    return app