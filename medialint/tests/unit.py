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
from mox import Mox

from medialint import CSSLint, InvalidCSSError, CSSCompressor, JSLint, InvalidJSError
from medialint.tests.utils import assert_raises

class CSSCompressorUnitTest(TestCase):
    def _test_compressing_uses_lint_before_compressing(self):
        "CSSCompressor should make a lint check before compressing..."
        some_css = """
        #my-test {
            color:green;
        }
        """
        mox = Mox()

        csslint_class_mock = mox.CreateMockAnything()
        csslint_mock = mox.CreateMockAnything()

        csslint_class_mock(some_css).AndReturn(csslint_mock)
        csslint_mock.validate().AndReturn(True)

        mox.ReplayAll()
        cp = CSSCompressor(lintian=csslint_class_mock)
        cp.compress(some_css)
        mox.VerifyAll()

    def _test_compressing_remove_extra_spaces(self):
        "CSSCompressor should remove extra spaces"
        some_css = "  #my-test    {            color:green;         }"
        cp = CSSCompressor()
        self.assertEquals(cp.compress(some_css),
                          "#my-test { color:green; }")

    def _test_compressing_remove_extra_spaces_and_keep_nospaces(self):
        "CSSCompressor should remove extra spaces, but don't touch nonspaces"
        some_css = "#my-test{color:green;         }"
        cp = CSSCompressor()
        self.assertEquals(cp.compress(some_css),
                          "#my-test{color:green; }")

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


    def test_should_validate_ok(self):
        'CSSLint("a valid css") should validate successfully'
        css_ok = """
            #some {
                color: blue;
            }
        """
        css = CSSLint(css_ok)
        assert css.validate() is True, 'Should validate successfully'


class JSLintUnitTest(TestCase):
    def test_can_validate(self):
        'CSSLint() should be able to validate js string'
        js = JSLint()
        assert hasattr(css, 'validate'), \
               'Should have the attribute "validate"'
        assert isinstance(css.validate, types.MethodType), \
               'The attribute validate should be a method'

    def _test_raise_invalid_js_with_at_instead_of_semicolon(self):
        'JSLint("js with a at instead of semicolon at line end") should raise invalid js'
        
        js = JSLint(js_without_semicolon)

        assert_raises(InvalidJSError, js.validate, exc_pattern=r'Syntax error on line 2 column 23')

    def _test_raise_invalid_js_when_get_no_semicolon(self):
        'JSLint("js without semicolon at line end") should raise invalid js'
        js_without_semicolon = """var a = 0
            var b = 0;
        }"""
        js = JSLint(js_without_semicolon)
        assert_raises(InvalidJSError, js.validate, exc_pattern=r'Syntax error on line 2 column 19')


    def _test_should_validate_ok(self):
        'JSLint("a valid js") should validate successfully'
        css_ok = """
            var a = 0;
            var b = 0;
        """
        js = JSLint(js_ok)
        assert js.validate() is True, 'Should validate successfully'


class CSSLintExceptionUnitTest(TestCase):
    def test_construction(self):
        exc = InvalidCSSError(line=2, column=10, char="$")
        self.assertEquals(exc.line, 2)
        self.assertEquals(exc.column, 10)
        self.assertEquals(exc.char, "$")


class JSLintExceptionUnitTest(TestCase):
    def _test_construction(self):
        exc = InvalidJSError(line=2, column=10)
        self.assertEquals(exc.line, 2)
        self.assertEquals(exc.column, 10)
