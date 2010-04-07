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

class InvalidCSSError(Exception):
    def __init__(self, line=None, column=None, char=None, file_name=None, error=None):
        self.line = line and int(line) or 0
        self.column = column and int(column) or 0
        self.char = char

        if error:
            super(InvalidCSSError, self).__init__(error)
            return

        m = u'Syntax error on%s line %d column %d. Got the unexpected char "%s"'
        sfile = file_name and " file: %s" % file_name or ''
        msg = m % (sfile, self.line, self.column, self.char)
        super(InvalidCSSError, self).__init__(msg)

class InvalidJSError(Exception):
    def __init__(self, file_name=None, error=None):
        self.file_name = file_name

        if error:
            super(InvalidJSError, self).__init__(error)
            return
        msg = "FALTA MENSAGEM AQUI"
        super(InvalidJSError, self).__init__(msg)

class InvalidMediaNameError(Exception):
    pass
    
class DuplicatedMediaError(Exception):
    pass
