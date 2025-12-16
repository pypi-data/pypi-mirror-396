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


import datetime
from collections import namedtuple
from urllib.parse import urlencode

import cherrypy
from cherrypy.lib.sessions import RamSession
from cherrypy.test import helper

from ..auth import AUTH_LAST_PASSWORD_AT
from ..auth_mfa import (
    MFA_CODE_TIME,
    MFA_DEFAULT_CODE_TIMEOUT,
    MFA_DEFAULT_TRUST_DURATION,
    MFA_TRUSTED_IP_LIST,
    MFA_USER_KEY,
    MFA_VERIFICATION_TIME,
)
from ..sessions_timeout import SESSION_PERSISTENT

User = namedtuple('User', 'id,username,password,email,mfa', defaults=[False])

users = {
    User(2, 'myuser', 'changeme', 'myuser@example.com', False),
    User(3, 'mfauser', 'changeme', 'mfauser@example.com', True),
    User(4, 'noemail', 'changeme', '', True),
}


def checkpassword(username, password):
    for u in users:
        if u.username == username and u.password == password:
            return True
    return False


def user_lookup_func(login, user_info):
    for u in users:
        if u.username == login:
            return u.id, u
    return None


def user_from_key_func(userkey):
    for u in users:
        if u.id == userkey:
            return u
    return None


@cherrypy.tools.sessions()
@cherrypy.tools.auth(
    user_lookup_func=user_lookup_func,
    user_from_key_func=user_from_key_func,
    checkpassword=checkpassword,
)
@cherrypy.tools.auth_mfa(
    mfa_enabled=lambda: hasattr(cherrypy.serving.request, 'currentuser') and cherrypy.request.currentuser.mfa
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

    @cherrypy.expose()
    def mfa(self, code=None, resend_code=None, persistent=False):
        html = "mfa\n"
        if cherrypy.serving.request.method == 'POST' and code:
            if cherrypy.tools.auth_mfa.verify_code(code=code, persistent=persistent):
                raise cherrypy.tools.auth.redirect_to_original_url()
            else:
                html += "<p>invalid verification code</p>\n"
        # Send verification code if previous code expired.
        # Or when requested by user.
        if (resend_code and cherrypy.serving.request.method == 'POST') or cherrypy.tools.auth_mfa.is_code_expired():
            code = cherrypy.tools.auth_mfa.generate_code()
            # Here the code should be send by email, SMS or any other means.
            # For our test we store it in the session.
            cherrypy.serving.session['code'] = code
            html += "<p>new verification code sent to your email</p>\n"
        return html


class AuthManagerMfaTest(helper.CPWebCase):
    interactive = False
    # Authenticated by default.
    login = True

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def getPage(self, *args, **kwargs):
        """
        This implementation keep track of session cookies.
        """
        headers = kwargs.pop('headers', [])
        if hasattr(self, 'cookies') and self.cookies:
            headers.extend(self.cookies)
        return helper.CPWebCase.getPage(self, *args, headers=headers, **kwargs)

    def _login(self, username, password):
        self.getPage('/login/', method='POST', body=urlencode({'username': username, 'password': password}))
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')

    @property
    def _session_id(self):
        if hasattr(self, 'cookies') and self.cookies:
            for unused, value in self.cookies:
                for part in value.split(';'):
                    key, unused, value = part.partition('=')
                    if key == 'session_id':
                        return value

    def _get_code(self):
        # Query MFA page to generate a code
        self.getPage("/mfa/")
        self.assertStatus(200)
        self.assertInBody("new verification code sent to your email")
        # Extract code from user session for testing only.
        session = RamSession.cache[self._session_id][0]
        return session['code']

    def test_get_without_login(self):
        # Given the user is not authenticated.
        # When requesting /mfa/
        self.getPage("/mfa/")
        # Then user is redirected to /login/
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/login/')

    def test_get_with_mfa_disabled(self):
        # Given an authenticated user with MFA Disable
        self._login('myuser', 'changeme')
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')
        # Then index is enabled.
        self.getPage("/")
        self.assertStatus(200)
        self.assertInBody('OK')

    def test_get_with_trusted(self):
        # Given an authenticated user with MFA Disable
        self._login('mfauser', 'changeme')
        # Given an authenticated user with MFA enabled and already verified
        session = RamSession.cache[self._session_id][0]
        session[MFA_USER_KEY] = 3
        session[MFA_VERIFICATION_TIME] = datetime.datetime.now()
        session[MFA_TRUSTED_IP_LIST] = ['127.0.0.1']

        # When requesting /mfa/ page when we are already trusted
        self.getPage("/mfa/")
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')

    def test_get_with_trusted_expired(self):
        # Given an authenticated user with MFA enabled and already verified
        self._login('mfauser', 'changeme')
        session = RamSession.cache[self._session_id][0]
        session[MFA_USER_KEY] = 3
        session[MFA_VERIFICATION_TIME] = datetime.datetime.now() - datetime.timedelta(minutes=60)

        # When requesting /mfa/ page
        self.getPage("/mfa/")
        self.assertStatus(200)
        # Then a verification code is send to the user
        self.assertInBody("new verification code sent to your email")

    def test_get_with_trusted_different_ip(self):
        # Given an authenticated user with MFA enabled and already verified
        self._login('mfauser', 'changeme')
        session = RamSession.cache[self._session_id][0]
        session[MFA_USER_KEY] = 3
        session[MFA_VERIFICATION_TIME] = datetime.datetime.now()

        # When requesting /mfa/ page from a different ip
        self.getPage("/mfa/", headers=[('X-Forwarded-For', '10.255.14.23')])
        self.assertStatus(200)
        # Then a verification code is send to the user
        self.assertInBody("new verification code sent to your email")

    def test_get_without_verified(self):
        # Given an authenticated user With MFA enabled
        self._login('mfauser', 'changeme')
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        self.assertStatus(200)
        # Then a verification code is send to the user
        self.assertInBody("new verification code sent to your email")

    def test_verify_code_valid(self):
        prev_session_id = self._session_id
        # Given an authenticated user With MFA enabled
        self._login('mfauser', 'changeme')
        code = self._get_code()
        # When sending a valid verification code
        self.getPage("/mfa/", method='POST', body=urlencode({'code': code}))
        # Then a new session_id is generated
        self.assertNotEqual(prev_session_id, self._session_id)
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')
        # Then user has access
        self.getPage("/")
        self.assertStatus(200)

    def test_verify_code_invalid(self):
        # Given an authenticated user With MFA enabled
        # When sending an invalid verification code
        self.getPage("/mfa/", method='POST', body=urlencode({'code': '1234567'}))
        # Then user is redirected to login page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/login/')

    def test_verify_code_expired(self):
        # Given an authenticated user With MFA enabled
        self._login('mfauser', 'changeme')
        code = self._get_code()
        # When sending a valid verification code that expired
        session = RamSession.cache[self._session_id][0]

        session[MFA_CODE_TIME] = datetime.datetime.now() - datetime.timedelta(minutes=MFA_DEFAULT_CODE_TIMEOUT + 1)

        self.getPage("/mfa/", method='POST', body=urlencode({'code': code}))
        # Then a new code get generated.
        self.assertStatus(200)
        self.assertInBody("invalid verification code")

    def test_verify_code_invalid_after_3_tentative(self):
        # Given an authenticated user With MFA
        self._login('mfauser', 'changeme')
        code = self._get_code()
        # When user enter an invalid verification code 3 times
        self.getPage("/mfa/", method='POST', body=urlencode({'code': '1234567'}))
        self.assertStatus(200)
        self.getPage("/mfa/", method='POST', body=urlencode({'code': '1234567'}))
        self.assertStatus(200)
        self.getPage("/mfa/", method='POST', body=urlencode({'code': '1234567'}))
        # Then an error get displayed to the user
        self.assertStatus(200)
        self.assertInBody("invalid verification code")
        # Then a new code get send to the user.
        self.assertInBody("new verification code sent to your email")
        session = RamSession.cache[self._session_id][0]
        new_code = session['code']
        self.assertNotEqual(code, new_code)

    def test_resend_code(self):
        # Given an authenticated user With MFA enabled with an existing code
        self._login('mfauser', 'changeme')
        code = self._get_code()
        # When user request a new code
        self.getPage("/mfa/", method='POST', body=urlencode({'resend_code': '1'}))
        # Then A success message is displayedto the user.
        self.assertInBody("new verification code sent to your email")
        session = RamSession.cache[self._session_id][0]
        new_code = session['code']
        self.assertNotEqual(code, new_code)

    def test_redirect_to_original_url(self):
        # Given an authenticated user
        self._login('mfauser', 'changeme')
        # When querying a page that required mfa
        self.getPage('/prefs/general')
        # Then user is redirected to mfa page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/mfa/')
        # When providing verification code
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body=urlencode({'code': code}))
        # Then user is redirected to original url
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/prefs/general')

    def test_login_persistent_when_login_timeout(self):
        prev_session_id = self._session_id
        # Given a user authenticated with MFA with "persistent"
        self._login('mfauser', 'changeme')
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body=urlencode({'code': code, 'persistent': '1'}))
        self.assertStatus(303)
        self.getPage("/")
        self.assertStatus(200)
        self.assertNotEqual(prev_session_id, self._session_id)
        session = RamSession.cache[self._session_id][0]
        self.assertTrue(session[SESSION_PERSISTENT])
        # When the re-auth time expired (after 15 min)
        session[AUTH_LAST_PASSWORD_AT] = datetime.datetime.now() - datetime.timedelta(minutes=60, seconds=1)

        # Then next query redirect user to /login/ page (by mfa)
        self.getPage("/")
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/login/')
        prev_session_id = self._session_id
        # When user enter valid username password
        self.getPage("/login/", method='POST', body=urlencode({'username': 'mfauser', 'password': 'changeme'}))
        # Then user is redirected to original url without need to pass MFA again.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/')
        self.assertNotEqual(prev_session_id, self._session_id)
        self.getPage("/")
        self.assertStatus(200)
        self.assertInBody('OK')

    def test_login_persistent_when_mfa_timeout(self):
        prev_session_id = self._session_id
        # Given a user authenticated with MFA with "persistent"
        self._login('mfauser', 'changeme')
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body=urlencode({'code': code, 'persistent': '1'}))
        self.assertStatus(303)
        self.getPage("/")
        self.assertStatus(200)
        self.assertNotEqual(prev_session_id, self._session_id)
        session = RamSession.cache[self._session_id][0]

        self.assertTrue(session[SESSION_PERSISTENT])
        # When the mfa verification timeout (after 15 min)
        session[MFA_VERIFICATION_TIME] = datetime.datetime.now() - datetime.timedelta(
            minutes=MFA_DEFAULT_TRUST_DURATION, seconds=1
        )

        # Then next query redirect user to mfa page
        self.getPage("/prefs/general")
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/mfa/')
        # When user enter valid code
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body=urlencode({'code': code, 'persistent': '1'}))
        # Then user is redirected to original page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'http://{self.HOST}:{self.PORT}/prefs/general')
        self.getPage("/")
        self.assertStatus(200)
        self.assertInBody('OK')
