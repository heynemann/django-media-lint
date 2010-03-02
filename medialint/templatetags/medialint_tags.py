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
from django.conf import settings
from django.http import HttpRequest
from django.core.urlresolvers import resolve, Resolver404
from lxml import html as lhtml
from django.core.cache import cache

from medialint.compressor import CSSCompressor
from medialint.signals import css_joined, js_joined

register = template.Library()

class CSSJoiner(object):
    def __init__(self, content):
        self.content = content
        self.html = lhtml.fromstring(content)
        self.links = []
        for link in self.html.cssselect('link'):
            self.links.append(link.attrib['href'])

class JSJoiner(object):
    def __init__(self, content):
        self.content = content
        self.html = lhtml.fromstring(content)
        self.links = []
        for link in self.html.cssselect('script'):
            self.links.append(link.attrib['src'])

class MediaJoinNode(template.Node):
    file_404 = 'The file "%s" does not exist.'

    def __init__(self, nodelist, file_name):
        self.nodelist = nodelist
        self.file_name = template.Variable(file_name)
        self.file_list = []
        self.content_list = []
 
    def render(self, context):
        html = "".join([x.render(context) for x in self.nodelist])
        if getattr(settings, 'DISABLE_MEDIALINT', False):
            return html
        file_name = self.file_name.resolve(context)
        arquivo_atualizado = cache.get(file_name)
        if arquivo_atualizado:
            return self.tag % file_name

        joiner = self.joiner(html)

        for link in joiner.links:
            if link.startswith("http://"):
                raise template.TemplateSyntaxError(self.http_error)
            self.file_list.append(link)
            try:
                view, args, kwargs = resolve(link)
            except Resolver404, e:
                raise template.TemplateSyntaxError(self.file_404 % link)
            content = view(request=HttpRequest(), *args, **kwargs)
            self.content_list.append(content.content.strip())

        content = "".join(self.content_list)

        if self.compressor:
            compressor = self.compressor()
            content = compressor.compress(content)

        cache.set(file_name, True, 600)
        self.send_signal(file_name, content, self.file_list, context)
        return self.tag % file_name

class CSSJoinNode(MediaJoinNode):
    http_error = 'Links under cssjoin templatetag can not have full ' \
                 'URL (starting with http)'
    joiner = CSSJoiner
    compressor = CSSCompressor
    tag = '<link rel="stylesheet" href="%s" />'

    def send_signal(self, file_name, content, files, context):
        css_joined.send(sender=self,
                        css_name=file_name,
                        joined_content=content,
                        css_files=files,
                        context=context)

class JSJoinNode(MediaJoinNode):
    http_error = 'Links under jsjoin templatetag can not have full ' \
                 'URL (starting with http)'
    joiner = JSJoiner
    tag = '<script type="text/javascript" src="%s"></script>'
    compressor = None
    def send_signal(self, file_name, content, files, context):
        js_joined.send(sender=self,
                       js_name=file_name,
                       joined_content=content,
                       js_files=files,
                       context=context)

def do_cssjoin(parser, token):
    bits = token.split_contents()
    css_name = bits[1]
    nodelist = parser.parse(('endcssjoin',))
    parser.delete_first_token()
    return CSSJoinNode(nodelist, css_name)

def do_jsjoin(parser, token):
    bits = token.split_contents()
    js_name = bits[1]
    nodelist = parser.parse(('endjsjoin',))
    parser.delete_first_token()
    return JSJoinNode(nodelist, js_name)

register.tag("cssjoin", do_cssjoin)
register.tag("jsjoin", do_jsjoin)
