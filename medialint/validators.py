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
import re
import os
from cssutils import CSSParser
from xml.dom import SyntaxErr
from medialint.exceptions import InvalidCSSError

class CSSLint(object):
    def __init__(self, css=None):
        self.css = css
        self.parser = CSSParser(raiseExceptions=True, loglevel=100)

    @classmethod
    def fetch_css(cls, path):
        css_files = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".css"):
                    css_files.append(os.path.join(root, filename))

        return css_files


    @classmethod
    def check_files(cls, path, ignore_hacks=False):
        files = cls.fetch_css(path)
        for file_name in files:
            content = open(file_name).read()
            css = cls(content)
            try:
                css.validate(ignore_hacks=ignore_hacks)
            except InvalidCSSError, e:
                raise InvalidCSSError(
                    line=e.line,
                    column=e.column,
                    char=e.char,
                    file_name=file_name
                )

        return True




    def validate(self, ignore_hacks=False):
        try:
            self.parser.parseString(self.css)
            return True
        except UnicodeDecodeError, e:
            raise InvalidCSSError(error=e)

        except SyntaxErr, e:
            regex = r'[[](?P<line>\d+)[:](?P<column>\d+)[:](?P<char>.+)[]]'
            match = re.compile(regex)

            matched = match.search(unicode(e))
            if matched:
                char = matched.group('char').strip() or ' '
                if ignore_hacks:
                    if char ==  "*" or char == "_":
                        return True
                raise InvalidCSSError(
                    line=matched.group('line'),
                    column=matched.group('column'),
                    char=char
                )
            else:
                raise InvalidCSSError(error=e)

class JSLint(object):
    def __init__(self, js=None):
        self.js = js

    @classmethod
    def fetch_js_files(cls, path):
        js_files = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".js"):
                    js_files.append(os.path.join(root, filename))

        return js_files

    @classmethod
    def check_js_files(cls, path):
        files = cls.fetch_js_files(path)
        for file_name in files:
            content = open(file_name).read()
            js = cls(content)
            try:
                js.validate()
            except InvalidJSError, e:
                raise InvalidJSError(
                    error=e
                )

        return True


    def validate(self):
        try:
            self.parser.parseString(self.css)
            return True
        except UnicodeDecodeError, e:
            raise InvalidJSError(error=e)


