from flask import Flask
from lemon import Lemon

app = Flask(__name__)
lemon = Lemon(
    app,
    app_view='AppView',
    view_path='tests/fixtures/views/',
    api_url='/views/')
client = app.test_client()
