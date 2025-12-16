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

import json
import logging

import cherrypy

HTML_ERROR_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>
    <title>%(status)s</title>
    <style type="text/css">
    #powered_by {
        margin-top: 20px;
        border-top: 2px solid black;
        font-style: italic;
    }

    #traceback {
        color: red;
    }
    </style>
</head>
    <body>
        <h2>%(status)s</h2>
        <p>%(message)s</p>
        <pre id="traceback">%(traceback)s</pre>
    <div id="powered_by">
      <span>
        Powered by <a href="http://www.cherrypy.dev">CherryPy %(version)s</a>
      </span>
    </div>
    </body>
</html>
'''


def error_page(status='', message='', traceback='', version=''):
    """
    Error page handler to handle Plain Text (text/plain), Json (application/json) or HTML (text/html) output.

    If available, uses Jina2 environment to generate error page using `error_page.html`.
    """
    # Log server error exception
    if status.startswith('500'):
        cherrypy.log(
            f'error page status={status} message={message}\n{traceback}', context='ERROR-PAGE', severity=logging.WARNING
        )

    # Replace message by generic one for 404. Default implementation leak path info.
    if status == '404 Not Found' and cherrypy.serving.request.path_info in message:
        message = 'Nothing matches the given URI'

    # Check expected response type.
    mtype = cherrypy.serving.response.headers.get('Content-Type') or cherrypy.tools.accept.callable(
        ['text/html', 'text/plain', 'application/json']
    )
    if mtype == 'text/plain':
        return message
    elif mtype == 'application/json':
        return json.dumps({'message': message, 'status': status})
    elif mtype == 'text/html':
        context = {'status': status, 'message': message, 'traceback': traceback, 'version': version}
        if hasattr(cherrypy.tools, 'jinja2'):
            # Try to build a nice error page with Jinja2 env
            try:
                return cherrypy.tools.jinja2.render_request(template='error_page.html', context=context)
            except Exception:
                cherrypy.log(
                    'fail to render error page with jinja2',
                    context='ERROR-PAGE',
                    severity=logging.ERROR,
                    traceback=True,
                )
        # Fallback to built-int HTML error page
        return HTML_ERROR_TEMPLATE % context

    # Fallback to raw error message.
    return message
