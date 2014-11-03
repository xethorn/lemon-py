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
