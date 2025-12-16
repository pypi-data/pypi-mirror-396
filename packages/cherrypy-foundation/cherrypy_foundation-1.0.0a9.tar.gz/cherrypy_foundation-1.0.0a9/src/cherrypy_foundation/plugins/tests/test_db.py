# Cherrypy Foundation
# Copyright (C) 2022-2025 IKUS Software
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
import tempfile
import unittest
from urllib.parse import urlencode

import cherrypy
from cherrypy.test import helper

HAS_SQLALCHEMY = importlib.util.find_spec("sqlalchemy") is not None

if not HAS_SQLALCHEMY:
    pass
else:
    from sqlalchemy import Column, Integer, String, func
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.schema import Index

    from .. import db  # noqa

    Base = cherrypy.db.get_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __repr__(self):
            return f"User(id={self.id}, username='{self.username}')"

    Index('user_username_unique_ix', func.lower(User.username), unique=True, info='This username already exists.')

    class Root:

        @cherrypy.expose
        def index(self):
            return str(User.query.all())

        @cherrypy.expose
        def add(self, username):
            try:
                User(username=username).add().commit()
                return "OK"
            except IntegrityError as e:
                return str(e)

    @unittest.skipUnless(HAS_SQLALCHEMY, "sqlalchemy not installed")
    class DbPluginTest(helper.CPWebCase):
        interactive = False

        @classmethod
        def setup_class(cls):
            cls.tempdir = tempfile.TemporaryDirectory(prefix='cherrypy-foundation-', suffix='-db-test')
            super().setup_class()

        @classmethod
        def teardown_class(cls):
            cls.tempdir.cleanup()
            super().teardown_class()

        @classmethod
        def setup_server(cls):
            cherrypy.config.update(
                {
                    'db.uri': f"sqlite:///{cls.tempdir.name}/data.db",
                }
            )
            cherrypy.tree.mount(Root(), '/')

        def setUp(self):
            cherrypy.db.create_all()
            return super().setUp()

        def tearDown(self):
            cherrypy.db.drop_all()
            return super().tearDown()

        def test_add_user(self):
            # Given an empty database
            self.assertEqual(0, User.query.count())
            # When calling "/add/" to create a user
            self.getPage('/add', method='POST', body=urlencode({'username': 'myuser'}))
            self.assertStatus(200)
            self.assertInBody('OK')
            # Then user get added to database
            self.assertEqual(1, User.query.count())

        def test_add_duplicate_user(self):
            # Given a database with a users
            User(username='user1').add().commit()
            # When trying to add another user
            self.getPage('/add', method='POST', body=urlencode({'username': 'user1'}))
            # Then an error get raised
            self.assertStatus(200)
            self.assertInBody('user_username_unique_ix')

        def test_get_users(self):
            # Given a database with a users
            new_user = User(username='newuser').add().commit()
            # When calling "/"
            self.getPage("/")
            self.assertStatus(200)
            # Then the page include our users
            self.assertInBody(new_user.username)
