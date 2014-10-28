from unittest.mock import MagicMock

from lemon import route
from lemon import view
from tests.fixtures.fixture_server import app
from tests.fixtures.fixture_server import client
from tests.fixtures.fixture_server import lemon


def test_route_add(monkeypatch):
    with app.app_context():
        monkeypatch.setattr(app, 'add_url_rule', MagicMock())
        route.add('/', 'ViewName')
        assert app.add_url_rule.called


def test_route_add_handler(monkeypatch):
    """Test adding a route that's an handler

    As a reminder: handlers are python module methods, they are callable
    elements.
    """

    with app.app_context():
        monkeypatch.setattr(app, 'add_url_rule', MagicMock())
        route.add('/add/', MagicMock())
        assert app.add_url_rule.called


def test_route_fetch(monkeypatch):
    """Fetch a regular view.
    """

    with app.app_context():
        monkeypatch.setattr(view, 'render_main_view',
            MagicMock(return_value='Called'))
        route.add(lemon, '/viewname/', 'ViewName')

        response = client.get('/viewname/')
        assert view.render_main_view.called
        assert response.data == b'Called'
        assert response.status_code == 200


def test_route_fetch_with_handler(monkeypatch):
    """Fetch a view that is an handler.
    """

    with app.app_context():
        handler = MagicMock(return_value='Called')
        route.add(lemon, '/handler/', handler)

        response = client.get('/handler/')
        assert handler.called
        assert response.data == b'Called'
        assert response.status_code == 200


def test_route_preparation():
    """Test the replacement of the routes.

    Note: The original options of the view should remain unchanged.
    """

    options = dict(
        params={
            'param1': '<value1>',
            'param2': {'param3': '<value3>'},
            'param5': 50
        },
        fetch={
            'endpoint': '/test/',
            'params': {'params1': '<value1>', 'params4': '<value4>'}
        })

    view_options = route.prepare(options, {
        '<value1>': 'v1', '<value3>': 'v3', '<value4>': 'v4'})

    for s in [options, view_options]:
        new = s is view_options

        assert s['params']['param1'] == new and 'v1' or '<value1>'
        assert s['params']['param5'] == 50
        assert s['params']['param2']['param3'] == new and 'v2' or '<value3>'
        assert s['fetch']['params']['params1'] == new and 'v1' or '<value1>'
        assert s['fetch']['params']['params4'] == new and 'v4' or '<value4>'
