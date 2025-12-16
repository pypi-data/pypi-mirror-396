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

import importlib.resources

import cherrypy
from cherrypy.test import helper
from parameterized import parameterized

from .. import StaticMiddleware


class Static:

    components = StaticMiddleware()


class Root:

    static = Static()

    @cherrypy.expose
    def index(self):
        return "OK"


class StaticMiddlewareTest(helper.CPWebCase):
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

    @parameterized.expand(
        [
            '/static/components/Datatable.css',
            '/static/components/Datatable.js',
            '/static/components/Field.css',
            '/static/components/Field.js',
            '/static/components/SideBySideMultiSelect.css',
            '/static/components/SideBySideMultiSelect.js',
            '/static/components/Typeahead.css',
            '/static/components/Typeahead.js',
            '/static/components/vendor/bootstrap5/css/bootstrap.min.css',
            '/static/components/vendor/bootstrap5/js/bootstrap.min.js',
            '/static/components/vendor/datatables-extensions/Buttons/css/buttons.dataTables.min.css',
            '/static/components/vendor/datatables-extensions/Buttons/js/buttons.html5.min.js',
            '/static/components/vendor/datatables-extensions/Buttons/js/dataTables.buttons.min.js',
            '/static/components/vendor/datatables-extensions/FixedHeader/css/fixedHeader.dataTables.css',
            '/static/components/vendor/datatables-extensions/FixedHeader/js/dataTables.fixedHeader.min.js',
            '/static/components/vendor/datatables-extensions/JSZip/jszip.min.js',
            '/static/components/vendor/datatables-extensions/pdfmake/build/pdfmake.min.js',
            '/static/components/vendor/datatables-extensions/pdfmake/build/vfs_fonts.js',
            '/static/components/vendor/datatables-extensions/Responsive/css/responsive.dataTables.min.css',
            '/static/components/vendor/datatables-extensions/Responsive/js/dataTables.responsive.min.js',
            '/static/components/vendor/datatables-extensions/rowgroup/css/rowGroup.dataTables.min.css',
            '/static/components/vendor/datatables-extensions/rowgroup/js/dataTables.rowGroup.js',
            '/static/components/vendor/datatables/css/dataTables.dataTables.css',
            '/static/components/vendor/datatables/js/dataTables.min.js',
            '/static/components/vendor/jquery/jquery.min.js',
            '/static/components/vendor/popper/popper.min.js',
            '/static/components/vendor/typeahead/jquery.typeahead.min.css',
            '/static/components/vendor/typeahead/jquery.typeahead.min.js',
            '/static/components/vendor/typeahead/jquery.typeahead.min.js',
        ]
    )
    def test_static(self, url):
        self.getPage(url)
        self.assertStatus(200)
