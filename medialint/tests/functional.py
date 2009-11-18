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

from os.path import dirname, abspath, join
from django.test import TestCase
from django.template import Template, RequestContext, TemplateSyntaxError
from medialint.signals import css_joined
from medialint import CSSLint, InvalidCSSError
from medialint.tests.utils import assert_raises

LOCAL_FILE = lambda *x: join(abspath(dirname(__file__)), *x)

class CSSJoinerTemplateTagFunctionalTest(TestCase):
    def test_rendering_css_joiner_simple_case(self):
        t = Template('''{% load medialint_tags %}
            {% cssjoin "/media/css/grid-stuff.css" %}
                <link rel="stylesheet" href="/media/css/reset.css" />
                <link rel="stylesheet" href="/media/css/text.css" />
                <link rel="stylesheet" href="/media/css/960.css" />
                <link rel="stylesheet" href="/media/css/main.css" />
            {% endcssjoin %}
        ''')
        c = RequestContext({})
        got = t.render(c).strip()
        expected = '''<link rel="stylesheet" href="/media/css/grid-stuff.css" />'''

        self.assertEquals(got, expected)

    def test_send_signal_before_rendering(self):
        self._signal_has_been_called = False
        def on_render(sender, **kw):
            self.assertEquals(kw['css_name'], '/some/path/grid-stuff.css')
            self.assertEquals(
                kw['css_files'],
                ['/media/foo.css', '/media/css/bar.css']
            )
            self._signal_has_been_called = True

        t = Template('''{% load medialint_tags %}
            {% cssjoin "/some/path/grid-stuff.css" %}
                <link rel="stylesheet" href="/media/foo.css" />
                <link rel="stylesheet" href="/media/css/bar.css" />
            {% endcssjoin %}
        ''')
        c = RequestContext({})
        css_joined.connect(on_render)
        t.render(c)

        assert self._signal_has_been_called

    def test_rendering_css_fail_when_http_in_link(self):
        t = Template('''{% load medialint_tags %}
            {% cssjoin "/media/css/should-fail-http.css" %}
                <link rel="stylesheet" href="/media/css/text.css" />
                <link rel="stylesheet" href="http://globo.com/media/css/reset.css" />
            {% endcssjoin %}
        ''')
        c = RequestContext({})
        assert_raises(TemplateSyntaxError, t.render, c,
                      exc_pattern=r'Links under cssjoin templatetag can' \
                      ' not have full URL [(]starting with http[)]')

class CSSLintFunctionalTest(TestCase):
    def test_can_find_css_files_for_given_path(self):
        'CSSLint.fetch_css should find css files within a given path'
        css_files = CSSLint.fetch_css(LOCAL_FILE('media'))
        self.assertTrue(isinstance(css_files, list))
        self.assertEquals(len(css_files), 3)
        self.assertEquals(css_files[0], LOCAL_FILE('media', 'css', 'invalid-css1.css'))
        self.assertEquals(css_files[2], LOCAL_FILE('media', 'css', 'valid', 'valid-css1.css'))
        self.assertEquals(css_files[1], LOCAL_FILE('media', 'css', 'hacks', 'valid-css1-with-hacks.css'))

    def test_find_and_check_css_error(self):
        'CSSLint.fetch_and_check should find and check css files'
        fname = LOCAL_FILE('media', 'css', 'invalid-css1.css')
        assert_raises(InvalidCSSError,
                      CSSLint.check_files, LOCAL_FILE('media'),
                      exc_pattern=r'Syntax error on file: %s line 4 column 11. Got the unexpected char ":"' % fname)

    def test_find_and_check_css_success(self):
        'CSSLint.fetch_and_check should find and check css files'
        assert CSSLint.check_files(LOCAL_FILE('media','css', 'valid')) is True, 'Should check successfully'
    
    def test_find_and_check_css_error_ignoring_hacks(self):
        'CSSLint.fetch_and_check should find and check css files ignoring css hacks'
        assert CSSLint().check_files(LOCAL_FILE('media','css', 'hacks'), ignore_hacks='True') is True, 'Should check successfully'
