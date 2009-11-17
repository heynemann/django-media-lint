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
from os.path import dirname, abspath, join
from django.test import TestCase

from medialint import CSSLint, InvalidCSSError
from medialint.tests.utils import assert_raises

LOCAL_FILE = lambda *x: join(abspath(dirname(__file__)), *x)
class CSSLintFunctionalTest(TestCase):
    def test_can_find_css_files_for_given_path(self):
        'CSSLint.fetch_css should find css files within a given path'
        css_files = CSSLint.fetch_css(LOCAL_FILE('media'))
        self.assertTrue(isinstance(css_files, list))
        self.assertEquals(len(css_files), 2)
        self.assertEquals(css_files[0], LOCAL_FILE('media', 'css', 'invalid-css1.css'))
        self.assertEquals(css_files[1], LOCAL_FILE('media', 'css', 'valid', 'valid-css1.css'))

    def test_find_and_check_css_error(self):
        'CSSLint.fetch_and_check should find and check css files'
        fname = LOCAL_FILE('media', 'css', 'invalid-css1.css')
        assert_raises(InvalidCSSError,
                      CSSLint.check_files, LOCAL_FILE('media'),
                      exc_pattern=r'Syntax error on file: %s line 4 column 11. Got the unexpected char ":"' % fname)

    def test_find_and_check_css_success(self):
        'CSSLint.fetch_and_check should find and check css files'
        assert CSSLint.check_files(LOCAL_FILE('media','css', 'valid')) is True, 'Should check successfully'
