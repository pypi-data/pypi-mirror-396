# Jinja2 tools for cherrypy
# Copyright (C) 2021-2025 Patrik Dufresne
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
import logging
import time

import cherrypy
import jinja2

# Sentinel value
_UNDEFINED = object()

# Capture epoch time to invalidate cache of static file.
_cache_invalidate = int(time.time())


class Jinja2Tool(cherrypy.Tool):
    """
    Jinja2 Tool for CherryPy.
    """

    def __init__(self):
        super().__init__('before_handler', self._wrap_handler, 'jinja2', priority=30)

    def _finalize_assets(self, catalog, html):
        """
        Replace the placeholder token in the rendered HTML with the fully
        formatted asset tags, then reset asset state for the next render.
        """
        assets_html = catalog._format_collected_assets()
        assets_html = str(assets_html).replace('<script type="module" ', '<script ')
        catalog._emit_assets_later = False
        catalog.collected_css = []
        catalog.collected_js = []
        return str(html).replace(catalog._assets_placeholder, assets_html)

    def _wrap_handler(self, env, template, extra_processor=None, debug=False):

        def wrap(*args, **kwargs):
            # Call original handler
            context = self.oldhandler(*args, **kwargs)
            # Render template.
            return self.render_request(env=env, template=template, context=context, extra_processor=extra_processor)

        request = cherrypy.serving.request
        if request.handler is not None:
            # Replace request.handler with self
            if debug:
                cherrypy.log('replacing request handler', context='TOOLS.JINJA2', severity=logging.DEBUG)
            self.oldhandler = request.handler
            request.handler = wrap

    def create_env(self, package_name, filters={}, globals={}, tests={}):
        """
        Utility function used to create a default Jinja2 environment with good default.
        """
        env = jinja2.Environment(
            loader=jinja2.PackageLoader(package_name),
            auto_reload=True,
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Param to bust caches
        env.globals['cache_invalidate'] = _cache_invalidate

        # Enable translation if available
        if hasattr(cherrypy.tools, 'i18n'):
            from .i18n import format_date, format_datetime, get_language_name, get_translation, ugettext, ungettext

            env.add_extension('jinja2.ext.i18n')
            env.install_gettext_callables(ugettext, ungettext, newstyle=True)
            env.filters['format_date'] = format_date
            env.filters['format_datetime'] = format_datetime
            env.globals['get_language_name'] = get_language_name
            env.globals['get_translation'] = get_translation

        # Update globals, filters and tests
        env.globals.update(globals)
        env.filters.update(filters)
        env.tests.update(tests)

        # Enable JinjaX if available
        try:
            import jinjax

            env.add_extension(jinjax.JinjaX)
            catalog = jinjax.Catalog(jinja_env=env, root_url="/static/components/")
            catalog.add_folder(importlib.resources.files(package_name) / 'components')
            catalog.add_folder(importlib.resources.files(__package__) / '..' / 'components')
        except ImportError:
            pass

        return env

    def render_request(self, template, context={}, env=_UNDEFINED, extra_processor=_UNDEFINED):
        """
        Render template for a given cherrypy request.
        """
        request = cherrypy.serving.request
        if env is _UNDEFINED:
            env = request.config.get('tools.jinja2.env')
        if extra_processor is _UNDEFINED:
            extra_processor = request.config.get('tools.jinja2.extra_processor')
        # Execute extra processor if defined.
        new_context = {}
        if extra_processor:
            new_context.update(extra_processor())
        new_context.update(context)
        # Render templates
        return self.render(env=env, template=template, context=new_context)

    def render(self, env, template, context={}):
        """
        Lower level function used to render a template using the given jinja2 environment, template(s) and variable context.
        """
        # Get the right templates
        if isinstance(template, (list, tuple)):
            names = [t.format(**context) for t in template]
            tmpl = env.select_template(names)
        else:
            tmpl = env.get_template(template)
        out = tmpl.render(context)

        # With JinjaX > 0.60 render explicitly here.
        if 'catalog' in env.globals and getattr(env.globals['catalog'], '_emit_assets_later', False):
            return self._finalize_assets(catalog=env.globals['catalog'], html=out)
        return out


cherrypy.tools.jinja2 = Jinja2Tool()
