"""
Handlers
========

Handlers provide additional endpoints for all requests that do not correspond
to an existing view.
"""

from flask import current_app
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

    lemon = current_app.extensions.get('lemon')
    if not lemon:
        abort(512)

    params = json.loads(request.args.get('data'))
    primary_view = view.View(params.get('path'))
    primary_view.render(
        context=lemon.context,
        fetch=params.get('fetch'),
        id=params.get('id'),
        lemon=lemon,
        params=params.get('params'))
        
    primary_view.finish()
    response = json.dumps(dict(
        html=primary_view.html,
        tree=primary_view.to_dict()))

    return response
