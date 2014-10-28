from unittest.mock import MagicMock
import requests

from tests.fixtures import fixture_server
from lemon import api


def test_jinja2_endpoint(monkeypatch):
    """The jinja2 helper is only creating an object based on the data provided.
    """

    endpoint = '/test/'
    params = dict(page=20)
    res = api.jinja2(endpoint, params=params)
    assert res.get('endpoint') is endpoint
    assert res.get('params') is params


def test_api_getter(monkeypatch):
    """Test the api get endpoint.
    """

    monkeypatch.setattr(requests, 'get',
        MagicMock(return_value=requests.Response()))
    monkeypatch.setattr(requests.Response, 'json', MagicMock())

    from flask import current_app

    with fixture_server.app.app_context():
        api.get('/test/')

    assert requests.get.called
    assert requests.Response.json.called
