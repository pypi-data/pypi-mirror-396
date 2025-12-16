# CherryPy Foundation
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

from urllib.parse import urljoin

import cherrypy


def url_for(*args, _relative=None, _base=None, **kwargs):
    """
    Generate a URL for the given endpoint/path (*args) with query params (**kwargs).

    relative:
      - None: pass through to cherrypy.url (CherryPy default behavior).
      - False: absolute URL (scheme, host, vhost, script_name).
      - True: URL relative to current request path (may include '..').
      - 'server': URL relative to server root (starts with '/').
    Notes:
      - String chunks have leading/trailing slashes stripped and are joined with '/'.
      - Chunks '.' and '..' are allowed as literals (for relative paths).
      - Objects may implement __url_for__() -> str or have a string .url_for attribute.
      - Integers are appended as path segments.
      - When path == "", existing request query parameters are merged (kwargs win).
    """
    # Handle query-string
    qs = [(k, v) for k, v in sorted(kwargs.items()) if v is not None]

    path = []
    for chunk in args:
        if hasattr(chunk, '__url_for__') and callable(chunk.__url_for__):
            path.append(str(chunk.__url_for__()))
        elif hasattr(chunk, 'url_for'):
            path.append(str(chunk.url_for))
        elif isinstance(chunk, str):
            path.append(chunk)
        elif isinstance(chunk, int):
            path.append(str(chunk))
        else:
            raise ValueError('invalid positional arguments, url_for accept str, bytes, int: %r' % chunk)
    path = '/'.join(path)
    # When path is empty, we are browsing the same page.
    # Let keep the original query_string to avoid loosing it.
    if not path:
        params = cherrypy.request.params.copy()
        params.update(kwargs)
        qs = [(k, v) for k, v in sorted(params.items()) if v is not None]
    elif not path.startswith('.'):
        path = urljoin('/', path)
    # Outside a request, use cherrypy.tools.proxy config
    if not cherrypy.request.app:
        if _base is None:
            _base = cherrypy.config.get('tools.proxy.base', None)
    # Use cherrypy to build the URL
    return cherrypy.url(path=path, qs=qs, relative=_relative, base=_base)
