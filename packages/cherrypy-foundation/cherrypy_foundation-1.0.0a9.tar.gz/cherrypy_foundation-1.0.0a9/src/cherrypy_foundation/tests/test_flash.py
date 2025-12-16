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
import importlib
from unittest import skipUnless

import cherrypy
from cherrypy.test import helper

import cherrypy_foundation.tools.jinja2  # noqa
from cherrypy_foundation.flash import flash, get_flashed_messages

HAS_JINJAX = importlib.util.find_spec("jinjax") is not None

env = cherrypy.tools.jinja2.create_env(
    package_name=__package__,
    globals={'get_flashed_messages': get_flashed_messages},
)


@cherrypy.tools.sessions()
@cherrypy.tools.jinja2(env=env)
class Root:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_flash.html')
    def index(self):
        flash('default flash message', level='info')
        return {}


@skipUnless(HAS_JINJAX, reason='Required jinjax')
class FormTest(helper.CPWebCase):
    default_lang = None
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def test_get_flash(self):
        # Given a page returning a flash message
        # When querying the page that include this form
        self.getPage("/")
        self.assertStatus(200)
        # Then page display the message.
        self.assertInBody('test-flash')
        self.assertInBody('<div class="alert alert-info alert-dismissible fade show"')
        self.assertInBody('default flash message')
