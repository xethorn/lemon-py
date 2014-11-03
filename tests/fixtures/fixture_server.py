from flask import Flask
from lemon import Lemon
from tests.fixtures import fixture_api_handler

app = Flask(__name__)
lemon = Lemon(
    app,
    app_view='AppView',
    view_path='tests/fixtures/views/',
    api_handler=fixture_api_handler.api)
client = app.test_client()
