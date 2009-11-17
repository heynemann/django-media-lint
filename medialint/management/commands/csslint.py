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
from django.conf import settings
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
        if not path:
            path = settings.MEDIA_ROOT
            if not path:
                print "You did not pass the argument --path and don't " \
                      "even have settings.MEDIA_ROOT set. The command " \
                      "can not proceed :("
            else:
                print "Scanning css files under settings.MEDIA_ROOT: " \
                      "%s" % path
        else:
            print "Scanning css files under: %s" % path

        valid_files = []
        invalid_files = []
        for filename in CSSLint.fetch_css(path):
            content = open(filename).read()
            cssl = CSSLint(content)
            try:
                cssl.validate()
                valid_files.append(filename)
            except InvalidCSSError, e:
                invalid_files.append((filename, e))

        for vfile in valid_files:
            print "%s - OK" % vfile

        for ifile, err in invalid_files:
            print "%s - ERROR: in line %d, column %d" % (ifile, err.line, err.column)
