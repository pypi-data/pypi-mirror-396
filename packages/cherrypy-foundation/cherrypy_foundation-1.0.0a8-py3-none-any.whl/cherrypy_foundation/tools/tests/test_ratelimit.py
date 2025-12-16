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

import tempfile

import cherrypy
from cherrypy.test import helper

from .. import ratelimit  # noqa


class Root:

    @cherrypy.expose
    def index(self):
        return "OK"

    @cherrypy.expose
    @cherrypy.tools.ratelimit(on=True, methods=['POST'])
    def login(self):
        return "login"


class RateLimitTest(helper.CPWebCase):
    interactive = False
    rate_limit = 5
    rate_limit_dir = None

    def setUp(self):
        cherrypy.tools.ratelimit.reset()
        return super().setUp()

    def tearDown(self):
        cherrypy.tools.ratelimit.reset()
        return super().tearDown()

    @classmethod
    def setup_server(cls):
        rate_limit_storage_class = ratelimit.RamRateLimit
        if cls.rate_limit_dir:
            rate_limit_storage_class = ratelimit.FileRateLimit
        cherrypy.config.update(
            {
                'tools.ratelimit.debug': True,
                'tools.ratelimit.delay': 3600,
                'tools.ratelimit.limit': cls.rate_limit,
                'tools.ratelimit.storage_class': rate_limit_storage_class,
                'tools.ratelimit.storage_path': cls.rate_limit_dir,
            }
        )
        cherrypy.tree.mount(Root(), '/')

    def test_ratelimit(self):
        # Given a endpoint with ratelimit enabled
        # When requesting multiple time the page
        for i in range(0, 5):
            self.getPage('/login', method='POST')
            self.assertStatus(200)
        # Then a 429 error (too many request) is return
        self.getPage('/login', method='POST')
        self.assertStatus(429)

    def test_ratelimit_forwarded_for(self):
        # Given a endpoint with ratelimit enabled
        # When requesting multiple time the login page with different `X-Forwarded-For`
        for i in range(0, 5):
            self.getPage(
                '/login',
                headers=[('X-Forwarded-For', '127.0.0.%s' % i)],
                method='POST',
            )
            self.assertStatus(200)
        # Then original IP get blocked
        self.getPage(
            '/login',
            headers=[('X-Forwarded-For', '127.0.0.%s' % i)],
            method='POST',
        )
        self.assertHeaderItemValue('X-Ratelimit-Limit', '5')
        self.assertHeaderItemValue('X-Ratelimit-Remaining', '0')
        self.assertHeader('X-Ratelimit-Reset')
        self.assertStatus(429)


class FileStorageRateLimitTest(RateLimitTest):

    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.TemporaryDirectory(prefix='cherrypy-foundation-', suffix='-ratelimit-test')
        cls.rate_limit_dir = cls.tempdir.name
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        cls.tempdir.cleanup()
        super().teardown_class()
