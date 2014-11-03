"""
Application
===========

Lemon Application are single page web applications. This backend work in pair
with [Lemon-JS](github.com/theorchard/lemon-js/). For all those applications,
the url: `/views/` is reserved as an endpoint to regenerate the views.

Configuration
-------------

- _Application view (app_view)_: Main view of your application. In most cases,
  it will contain the basic structure of your html page (header, body, footer)
  and the `primary_view` (which will be defined by the url.)

- _View Path (view_path)_: Where all the views are located. For consistency,
  they should all be in the same directory.

Example
-------

The most common case, the application has a `/views/` directory, and all the
data fetched is being provided by `/api/`.

```python

from flask import Flask
from lemon import Lemon

app = Flask(__name__)
lemon = Lemon(app, app_view='AppView', view_path='views/')
```

"""

from flask import current_app

from lemon import route
from lemon import view
from lemon import handlers


class Lemon(object):

    def __init__(self, app=None, app_view=None, view_path=None):
        """Initialize Lemon.

        Create one instance of Lemon and defines the basic configuration of the
        plugin.

        Args:
            app (Flask): The flask application.
            app_view (string): The application main view.
            view_path (string): The application view path.
        """

        self.app = app
        self.route_views = []

        if app is not None:
            self.init_app(app, app_view, view_path)

    def init_app(self, app, app_view, view_path):
        """Set the configuration and initialize the jinja2 environment.

        Args:
            app (Flask): The flask application.
            app_view (string): The application main view.
            view_path (string): The application view path.
        """

        # Set all the app configuration.
        app.config.setdefault('LEMON_APP_VIEW', app_view or 'App')
        app.config.setdefault('LEMON_VIEW_PATH', view_path or '/views/')

        # Create the environment
        view.create_environment(self)

        # Register the routes.
        self.add_route('/view/', handlers.view_handler, app, methods=['POST'])

    def add_route(self, rule, handler, app=None, **options):
        """Add a new route.

        Args:
            rule (string): The url rule (flask url regex style.)
            handler (string, Function): Handler for this url.
            options (dict): Additional options passed to the flask
                ``add_url_rule`` method or the handler itself.
        """

        app = app or self.app
        route.add(self, rule, handler, app=app, **options)

    def add_route_views(self, **view_info):
        """Register a view to correspond to a view.

        Args:
            view_infos (dict): The view information.
        """

        self.route_views.append(view_info)
