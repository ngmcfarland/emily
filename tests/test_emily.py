"""Tests for main Emily functions and Emily() class"""

import time
import json
import sys
import os

import emily
from pytest_flask.fixtures import client


curdir = os.path.dirname(__file__)
data_dir = os.path.join(curdir,'data')


def test_emily():
    """Does Emily() class work with 'EMILY_DIR/tests/data/tests.json' and default configuration?"""
    more_brains = [os.path.join(data_dir,'tests.json')]
    session_vars_path = os.path.join(data_dir,'session_vars_test.json')
    session = emily.Emily(more_brains=more_brains,disable_emily_defaults=True,session_vars_path=session_vars_path,emily_port=8004)
    session_id = session.get_session()
    session.start()
    hello_response,session_id = session.send(message='hello',session_id=session_id)
    quit_response,session_id = session.send(message='quit',session_id=session_id)
    assert hello_response == 'world'
    # The Emily thread closes if no more sessions are left, but pytest runs through these tests too quickly for Emily to make that check in time.
    time.sleep(0.1)


def test_stateless():
    """Does stateless function respond as expected to hello input?"""
    more_brains = [os.path.join(data_dir,'tests.json')]
    session_vars_path = os.path.join(data_dir,'session_vars_test.json')
    hello_response,session_id = emily.stateless(message='hello',more_brains=more_brains,disable_emily_defaults=True,session_vars_path=session_vars_path,emily_port=8006)
    quit_response,session_id = emily.stateless(message='quit',session_id=session_id,more_brains=more_brains,disable_emily_defaults=True,session_vars_path=session_vars_path)
    assert hello_response == 'world'


def test_flask_app(client):
    """Does Emily run successfully as a Flask web server?"""
    response = client.get('/get_session')
    assert response.status_code == 200
    session_id = response.get_data(as_text=True)
    response = client.post('/chat',data={'message':'hello','session_id':session_id})
    assert response.status_code == 200
    json_response = json.loads(response.get_data(as_text=True))
    assert json_response['response'] == 'world'
    response = client.post('/chat',data={'message':'quit','session_id':session_id})
    # The Emily thread closes if no more sessions are left, but pytest runs through these tests too quickly for Emily to make that check in time.
    time.sleep(0.1)