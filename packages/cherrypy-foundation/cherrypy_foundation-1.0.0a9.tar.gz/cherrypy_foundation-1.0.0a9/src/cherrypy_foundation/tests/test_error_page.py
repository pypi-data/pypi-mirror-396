# CherryPy
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
from parameterized import parameterized

from ..error_page import error_page


class Root:

    @cherrypy.expose
    def index(self):
        return "OK"

    @cherrypy.expose
    def not_found(self):
        raise cherrypy.NotFound()

    @cherrypy.expose
    def not_found_custom(self):
        raise cherrypy.HTTPError(404, message='My error message')

    @cherrypy.expose
    def html_error(self):
        raise cherrypy.HTTPError(400, message='My error message')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def json_error(self):
        raise cherrypy.HTTPError(400, message='json error message')

    @cherrypy.expose
    @cherrypy.tools.response_headers(headers=[('Content-Type', 'text/plain')])
    def text_error(self):
        raise cherrypy.HTTPError(400, message='text error message')


class ErrorPageTest(helper.CPWebCase):
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'error_page.default': error_page,
            }
        )
        cherrypy.tree.mount(Root(), '/')

    @parameterized.expand(
        [
            ('/not_found', '<p>Nothing matches the given URI</p>'),
            ('/not_found_custom', '<p>My error message</p>'),
            ('/html_error', '<p>My error message</p>'),
            ('/json_error', '{"message": "json error message", "status": "400 Bad Request"}'),
            ('/text_error', 'text error message'),
        ]
    )
    def test_error_page(self, page, expect_body):
        # When query return an error
        self.getPage(page)
        # then error page adjust the content
        self.assertInBody(expect_body)
