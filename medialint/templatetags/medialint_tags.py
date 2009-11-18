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

from django import template
from django.http import HttpRequest
from django.core.urlresolvers import resolve, Resolver404
from lxml import html as lhtml

from medialint.signals import css_joined

register = template.Library()

class CSSJoiner(object):
    def __init__(self, content):
        self.content = content
        self.html = lhtml.fromstring(content)
        self.links = []
        for link in self.html.cssselect('link'):
            self.links.append(link.attrib['href'])

class CSSJoinNode(template.Node):
    http_error = 'Links under cssjoin templatetag can not have full ' \
                 'URL (starting with http)'

    file_404 = 'The file "%s" does not exist.'

    def __init__(self, nodelist, css_name):
        self.nodelist = nodelist
        self.css_name = template.Variable(css_name)

    def __repr__(self):
        return "<CSSJoinNode>"

    def render(self, context):
        html = "".join([x.render(context) for x in self.nodelist])
        joiner = CSSJoiner(html)
        css_list = []
        content_list = []
        css_name = self.css_name.resolve(context)
        for link in joiner.links:
            if link.startswith("http://"):
                raise template.TemplateSyntaxError(self.http_error)
            css_list.append(link)
            try:
                view, args, kwargs = resolve(link)
            except Resolver404, e:
                raise template.TemplateSyntaxError(self.file_404 % link) 
            content = view(request=HttpRequest(), *args, **kwargs)
            content_list.append(content.content.strip())

        css_joined.send(sender=self,
                        css_name=css_name,
                        joined_content="".join(content_list),
                        css_files = css_list[:],
                        context=context)

        return '<link rel="stylesheet" href="%s" />' % css_name

def do_cssjoin(parser, token):
    bits = token.split_contents()
    css_name = bits[1]
    nodelist = parser.parse(('endcssjoin',))
    parser.delete_first_token()
    return CSSJoinNode(nodelist, css_name)

register.tag("cssjoin", do_cssjoin)
