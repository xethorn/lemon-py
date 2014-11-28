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

from threading import Thread
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
        self.describe()

    def describe(self, tag=None, classes=None, attrs=None):
        """Describe a view.

        The description of a view can alter the css classes appended, the
        attribtues and the tags.

        Args:
            tag (string): Valid html tag (e.g. `div`, `button`).
            classes (list): Css classes to use for this particular view.
            attrs (dict): HTML Attributes (other than classes.)
        """

        self.tag = tag or 'div'
        self.classes = classes or []
        self.attrs = attrs or {}

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

    def fetch(self, lemon, context, params):
        """Fetch the api to display information.
        """

        if not params:
            return None

        self.api = dict(
            endpoint=params.get('endpoint'),
            params=params.get('params'))

        handler = lemon.api_handler
        self.data = handler.get(context, view_name=self.path, **self.api)

    def render_response(self, kwargs):
        """Render the html response for the view.

        The generated response takes in ready to go html and will also use a
        lot of the view values (id, tag, classes, attributes) to generate the
        container of the view.

        Args:
            template (string): the html for this view.
            kwargs (dict): The params of the views
        Return:
            String: the container of the view along with the html.
        """

        lemon = kwargs.get('lemon')
        context = kwargs.get('context')

        self.fetch(lemon, context, kwargs.get('fetch'))
        self.params = kwargs.get('params') or dict()

        html = lemon.app.jinja_env.get_template(self.template).render(
            lemon=lemon,
            context=context,
            params=self.params,
            api=self.api,
            data=self.data,
            parent=self)

        # Wait for all children to be rendered and replace them as we get them.
        for child in self.children:
            child.finish()
            html = html.replace('#%s' % child.id, child.html or '')

        html_element = dict(
            id=self.id,
            html=jinja2.Markup(html),
            tag_name=self.tag,
            classes=' '.join(self.classes + [self.name]),
            attrs=' '.join([
                n + '="' + jinja2.escape(v) + '" '
                for n, v in self.attrs.items()]))

        self.html = jinja2.Markup(
            '<%(tag_name)s id="%(id)s" class="View %(classes)s" %(attrs)s>' +
            '%(html)s' +
            '</%(tag_name)s>') % html_element

    def render(self, **kwargs):
        """Render a view (async).

        The view is rendered in a thread, which allows other child views to be
        rendered at the same time.

        Args:
            kwargs (dict): Contains the informations that are allowing us to
                draw this specific view.
        Return:
            string: The id of the view (which will later on be replaced with
                its html.)
        """

        self.register(kwargs.get('parent') or None)
        self.html = ''

        # Create the thread.
        if kwargs.get('fetch'):
            thread = Thread(
                target=self.render_response, args=(kwargs,))
            thread.start()
            self.finish = thread.join
            return '#%(id)s' % dict(id=self.id)

        self.finish = lambda: None
        self.render_response(kwargs)
        return self.html

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
            kwargs.update(routes=lemon.route_views, lemon=lemon)

        render = current_app.jinja_env.get_template(
            self.template).render(**kwargs)

        for child in self.children:
            child.finish()
            render = render.replace('#%s' % child.id, child.html)
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

    primary_view = View(primary_view)
    context = lemon.context
    primary_view.render(
        lemon=lemon,
        context=context,
        fetch=kwargs.get('fetch'),
        params=kwargs.get('params'),
        data=kwargs.get('data'))

    main_view = MainView(current_app.config.get('LEMON_APP_VIEW'))
    main_view.add_child(primary_view)
    primary_view.finish()

    html = main_view.render(
        lemon=lemon,
        context=context,
        parent=main_view,
        primary_view=primary_view.html)

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

    kwargs.update(
        context=context.get('context'),
        lemon=context.get('lemon'),
        parent=context.get('parent'))
    return render(view_name, **kwargs)


def jsonify(obj):
    """Turns an object into a json.

    Return:
        string: The json content that will be displayed in the template.
    """
    return flask.json.dumps(obj)


@jinja2.contextfunction
def describe(context, tag=None, classes=None, attrs=None):
    """Describe a view.

    Proxy for View.describe
    """

    context.get('parent').describe(tag, classes, attrs)
    return ''


def create_environment(lemon):
    """Create the jinja2 environmnet for a lemon instance.

    Each lemon instance has its own jinja2 environment. This environment is
    kept in memory for faster access.
    """

    view_path = lemon.app.config['LEMON_VIEW_PATH']
    view_loader = jinja2.FileSystemLoader([view_path])

    lemon.app.jinja_env = jinja2.Environment(
        loader=view_loader,
        autoescape=True)

    lemon.app.jinja_env.globals.update(
        lemon=lemon,
        describe=describe,
        view=jinja2_render,
        Api=api.jinja2,
        jsonify=jsonify)
