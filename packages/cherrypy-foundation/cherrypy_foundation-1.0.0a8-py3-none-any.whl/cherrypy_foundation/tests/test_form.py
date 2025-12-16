# CherryPy Foundation
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
import importlib
from unittest import skipUnless

import cherrypy
from cherrypy.test import helper
from wtforms.fields import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length

import cherrypy_foundation.tools.jinja2  # noqa
from cherrypy_foundation.form import CherryForm
from cherrypy_foundation.tools.i18n import gettext_lazy as _

HAS_JINJAX = importlib.util.find_spec("jinjax") is not None

env = cherrypy.tools.jinja2.create_env(
    package_name=__package__,
)


class LoginForm(CherryForm):
    login = StringField(
        _('User'),
        validators=[
            InputRequired(),
            Length(max=256, message=_('User too long.')),
        ],
        render_kw={
            "placeholder": _('User'),
            "autocorrect": "off",
            "autocapitalize": "none",
            "autocomplete": "off",
            "autofocus": "autofocus",
        },
    )
    password = PasswordField(
        _('Password'),
        validators=[
            InputRequired(),
            Length(max=256, message=_('Password too long.')),
        ],
        render_kw={"placeholder": _("Password")},
    )
    persistent = BooleanField(
        _('Remember me'),
        # All `label-*` are assigned to the label tag.
        render_kw={'container_class': 'col-sm-6', 'label-attr': 'FOO'},
    )
    submit = SubmitField(
        _('Login'),
        # All `container-*` are assigned to the container tag.
        render_kw={"class": "btn-primary float-end", 'container_class': 'col-sm-6', 'container-attr': 'BAR'},
    )


@cherrypy.tools.jinja2(env=env)
class Root:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='test_form.html')
    def index(self):
        form = LoginForm()
        return {'form': form}


@skipUnless(HAS_JINJAX, reason='Required jinjax')
class FormTest(helper.CPWebCase):
    default_lang = None
    interactive = False

    @classmethod
    def setup_server(cls):
        cherrypy.tree.mount(Root(), '/')

    def test_get_form(self):
        # Given a form
        # When querying the page that include this form
        self.getPage("/")
        self.assertStatus(200)
        # Then each field is render properly.
        # 1. Check title
        self.assertInBody('test-form')
        # 2. Check user field
        self.assertInBody('<label class="form-label" for="login">User</label>')
        self.assertInBody(
            '<input autocapitalize="none" autocomplete="off" autocorrect="off" autofocus="autofocus" class="form-control" id="login" maxlength="256" name="login" placeholder="User" required type="text" value="">'
        )
        # 3. Check password
        self.assertInBody('<label class="form-label" for="password">Password</label>')
        self.assertInBody(
            '<input class="form-control" id="password" maxlength="256" name="password" placeholder="Password" required type="password" value="">'
        )
        # 4 Check remember me
        self.assertInBody(
            '<input class="form-check-input" container-class="col-sm-6" id="persistent" label-attr="FOO" name="persistent" type="checkbox" value="y">'
        )
        self.assertInBody('<label attr="FOO" class="form-check-label" for="persistent">Remember me</label>')
        # 5. check submit button (regex matches because class could have different order with jinjax<=0.57)
        self.assertInBody('<div  attr="BAR"')
        self.assertMatchesBody(
            '<input class="(btn-primary ?|float-end ?|btn ?){3}" container-attr="BAR" container-class="col-sm-6" id="submit" name="submit" type="submit" value="Login">'
        )
