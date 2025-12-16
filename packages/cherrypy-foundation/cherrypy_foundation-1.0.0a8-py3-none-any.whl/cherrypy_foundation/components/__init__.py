# Cherrypy Foundation
# Copyright (C) 2025 IKUS Software inc.
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

RE_STATIC_MATCH = r"(\.js|\.css|\.png|\.woff|\.woff2|\.map)$"


@cherrypy.config(
    **{
        'tools.auth.on': False,
        'tools.auth_mfa.on': False,
        'tools.i18n.on': False,
        'tools.ratelimit.on': False,
        'tools.secure_headers.on': False,
        'tools.sessions.on': False,
    }
)
class StaticMiddleware:

    @cherrypy.expose
    @cherrypy.tools.staticdir(match=RE_STATIC_MATCH, dir=str(importlib.resources.files(__package__)))
    def default(self, *args, **kwargs):
        """This entry point is used to serve content of /static/components/ folder and JinjaX static ressources"""
        # Make use of JinjaX catalog
        env = cherrypy.request.config.get('tools.jinja2.env')
        if env is None or 'catalog' not in env.globals:
            raise cherrypy.HTTPError(400)

        # JinjaX resources could be locaed in multiple path.
        section = cherrypy.serving.request.toolmaps['tools']['staticdir']['section']
        jinjax_catalog = env.globals['catalog']
        for path in jinjax_catalog.paths:
            handled = cherrypy.lib.static.staticdir(section=section, match=RE_STATIC_MATCH, dir=path)
            if handled:
                return cherrypy.serving.response.body
        raise cherrypy.HTTPError(400)
