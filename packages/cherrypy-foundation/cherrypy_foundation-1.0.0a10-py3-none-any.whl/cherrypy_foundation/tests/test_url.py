# CherryPy Foundation
# Copyright (C) 2025 IKUS Software
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import cherrypy
from cherrypy.test import helper

import cherrypy_foundation.tools.jinja2  # noqa

from ..url import url_for

env = cherrypy.tools.jinja2.create_env(
    package_name=__package__,
    globals={
        'url_for': url_for,
    },
)


class SubPage:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_url.html')
    def index(self, **kwargs):
        _relative = cherrypy.request.headers.get('-Relative')
        return {'kwargs': {'_relative': _relative or None}}


@cherrypy.tools.proxy(base='https://www.example.com')
class ProxiedPage:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_url.html')
    def index(self, **kwargs):
        _relative = cherrypy.request.headers.get('-Relative')
        return {'kwargs': {'_relative': _relative or None}}


@cherrypy.tools.jinja2(env=env)
class Root:
    sub_page = SubPage()
    proxied = ProxiedPage()

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_url.html')
    def index(self, **kwargs):
        _relative = cherrypy.request.headers.get('-Relative')
        return {'kwargs': {'_relative': _relative or None}}


class UrlTest(helper.CPWebCase):
    default_lang = None
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def test_url_for(self):
        self.assertEqual(url_for("foo", "bar"), 'http://127.0.0.1:54583/foo/bar')
        self.assertEqual(url_for("foo", "bar", _relative='server'), '/foo/bar')
        # Outside a request, relative url doesn't make alot of sens.
        self.assertEqual(url_for("foo", "bar", _relative=1), '127.0.0.1:54583/foo/bar')
        self.assertEqual(url_for("foo", "bar", _base='http://test.com'), 'http://test.com/foo/bar')

    def test_get_page(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/")
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-url')
        # 2. Check user field
        self.assertInBody(f'Empty: http://{self.HOST}:{self.PORT}/')
        self.assertInBody(f'Dot: http://{self.HOST}:{self.PORT}/')
        self.assertInBody(f'Dot page: http://{self.HOST}:{self.PORT}/my-page')
        self.assertInBody(f'Slash: http://{self.HOST}:{self.PORT}/')
        self.assertInBody(f'Page: http://{self.HOST}:{self.PORT}/my-page')
        self.assertInBody(f'Slash page: http://{self.HOST}:{self.PORT}/my-page')
        self.assertInBody(f'Query: http://{self.HOST}:{self.PORT}/my-page?bar=test+with+space&amp;foo=1')

    def test_get_page_relative_true(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/", headers=[('_relative', '1')])
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-url')
        # 2. Check user field
        self.assertInBody('Empty: <br/>')
        self.assertInBody('Dot: <br/>')
        self.assertInBody('Dot page: my-page<br/>')
        self.assertInBody('Slash: <br/>')
        self.assertInBody('Page: my-page<br/>')
        self.assertInBody('Slash page: my-page<br/>')
        self.assertInBody('Query: my-page?bar=test+with+space&amp;foo=1<br/>')

    def test_get_page_relative_server(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/", headers=[('_relative', 'server')])
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-url')
        # 2. Check user field
        self.assertInBody('Empty: /<br/>')
        self.assertInBody('Dot: /<br/>')
        self.assertInBody('Dot page: /my-page<br/>')
        self.assertInBody('Slash: /<br/>')
        self.assertInBody('Page: /my-page<br/>')
        self.assertInBody('Slash page: /my-page<br/>')
        self.assertInBody('Query: /my-page?bar=test+with+space&amp;foo=1<br/>')

    def test_get_page_proxied(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/proxied/")
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-url')
        # 2. Check user field
        self.assertInBody('Empty: https://www.example.com/')
        self.assertInBody('Dot: https://www.example.com/proxied/')
        self.assertInBody('Dot page: https://www.example.com/proxied/my-page<br/>')
        self.assertInBody('Slash: https://www.example.com/')
        self.assertInBody('Page: https://www.example.com/my-page')
        self.assertInBody('Slash page: https://www.example.com/my-page')
        self.assertInBody('Query: https://www.example.com/my-page?bar=test+with+space&amp;foo=1')

    def test_get_sub_page(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/sub-page/")
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-url')
        # 2. Check user field
        self.assertInBody(f'Empty: http://{self.HOST}:{self.PORT}/sub-page/')
        self.assertInBody(f'Dot: http://{self.HOST}:{self.PORT}/sub-page/')
        self.assertInBody(f'Dot page: http://{self.HOST}:{self.PORT}/sub-page/my-page')
        self.assertInBody(f'Slash: http://{self.HOST}:{self.PORT}/')
        self.assertInBody(f'Page: http://{self.HOST}:{self.PORT}/my-page')
        self.assertInBody(f'Slash page: http://{self.HOST}:{self.PORT}/my-page')
        self.assertInBody(f'Query: http://{self.HOST}:{self.PORT}/my-page?bar=test+with+space&amp;foo=1')
