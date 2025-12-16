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


from collections import namedtuple
from urllib.parse import urlencode

import cherrypy
from cherrypy.test import helper

from .. import auth  # noqa

User = namedtuple('User', 'id,username')


def checkpassword(username, password):
    return username == 'myuser' and password == 'changeme'


def user_lookup_func(login, user_info):
    if login == 'myuser':
        return login, User(2, login)
    return None


def user_from_key_func(userkey):
    if userkey == 'myuser':
        return User(2, 'myuser')
    return None


@cherrypy.tools.sessions()
@cherrypy.tools.auth(
    user_lookup_func=user_lookup_func,
    user_from_key_func=user_from_key_func,
    checkpassword=checkpassword,
)
class Root:

    @cherrypy.expose
    def index(self):
        return "OK"

    @cherrypy.expose()
    def login(self, username=None, password=None):
        if cherrypy.serving.request.method == 'POST' and username and password:
            userobj = cherrypy.tools.auth.login_with_credentials(username, password)
            if userobj:
                raise cherrypy.tools.auth.redirect_to_original_url()
            else:
                return "invalid credentials"
        return "login"


class AuthManagerTest(helper.CPWebCase):
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def test_auth_redirect(self):
        # Given unauthenticated user
        # When requesting protected page
        self.getPage('/')
        # Then user is redirected to login page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/login/')

    def test_auth_login(self):
        # Given unauthenticated user
        # When posting valid login
        self.getPage('/login/', method='POST', body=urlencode({'username': 'myuser', 'password': 'changeme'}))
        # Then user is redirect to index.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')
        # Then page is accessible
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        self.assertInBody('OK')
