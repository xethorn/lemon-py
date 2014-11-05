from jinja2 import Template
from tests.fixtures.fixture_api_handler import api
from tests.fixtures.fixture_server import app
from tests.fixtures.fixture_server import lemon
from unittest.mock import MagicMock
import os
import os.path


from lemon import view


def test_view_generation():
    """Test the view generation.
    """

    my_view = view.View('ViewName')
    assert my_view.path == 'ViewName'
    assert my_view.name == 'ViewName'
    assert my_view.template == 'ViewName/ViewName.nunjucks'

    my_view = view.View('ParentView/ChildView')
    assert my_view.path == 'ParentView/ChildView'
    assert my_view.name == 'ChildView'
    assert my_view.template == 'ParentView/ChildView/ChildView.nunjucks'


def test_add_child():
    """Test adding a child.
    """

    my_view = view.View('View')
    test_view = view.View('Test')

    my_view.add_child(my_view)
    assert not my_view.children

    my_view.add_child(test_view)
    assert len(my_view.children) == 1
    assert my_view.children[0] == test_view


def test_registering_parent():
    """Registering a child to a parent should add it.
    """

    my_view = view.View('View')
    parent_view = view.View('Parent')

    my_view.register()
    assert not parent_view.children

    my_view.register(parent=parent_view)
    assert parent_view.children
    assert parent_view.children[0] == my_view


def test_main_view_rendering(monkeypatch):
    """Test the main view rendering.

    The main view does not add additional html into the response since it is
    meant to draw the shell of the site.
    """

    value = (
        'Hello {% if primary_view %}'
        '{{ primary_view|safe }}'
        '{% endif %}');

    app.app_context().push()
    create_template = app.jinja_env.from_string

    template = create_template(value)
    magic_template = MagicMock(return_value=template)
    monkeypatch.setattr(
        app.jinja_env, 'get_template', magic_template)

    my_view = view.MainView('Test')
    primary_view = view.View('PrimaryView')

    app.config.setdefault('LEMON_APP_VIEW', 'Test')
    value = view.render_main_view(lemon, primary_view='PrimaryView')

    assert magic_template.called
    assert value.find('View Primary') > 0


def test_view_rendering(monkeypatch):
    """Test the view rendering.

    Normal view rendering casts the response into an html element that contains
    more information, and make it easier for javascript to identify it.
    """

    value = 'View Content'

    template = Template(value)
    magic_template = MagicMock(return_value=template)
    monkeypatch.setattr(
        app.jinja_env, 'get_template', magic_template)
    my_view = view.View('Test')
    my_view.render(lemon=lemon)
    my_view.finish()

    assert not my_view.html == value
    assert my_view.html.find(value) > 0
    assert magic_template.called


def test_call_non_existent_view():
    """Test calling a view that does not exist.

    The error is simple enough that it should throw an exception when the view
    called is missing.
    """

    my_view = view.View('Test')

    try:
        my_view.render()
        assert False
    except:
        assert True


def test_jinja2_render(monkeypatch):
    """Test jinja2 render and inclusion of other views.

    The view included should
    """

    identifier = '<MyView>'
    view_name = 'MyView'

    render = view.View(view_name).render
    my_view_tpl = Template(identifier)
    monkeypatch.setattr(
        app.jinja_env, 'get_template',
        MagicMock(return_value=my_view_tpl))

    create_template = app.jinja_env.from_string
    html = create_template(
        "{{ view('" + view_name +"') }}").render(lemon=lemon)

    assert str(view.render(view_name, lemon=lemon)).find(identifier) > 0
    assert html.find(identifier) > 0


def test_jinja2_render_with_tag_name():
    """Test jinja2 render with a different view tag.
    """

    response = view.render_main_view(lemon, primary_view='Button')
    create_template = app.jinja_env.from_string
    html = create_template("{{ view('Button') }}").render(lemon=lemon)
    assert html.find('<button') > -1


def test_jinja2_render_with_tag_name():
    """Test jinja2 render with additional classes
    """

    response = view.render_main_view(lemon, primary_view='Button')
    create_template = app.jinja_env.from_string
    html = create_template(
        "{{ view('Button', params={'classes': ['Test']}) }}").render(lemon=lemon)
    assert html.find('Test') > -1


def test_jinja2_render_with_attributes():
    """Test jinja2 render with additional classes
    """

    response = view.render_main_view(lemon, primary_view='Button')
    create_template = app.jinja_env.from_string
    html = create_template(
        "{{ view('Button', params={'attrs': {'data-id': 'foo'}}) }}").render(
            lemon=lemon)
    assert html.find('data-id') > -1
    assert html.find('foo') > -1


def test_add_child_with_template(monkeypatch):
    """Test adding child.

    Whenever views are rendered, a tree should be rendered in parallel, that
    allows us to know where things are build.
    """

    view.render_main_view(lemon, primary_view='MainView')
    view_dict = view.MainView.instance.to_dict()
    children = view_dict.get('children')

    assert len(children) == 1
    assert children[0].get('path') == 'MainView'


def test_get():
    """Test getting a view.
    """

    assert isinstance(view.get('Test'), view.View)


def test_fetching_data(monkeypatch):
    """Test fetching data for a view.
    """

    mock = MagicMock(return_value='response')
    monkeypatch.setattr(api, 'get', mock)

    params = dict(key='value')
    test_view = view.View('Test')
    test_view.fetch(lemon, dict(endpoint='/url/', params=params))

    assert test_view.data is 'response'
    mock.assert_called_once_with('Test', endpoint='/url/', params=params)


def test_jsonify():
    """Test the ability to jsonify an object
    """

    assert view.jsonify(True) == 'true'
    assert view.jsonify({'foo': 'bar'}) == '{"foo": "bar"}'
