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
from cssutils import CSSParser
from xml.dom import SyntaxErr
from medialint.exceptions import InvalidCSSError


class CSSLint(object):
    def __init__(self, css=None):
        self.css = css
        self.parser = CSSParser(raiseExceptions=True)


    def validate(self):
        try:
            self.parser.parseString(self.css)
            return True
        except SyntaxErr, e:
            regex = r'[[](?P<line>\d+)[:](?P<column>\d+)[:](?P<char>.+)[]]'
            match = re.compile(regex)
            matched = match.search(e.msg)
            char = matched.group('char').strip() or ' '
            if matched:
                message = 'Syntax error on line %s column %s. ' \
                    'Got the unexpected char "%s"' % (
                        matched.group('line'),
                        matched.group('column'),
                        char)

                raise InvalidCSSError(message)
            

            
                
