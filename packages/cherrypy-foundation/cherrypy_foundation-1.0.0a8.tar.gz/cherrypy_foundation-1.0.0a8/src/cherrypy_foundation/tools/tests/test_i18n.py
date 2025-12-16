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

import gettext
import importlib.resources
import unittest
from datetime import datetime, timezone

import cherrypy
from cherrypy import _cpconfig
from cherrypy.test import helper

from .. import i18n

TEXT_EN = 'Some text to translate'
TEXT_FR = 'Du texte à traduire'


class TestI18n(unittest.TestCase):
    def setUp(self):
        self.mo_dir = importlib.resources.files(__package__) / 'locales'
        self.assertTrue(self.mo_dir.is_dir())
        cherrypy.request.config = _cpconfig.Config()

    def test_search_translation_en(self):
        # Load default translation return translation
        t = i18n._search_translation(self.mo_dir, 'messages', 'en')
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", t.locale.language)
        # Test translation object
        self.assertEqual(TEXT_EN, t.gettext(TEXT_EN))

    def test_search_translation_fr(self):
        # Custom lang return translation.
        t = i18n._search_translation(self.mo_dir, 'messages', 'fr')
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", t.locale.language)
        # Test translation object
        self.assertEqual(TEXT_FR, t.gettext(TEXT_EN))

    def test_search_translation_invalid(self):
        # Load invalid translation return None
        t = i18n._search_translation(self.mo_dir, 'messages', 'tr')
        self.assertIsNone(t)


class Root:

    @cherrypy.expose
    @cherrypy.tools.i18n(on=True)
    def index(self):
        return i18n.gettext(TEXT_EN)


class AbstractI18nTest(helper.CPWebCase):
    default_lang = None
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'tools.i18n.default': cls.default_lang,
                'tools.i18n.mo_dir': importlib.resources.files(__package__) / 'locales',
                'tools.i18n.domain': 'messages',
            }
        )
        cherrypy.tree.mount(Root(), '/')


class TestI18nWebCase(AbstractI18nTest):

    def test_language_with_unknown(self):
        #  Query the page without login-in
        self.getPage("/", headers=[("Accept-Language", "it")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody(TEXT_EN)

    def test_language_en(self):
        self.getPage("/", headers=[("Accept-Language", "en-US,en;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody(TEXT_EN)

    def test_language_en_fr(self):
        self.getPage("/", headers=[("Accept-Language", "en-US,en;q=0.8,fr-CA;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody(TEXT_EN)

    def test_language_fr(self):
        self.getPage("/")
        self.assertInBody(TEXT_EN)
        self.getPage("/", headers=[("Accept-Language", "fr-CA;q=0.8,fr;q=0.6")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "fr")
        self.assertInBody(TEXT_FR)

    def test_with_preferred_lang(self):
        # Given a default lang 'en'
        date = datetime.fromtimestamp(1680111611, timezone.utc)
        self.assertEqual(TEXT_EN, i18n.ugettext(TEXT_EN))
        self.assertIn('March', i18n.format_datetime(date, format='long'))
        # When using preferred_lang with french
        with i18n.preferred_lang('fr'):
            # Then french translation is used
            self.assertEqual(TEXT_FR, i18n.ugettext(TEXT_EN))
            # Then date time formating used french locale
            self.assertIn('mars', i18n.format_datetime(date, format='long'))
        # Then ouside the block, settings goest back to english
        self.assertEqual(TEXT_EN, i18n.ugettext(TEXT_EN))
        self.assertIn('March', i18n.format_datetime(date, format='long'))


class TestI18nDefaultLangWebCase(AbstractI18nTest):
    default_lang = 'FR'

    @classmethod
    def teardown_class(cls):
        # Reset default-lang to avoid issue with other test
        cherrypy.config['tools.i18n.default'] = 'en'
        super().teardown_class()

    def test_default_lang_without_accept_language(self):
        # Given a default language
        # When user connect to the application without Accept-Language
        self.getPage("/")
        self.assertStatus(200)
        # Then page is displayed with default lang
        self.assertInBody(TEXT_FR)

    def test_default_lang_with_accept_language(self):
        # Given a default language
        # When user connect to the application with Accept-Language English
        self.getPage("/", headers=[("Accept-Language", "en-US,en;q=0.8")])
        self.assertStatus(200)
        # Then page is displayed as english
        self.assertInBody(TEXT_EN)

    def test_default_lang_with_unknown_accept_language(self):
        # Given a default language
        # When user connect to the application with Accept-Language English
        self.getPage("/", headers=[("Accept-Language", "it")])
        self.assertStatus(200)
        # Then page is displayed as english
        self.assertInBody(TEXT_FR)


class TestI18nInvalidDefaultLangWebCase(AbstractI18nTest):
    default_lang = 'invalid'

    def test_default_lang_invalid(self):
        # Given an invalid default language
        # When user connect to the application without Accept-Language
        self.getPage("/")
        self.assertStatus(200)
        # Then page is displayed with fallback to "en"
        self.assertInBody(TEXT_EN)
