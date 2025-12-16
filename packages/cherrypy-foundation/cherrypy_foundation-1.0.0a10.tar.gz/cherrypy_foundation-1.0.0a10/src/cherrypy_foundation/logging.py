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

import logging
import logging.handlers
import sys

import cherrypy


def _coerce_level(level):
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        lvl = logging._nameToLevel.get(level.upper())
        if isinstance(lvl, int):
            return lvl
    raise ValueError(f"Invalid log level: {level!r}")


def _remove_cherrypy_date(record):
    """Remove the leading date for cherrypy error."""
    if record.name.startswith('cherrypy.error'):
        record.msg = record.msg[23:].strip()
    return True


def _add_ip(record):
    """Add request IP to record."""
    # Check if we are serving a real request
    if cherrypy.request and cherrypy.request.request_line:
        remote = cherrypy.request.remote
        record.ip = remote.name or remote.ip
    else:
        record.ip = "-"
    return True


def _add_username(record):
    """Add current username to record."""
    # Check if we are serving a real request
    if cherrypy.request and cherrypy.request.request_line:
        if cherrypy.request.login:
            record.user = cherrypy.request.login
        else:
            record.user = "anonymous"
    else:
        record.user = "-"
    return True


def setup_logging(log_file, log_access_file, level):
    """
    Configure the logging system for CherryPy.
    Safe to call multiple times.
    """
    lvl = _coerce_level(level)

    cherrypy.config.update({'log.screen': False, 'log.access_file': '', 'log.error_file': ''})
    cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)

    # Configure root logger
    logger = logging.getLogger('')
    logger.level = lvl
    # Capture warnings
    logging.captureWarnings(True)
    if log_file:
        print("continue logging to %s" % log_file)
        default_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=20)
    else:
        default_handler = logging.StreamHandler(sys.stdout)
    default_handler.addFilter(_remove_cherrypy_date)
    default_handler.addFilter(_add_ip)
    default_handler.addFilter(_add_username)
    default_handler.setFormatter(
        logging.Formatter("[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s")
    )
    logger.addHandler(default_handler)

    # Configure cherrypy access logger
    cherrypy_access = logging.getLogger('cherrypy.access')
    cherrypy_access.propagate = False
    if log_access_file:
        handler = logging.handlers.RotatingFileHandler(log_access_file, maxBytes=10485760, backupCount=20)
        cherrypy_access.addHandler(handler)

    # Configure cherrypy error logger
    cherrypy_error = logging.getLogger('cherrypy.error')
    cherrypy_error.propagate = False
    cherrypy_error.addHandler(default_handler)
