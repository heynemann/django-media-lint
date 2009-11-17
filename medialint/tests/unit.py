# -*- coding: utf-8 -*-
# <Django Media Lint - CSS and JS lint checker for django>
# Copyright (C) <2009>  Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) <2009>  Benitez Moretti Coelho <benitezmc@gmail.com>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Django settings for medialint_project project.
import types
from django.test import TestCase

from medialint import CSSLint, InvalidCSSError
from medialint.tests.utils import assert_raises

class CSSLintUnitTest(TestCase):
    def test_can_validate(self):
        'CSSLint() should be able to validate css string'
        css = CSSLint()
        assert hasattr(css, 'validate'), \
               'Should have the attribute "validate"'
        assert isinstance(css.validate, types.MethodType), \
               'The attribute validate should be a method'

    def test_raise_invalid_css_with_at_instead_of_semicolon(self):
        'CSSLint("css with a at instead of semicolon at line end") should raise invalid css'
        css_without_semicolon = """a.big {
            color: red@
            border: 1px solid black;
        }"""
        css = CSSLint(css_without_semicolon)

        assert_raises(InvalidCSSError, css.validate, exc_pattern=r'Syntax error on line 2 column 23. Got the unexpected char "@"')

    def test_raise_invalid_css_when_get_no_semicolon(self):
        'CSSLint("css without semicolon at line end") should raise invalid css'
        css_without_semicolon = """a.big {color: blue
            border: 1px solid black;
        }"""
        css = CSSLint(css_without_semicolon)
        assert_raises(InvalidCSSError, css.validate, exc_pattern=r'Syntax error on line 2 column 19. Got the unexpected char ":"')

    def test_ie_hack_1(self):
        'CSSLint should not complain about IE Hack with asterisk'

        css_ie_hack_1 = """
        a.iehack1 {
            *border: 1px;
        }"""
        css = CSSLint(css_ie_hack_1)
        assert css.validate() is True, 'Should validate successfully in properties'

    def test_ie_hack_1_single_line(self):
        'CSSLint should not complain about IE Hack with asterisk in properties, single line'

        css_ie_hack_1 = ".iehack1 {*border:1px;} .iehack1 {*background:red;}"
        css = CSSLint(css_ie_hack_1)
        assert css.validate() is True, 'Should validate successfully'

    def test_ie_hack_2(self):
        'CSSLint should not complain about IE Hack with underscore in property'
        css_ie_hack_2 = """
        a.iehack2 {
            _border: 1px;
        }"""
        css = CSSLint(css_ie_hack_2)
        assert css.validate() is True, 'Should validate successfully'

    def test_ie_hack_2_single_line(self):
        'CSSLint should not complain about IE Hack with underscore in properties, single line'
        css_ie_hack_2 = "a.iehack2 {_color:red;} a.iehack2 {_background:blue;}"
        css = CSSLint(css_ie_hack_2)
        assert css.validate() is True, 'Should validate successfully'

    def test_should_validate_ok(self):
        'CSSLint("a valid css") should validate successfully'
        css_ok = """
            #some {
                color: blue;
            }
        """
        css = CSSLint(css_ok)
        assert css.validate() is True, 'Should validate successfully'

class CSSLintExceptionUnitTest(TestCase):
    def test_construction(self):
        exc = InvalidCSSError(line=2, column=10, char="$")
        self.assertEquals(exc.line, 2)
        self.assertEquals(exc.column, 10)
        self.assertEquals(exc.char, "$")

