# CherryPy Foundation
# Copyright (C) 2020-2025 IKUS Software
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
from markupsafe import Markup


class JinjaWidget:
    """
    Create field widget from Jinja2 templates.
    """

    filename = None

    def __init__(self, **options):
        self.options = options

    def __call__(self, field, **kwargs):
        env = cherrypy.request.config.get('tools.jinja2.env')
        kwargs = dict(self.options, **kwargs)
        # Support JinjaX
        if self.filename.endswith('.jinja'):
            catalog = env.globals['catalog']
            return catalog.irender(self.filename[0:-6], field=field, **kwargs)
        else:
            tmpl = env.get_template(self.filename)
            return Markup(tmpl.render(field=field, **kwargs))


class SwitchWidget(JinjaWidget):
    filename = 'SwitchWidget.jinja'


class SideBySideMultiSelect(JinjaWidget):
    filename = 'SideBySideMultiSelect.jinja'
