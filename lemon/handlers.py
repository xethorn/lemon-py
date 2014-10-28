"""
Handlers
========

Handlers provide additional endpoints for all requests that do not correspond
to an existing view.
"""

from flask import json
from lemon import view


def view_handler(request, options=None):
    """Generate a partial view.

    A partial view only re-render a view, without the need to recreate the full
    application. It makes fetching small components faster. This endpoint is
    primarely used for xhr.

    Args:
        request: The Flask.request object.
        options (dict): Extra options.

    Return:
        `string`: Contains the json object which will later on be used by
            Backbone to regenerate the view.
    """

    params = request.get_json(force=True)
    primary_view = view.View(params.get('path'))
    response = json.dumps(dict(
        html=primary_view.render(
            fetch=params.get('fetch'),
            params=params.get('params')),
        tree=primary_view.to_dict()))
    return response
