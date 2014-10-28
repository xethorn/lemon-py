from flask import json
from unittest.mock import MagicMock
from unittest.mock import patch

from lemon import view
from lemon import handlers


def test_view_handler(monkeypatch):
    request = MagicMock(return_value=dict())
    get_json = MagicMock(return_value=dict(path='Test'))
    monkeypatch.setattr(request, 'get_json', get_json)

    with patch.object(view.View, 'render', return_value='HTML'):
        response = handlers.view_handler(request)
        obj = json.loads(response)
        assert obj.get('html') == 'HTML'
        assert obj.get('tree').get('path') == 'Test'
