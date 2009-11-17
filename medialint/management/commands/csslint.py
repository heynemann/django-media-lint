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


from django.core.management.base import BaseCommand
from optparse import make_option
from medialint import CSSLint, InvalidCSSError



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--path', dest='path', default=None,
            help = "Validate css files"),
        
    )

    def handle(self, *args, **options):
        path = options.get('path')
        try:
            CSSLint.check_files(path)
            print "All css files under %s are fine :)" % path
        except InvalidCSSError, e:
            print e

