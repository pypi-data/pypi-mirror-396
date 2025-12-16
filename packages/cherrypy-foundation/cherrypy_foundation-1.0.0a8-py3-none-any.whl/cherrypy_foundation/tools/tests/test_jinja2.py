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
from datetime import datetime, timezone
from unittest import skipUnless

import cherrypy
from cherrypy.test import helper
from parameterized import parameterized

from .. import i18n  # noqa
from .. import jinja2  # noqa

HAS_JINJAX = importlib.util.find_spec("jinjax") is not None

env = cherrypy.tools.jinja2.create_env(
    package_name=__package__,
    globals={
        'const1': 'STATIC VALUE',
    },
)


def extra_processor():
    return {'var2': 'bar'}


@cherrypy.tools.jinja2(env=env, extra_processor=extra_processor)
class Root:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_jinja2.html')
    def index(self):
        return {'var1': 'test-jinja2'}

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_jinjax.html')
    def jinjax(self):
        return {'var1': 'test-jinjax'}

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_jinja2_i18n.html')
    @cherrypy.tools.i18n(
        default='fr',
        default_timezone='America/Toronto',
        mo_dir=importlib.resources.files(__package__) / 'locales',
        domain='messages',
    )
    def localized(self):
        return {
            'my_datetime': datetime(year=2025, month=11, day=26, hour=11, minute=16, tzinfo=timezone.utc),
            'my_date': datetime(year=2025, month=12, day=22, hour=14, minute=8, tzinfo=timezone.utc),
        }


class Jinja2Test(helper.CPWebCase):
    default_lang = None
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def test_get_page(self):
        # Given a page render using jinja2
        # When querying the page
        self.getPage("/")
        # Then the page return without error
        self.assertStatus(200)
        # Then the page is render dynamically using page context
        self.assertInBody('test-jinja2')
        self.assertInBody('bar')
        self.assertInBody('STATIC VALUE')

    @skipUnless(HAS_JINJAX, reason='Required jinjax')
    def test_get_page_jinjax(self):
        # Given a page render using jinjax
        # When querying the page
        self.getPage("/jinjax")
        # Then the page return without error
        self.assertStatus(200)
        # Then the page is render dynamically using page context
        self.assertInBody('<a class="btn btn-primary" href="http://example.com">foo</a>')

    @parameterized.expand(
        [
            ('server_default', {}, 'fr'),
            ('accept_lang_fr', {'Accept-Language': 'fr'}, 'fr'),
            ('accept_lang_en', {'Accept-Language': 'en'}, 'en'),
        ]
    )
    def test_get_page_i18n(self, _name, headers, expected_lang):
        # Given a localized page render with jinja2
        # When querying the page
        self.getPage("/localized", headers=list(headers.items()))
        # Then the page return without error
        self.assertStatus(200)
        # Then the page is render dynamically using page context
        if expected_lang == 'fr':
            self.assertInBody('lang="fr"')
            self.assertInBody('français')
            self.assertInBody('Du texte à traduire')
            self.assertInBody('mercredi 26 novembre 2025, 06:16:00 heure normale de l’Est nord-américain')
            self.assertInBody('lundi, décembre 22, 2025')
        else:
            self.assertInBody('lang="en"')
            self.assertInBody('English')
            self.assertInBody('Some text to translate')
            self.assertInBody('Wednesday, November 26, 2025, 6:16:00\u202fAM Eastern Standard Time')
            self.assertInBody('Monday, December 22, 2025')
