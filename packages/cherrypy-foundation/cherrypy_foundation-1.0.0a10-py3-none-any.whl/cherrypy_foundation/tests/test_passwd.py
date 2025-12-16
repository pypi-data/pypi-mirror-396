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
'''
Created on Apr. 10, 2020

@author: Patrik Dufresne
'''

import importlib
import unittest

from ..passwd import check_password, hash_password

HAS_ARGON2 = importlib.util.find_spec("argon2") is not None


class Test(unittest.TestCase):

    @unittest.skipUnless(HAS_ARGON2, "argon2 not installed")
    def test_check_password_argon(self):
        self.assertTrue(hash_password('admin12').startswith('$argon2'))
        self.assertTrue(
            check_password('admin123', '$argon2id$v=19$m=102400,t=2,p=8$/mDhOg8wyZeMTUjcbIC7mg$3pxRSfYgUXmKEKNtasP1Og')
        )

    @unittest.skipIf(HAS_ARGON2, "argon2 is installed")
    def test_check_password_hashlib(self):
        # Given argon is not installed
        # When generating hash password
        hash = hash_password('admin12')
        # Then SSHA hash is generated
        self.assertTrue(hash.startswith('{SSHA}'))

    def test_check_password(self):
        self.assertTrue(check_password('admin123', '{SSHA}/LAr7zGT/Rv/CEsbrEndyh27h+4fLb9h'))
        self.assertFalse(check_password('admin12', '{SSHA}/LAr7zGT/Rv/CEsbrEndyh27h+4fLb9h'))
        self.assertTrue(check_password('admin12', hash_password('admin12')))
        self.assertTrue(check_password('admin123', hash_password('admin123')))
