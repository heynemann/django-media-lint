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
from django.http import HttpRequest
from django.template import Template, RequestContext, TemplateSyntaxError, Context
from django.core.urlresolvers import resolve, Resolver404

from medialint import CSSLint, InvalidCSSError
from medialint.signals import css_joined, js_joined
from medialint.tests.utils import assert_raises
from medialint.exceptions import InvalidMediaNameError,DuplicatedMediaError

LOCAL_FILE = lambda *x: join(abspath(dirname(__file__)), *x)

class CSSJoinerTemplateTagFunctionalTest(TestCase):

    def test_css_same_name_different_path_work_correct(self):
        template = Template('''
            {% load medialint_tags %}
            {% cssjoin "/media/css/reset.css" %}
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
                <link rel="stylesheet" href="/media/css2/fake_joined.css" />
            {% endcssjoin %}
        ''')

        c = Context({})
        got = template.render(c).strip()
        expected = '''<link rel="stylesheet" href="/media/css/reset.css" />'''
        self.assertEquals(got, expected)
        
    def test_css_same_name_different_path_include_boths(self):
        self._signal_has_been_called = False
        template = Template('''
            {% load medialint_tags %}
            {% cssjoin "/media/css/reset.css" %}
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
                <link rel="stylesheet" href="/media/css2/fake_joined.css" />
            {% endcssjoin %}
        ''')
        view_1, args_1, kwargs_1 = resolve('/media/css/fake_joined.css')
        view_2, args_2, kwargs_2 = resolve('/media/css2/fake_joined.css')
        content_1 = view_1(request=HttpRequest(), *args_1, **kwargs_1)
        content_2 = view_2(request=HttpRequest(), *args_2, **kwargs_2)
        content_expected = "".join([content_1.content, content_2.content])
        
        def on_render(sender, **kw):
            self.assertEquals(
                 kw['joined_content'],
                 '.teste{border:solid 1px}.teste2{font:12px}'
             )
            self._signal_has_been_called = True

        
        css_joined.connect(on_render)
        c = RequestContext({})
        got = template.render(c).strip()
        expected = '''<link rel="stylesheet" href="/media/css/reset.css" />'''

        assert self._signal_has_been_called
        self.assertEquals(got, expected)
        css_joined.disconnect(on_render)


    def test_css_duplicated_path_should_raise_with_correct_msg(self):
        template = Template('''
            {% load medialint_tags %}
            {% cssjoin "/media/css/reset.css" %}
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
                <link rel="stylesheet" href="/media/css/text.css" />
                <link rel="stylesheet" href="/media/css/960.css" />
                <link rel="stylesheet" href="/media/css/960.css" />
            {% endcssjoin %}
        ''')
        c = Context({})
        try:
            template.render(c)
            assert False, "shouldn't reach here"
        except Exception, ex:
            self.assertEquals(ex.exc_info[0], DuplicatedMediaError)
            self.assertEquals(unicode(ex.exc_info[1]), u'The files "/media/css/fake_joined.css" is duplicate. It appears 2 times,"/media/css/960.css" is duplicate. It appears 2 times ')

    def test_css_duplicated_path_should_raise(self):
        template = Template('''
            {% load medialint_tags %}
            {% cssjoin "/media/css/reset.css" %}
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
            {% endcssjoin %}
        ''')
        c = Context({})
        try:
            template.render(c)
            assert False, "shouldn't reach here"
        except Exception, ex:
            self.assertEquals(ex.exc_info[0], DuplicatedMediaError)
            self.assertEquals(unicode(ex.exc_info[1]), u'The files "/media/css/fake_joined.css" is duplicate. It appears 2 times ')


    def test_css_paths_equals_file_name_should_raise(self):
        template = Template('''
            {% load medialint_tags %}
            {% cssjoin "/media/css/fake_joined.css" %}
                <link rel="stylesheet" href="/media/css/fake_joined.css" />
            {% endcssjoin %}
        ''')
        c = Context({})

        try:
            template.render(c)
            assert False, "shouldn't reach here"
        except Exception, ex:
            self.assertEquals(ex.exc_info[0], InvalidMediaNameError)
            self.assertEquals(unicode(ex.exc_info[1]), u'The file "/media/css/fake_joined.css" cannot be merged because it s on the files path.')


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
            self.assertEquals(
                kw['joined_content'],
                "#foo{color:red}#bar{color:blue;font:11px}"
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
        css_joined.disconnect(on_render)

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

    def test_rendering_css_fail_when_file_does_not_exist(self):
        t = Template('''{% load medialint_tags %}
            {% cssjoin "/media/css/should-fail-http.css" %}
                <link rel="stylesheet" href="/media/css/text.css" />
                <link rel="stylesheet" href="gluglu.css" />
            {% endcssjoin %}
        ''')
        c = RequestContext({})
        assert_raises(TemplateSyntaxError, t.render, c,
                      exc_pattern=r'The file "gluglu.css" does not exist.')

class JSJoinerTemplateTagFunctionalTest(TestCase):
    def test_rendering_js_joiner_simple_case(self):
        t = Template('''{% load medialint_tags %}
            {% jsjoin "/media/js/jquery-crew.js" %}
                <script type="text/javascript" src="/media/js/jquery.js"></script>
            {% endjsjoin %}
        ''')
        c = RequestContext({})
        got = t.render(c).strip()
        expected = '''<script type="text/javascript" src="/media/js/jquery-crew.js"></script>'''

        self.assertEquals(got, expected)

    def test_send_signal_before_rendering(self):
        self._signal_has_been_called = False
        def on_render(sender, **kw):
            self.assertEquals(kw['js_name'], '/path/to.js')
            self.assertEquals(
                kw['js_files'],
                ['/media/foo.js', '/media/js/bar.js']
            )
            self.assertEquals(
                kw['joined_content'],
                "var foo = 'foo';console.debug(foo);"
            )
            self._signal_has_been_called = True

        t = Template('''{% load medialint_tags %}
            {% jsjoin "/path/to.js" %}
                <script type="text/javascript" src="/media/foo.js"></script>
                <script type="text/javascript" src="/media/js/bar.js"></script>
            {% endjsjoin %}
        ''')
        c = RequestContext({})
        js_joined.connect(on_render)
        t.render(c)

        assert self._signal_has_been_called

    def test_rendering_js_fail_when_http_in_link(self):
        t = Template('''{% load medialint_tags %}
            {% jsjoin "/media/js/should-fail-http.js" %}
                <script type="text/javascript" src="/media/js/jquery.js"></script>
                <script type="text/javascript" src="http://globo.com/media/js/jquery.js"></script>
            {% endjsjoin %}
        ''')
        c = RequestContext({})
        assert_raises(TemplateSyntaxError, t.render, c,
                      exc_pattern=r'Links under jsjoin templatetag can' \
                      ' not have full URL [(]starting with http[)]')

    def test_rendering_js_fail_when_file_does_not_exist(self):
        t = Template('''{% load medialint_tags %}
            {% jsjoin "/media/js/should-fail-404.js" %}
                <script type="text/javascript" src="/media/js/jquery.js"></script>
                <script type="text/javascript" src="/gluglu.js"></script>
            {% endjsjoin %}
        ''')
        c = RequestContext({})
        assert_raises(TemplateSyntaxError, t.render, c,
                      exc_pattern=r'The file "/gluglu.js" does not exist.')

class CSSLintFunctionalTest(TestCase):
    def test_can_find_css_files_for_given_path(self):
        'CSSLint.fetch_css should find css files within a given path'
        css_files = sorted(CSSLint.fetch_css(LOCAL_FILE('media')))
        self.assertTrue(isinstance(css_files, list))
        self.assertEquals(len(css_files), 4)
        self.assertEquals(css_files[0], LOCAL_FILE('media', 'css', 'hacks', 'valid-css1-with-hacks.css'))
        self.assertEquals(css_files[1], LOCAL_FILE('media', 'css', 'invalid-css1.css'))
        self.assertEquals(css_files[2], LOCAL_FILE('media', 'css', 'valid', 'valid-css1.css'))

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
        assert CSSLint().check_files(LOCAL_FILE('media','css', 'hacks'), ignore_hacks=True) is True, 'Should check successfully'
