import re

from flask import current_app
from flask import request
from lemon import view


def add(lemon, rule, handler=None, app=None, **options):
    """Add a url endpoint.

    Each url is defined by a rule (regex style) which points to a specfic
    handler (either a module method or the name of a view.) The additional
    options are containing flask specific information and handler information.

    Example:

        Register a url to point to the Analytics view:

        ```python
        import route
        route.add('/analytics/', 'Analytics')
        ```

    Args:
        rule (string): The url rule (flask url regex style.)
        handler (string, Function): Handler for this url.
        options (dict): Additional options passed to the flask ``add_url_rule``
            method or the handler itself.
    """

    def callback(*arg, **kwargs):
        if isinstance(handler, str):  # pragma: no cover
            # Test in: tests/test_routes.py:test_route_fetch
            replacements = {'<' + k + '>': v for k, v in kwargs.items()}
            view_options = prepare(options, replacements)
            html = view.render_main_view(lemon, handler, **view_options)
            return html

        elif callable(handler):
            return handler(lemon, request, options=options)

    if isinstance(handler, str):
        lemon.add_route_views(
            rule=rule,
            keys=re.findall(r'(<.+?>)', rule),
            view=handler,
            params=options.get('params'),
            fetch=options.get('fetch'))

    if not app:
        app = current_app

    app.add_url_rule(
        rule, rule, callback, methods=options.get('methods'))


def prepare(options, replacements):
    """Prepare the options.

    Any of the placeholder in the options are being replaced with their
    corresponding value. It allows schemas to be (somewhat) aware of the
    context.

    Args:
        options (dict): the options of the view (includes the params, and
            fetch).
        replacements (dict): the replacement values for the placeholder (
            contains the key / value to make replacement faster.)
    Return:
        dict: The dictionary with the values.
    """

    if not isinstance(options, dict) and not isinstance(options, str):
        return options

    if isinstance(options, str):
        value = replacements.get(options)
        if value:
            return value
        return

    view_options = {}
    for key, value in options.items():
        view_options[key] = prepare(value, replacements)

    return view_options
