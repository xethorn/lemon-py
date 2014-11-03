"""
Views
=====

The views are small contained components composed of html, javascript
and stylesheets. They live in the directory defined in `config.VIEW_PATH`.
By default: ``<project>/views/``. Views are capable of:

- Include other views: A view can be a full page, but might require more
  than one additional view to be generated. Other views can be included by
  using the following code: ``{{ view('ViewName') }}``.

- Taking options: at times, views might require options. For instance, a button
  can have several states (primary, secondary, disabled). The state can be
  passed as an option.
  Example: ``{{ view('Button', options={'state': 'primary'}) }}``

- Fetch a source: The source is composed of an API url and options. It fetches
  an api and returns the data. Each view has a package.json which contains the
  list of available api endpoint for this specific view.

Author:
    Michael Ortali <mortali@theorchard.com>

Date:
    09/25/2014
"""

from flask import current_app
import flask
import jinja2
import os
import os.path
import uuid

from lemon import api


class View():

    def __init__(self, path):
        """Initialize a View.

        Args:
            path (string): The path of the view allows to fetch more quickly
                the data.
        """

        self.path = path
        self.name = path.split('/')[-1]
        self.children = []
        self.api = None
        self.data = None
        self.params = dict()
        self.id = str(uuid.uuid4())
        self.template = '%(path)s/%(name)s.nunjucks' % dict(
            path=self.path, name=self.name)


    def register(self, parent=None):
        """Register a child with its parent.

        Args:
            parent (`View`): The child view.
        """

        if parent:
            parent.add_child(self)


    def add_child(self, child):
        """Add a child to the view.

        Args:
            child (`View`): The child view.
        """

        if not child == self:
            self.children.append(child)


    def fetch(self, params):
        """Fetch the api to display information.
        """

        if not params:
            return None

        self.api = dict(
            endpoint=params.get('endpoint'),
            params=params.get('params'))


        env = view_environments.get(current_app, None)
        if not env:
            return None
        print(dir(env.globals))

        handler = env.globals.get('lemon').api_handler
        self.data = handler.get(self.path, **self.api)

    def render(self, **kwargs):
        """Render a view.

        Args:
            kwargs (dict): Contains the informations that are allowing us to
                draw this specific view.
        """

        self.register(kwargs.get('parent') or None)
        self.fetch(kwargs.get('fetch'))
        self.params = kwargs.get('params') or dict()

        environment = view_environments[current_app]

        return jinja2.Markup('<div '
            'id="' + self.id + '" class="View ' + self.name + '">' +
            environment.get_template(self.template).render(
                params=self.params,
                api=self.api,
                data=self.data,
                parent=self) +
            '</div>')


    def to_dict(self):
        """Render the dictionary representation of this object.

        Return:
            Dict: The dictionary that represents the view.
        """

        return dict(
            api=self.api,
            children=[child.to_dict() for child in self.children],
            id=self.id,
            params=self.params,
            path=self.path)


class MainView(View):
    """Main View

    The rendering of a main view implies that the site has not yet be rendered.
    This module is defined in `config.VIEW_MAIN_NAME` and does not need the tag
    to be rendered.
    """

    def __init__(self, path):
        super().__init__(path)
        MainView.instance = self


    def render(self, lemon=None, **kwargs):
        if lemon:
            kwargs.update(routes=lemon.route_views)

        render = view_environments[current_app].get_template(
            self.template, lemon).render(**kwargs)
        return render


def render_main_view(lemon, primary_view, **kwargs):
    """Render the main view.

    Args:
        lemon (Lemon): The lemon instance.
        primary_view (string): Name of the primary view.
        kwargs (dict): Properties to pass to the primary view.

    Return:
        `jinja2.Markup`: The html of the module.
    """

    main_view = MainView(current_app.config.get('LEMON_APP_VIEW'))
    html = main_view.render(
        parent=main_view,
        primary_view=primary_view,
        params=kwargs)
    return html


def render(view_name, **kwargs):
    """Render a view.

    Args:
        view_name (string): The view name.
        kwargs (dict): Properties to pass to the view.

    Return:
        `jinja2.Markup`: The html of the view.
    """

    return View(view_name).render(**kwargs)


def get(view_name):
    """Create a view based on its name.

    Todo:
        mortali: Rename this method create.

    Return:
        `View`: The view.
    """

    return View(view_name)


@jinja2.contextfunction
def jinja2_render(context, view_name, **kwargs):
    """Context-aware Jinja2 Helper.

    The context provides additional information, such as the reference to the
    current view.

    Args:
        context (`jinja2.Context`): The jinja2 context object.
        view_name (string): Name of the view.
        **kwargs: Additional options.
    Return:
        `jinja2.Markup`: the HTML of the view.
    """

    kwargs.update(parent=context.get('parent'))
    return render(view_name, **kwargs)


def jsonify(obj):
    """Turns an object into a json.

    Return:
        string: The json content that will be displayed in the template.
    """
    return flask.json.dumps(obj)


view_environments = {}


def create_environment(lemon):
    """Create the jinja2 environmnet for a lemon instance.

    Each lemon instance has its own jinja2 environment. This environment is
    kept in memory for faster access.
    """

    view_path = lemon.app.config['LEMON_VIEW_PATH']
    view_loader = jinja2.FileSystemLoader([view_path])

    view_environments[lemon.app] = jinja2.Environment(
        loader=view_loader,
        autoescape=True)

    view_environments[lemon.app].globals.update(
        lemon=lemon,
        view=jinja2_render,
        Api=api.jinja2,
        jsonify=jsonify)
