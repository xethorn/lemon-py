from flask import current_app

import requests
import urllib


def jinja2(endpoint, params=None):
    """Api Jinja2 Helper.

    This helpers provides a quick access to the API within a template. It
    creates a more friendly interface than a dictionnary.

    Args:
        endpoint (string): the endpoint url.
        params (dict): additional paramters to pass to the endpoint.
    """

    return dict(
        endpoint=endpoint,
        params=params)


def get(endpoint, params=None):
    """Fetch an api endpoint.

    Args:
        endpoint (string): the url endpoint.
        params (dict): parameters to pass to this api endpoint.

    Return:
        dict: The json dictionary from the response.

    Todo(xethorn): add handlers for each result (success, unsucess, error), and
    add view behavior for each of those.
    """

    url = urllib.parse.urljoin(current_app.config['LEMON_API_URL'], endpoint)
    resp = requests.get(url, params=params)
    return resp.json()
