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

from collections import namedtuple

import cherrypy

FlashMessage = namedtuple('FlashMessage', ['message', 'level'])


def flash(message, level='info'):
    """
    Add a flash message to the session.
    """
    assert message
    assert level in ['info', 'error', 'warning', 'success']
    if 'flash' not in cherrypy.session:
        cherrypy.session['flash'] = []
    # Support Markup and string
    if hasattr(message, '__html__'):
        flash_message = FlashMessage(message, level)
    else:
        flash_message = FlashMessage(str(message), level)
    cherrypy.session['flash'].append(flash_message)


def get_flashed_messages():
    """
    Return all flash message.
    """
    if 'flash' in cherrypy.session:
        messages = cherrypy.session['flash']
        del cherrypy.session['flash']
        return messages
    return []
