__author__ = 'Chris Barbara'

import logging
import os
import string

from google.appengine.api import users
from google.appengine.api import memcache
import webapp2

from django.conf import settings
from django.template.loader import render_to_string

from models import MatchedFile


def default_template_data():
    data = {
        "title": settings.SITE_NAME
    }

    user = users.get_current_user()
    if user is not None:
        data["user"] = user
        data["admin"] = users.is_current_user_admin()

    return data


class BaseHandler(webapp2.RequestHandler):

    def render(self, template_values, filename):
        self.response.out.write(render_to_string(filename, template_values))

    def not_found(self):
        self.error(404)
        self.render(default_template_data(), "404.html")

    def retrieve(self, key):
        item = memcache.get(key)
        if item is not None:
            return item
        else:
            item = self.data()
            if item is not None and not memcache.add(key, item):
                logging.error("Memcache set failed on %s" % key)
        return item


class NotFoundHandler(BaseHandler):

    def get(self):
        self.error(404)
        self.render(default_template_data(), "404.html")


class HomePageHandler(BaseHandler):
    def get(self):

        self.render(default_template_data(), "index.html")

class FileHandler(BaseHandler):
    def get(self,slug):
        existing = MatchedFile.get_by_slug(slug)
        if existing:
            td = default_template_data()
            td["file"] = existing
            self.render(td, "file.html")
        else:
            self.not_found()

class FileContentHandler(BaseHandler):
    def get(self,slug):
        existing = MatchedFile.get_by_slug(slug)
        if existing:
            self.response.headers['Content-Type'] = 'application/x-nzb'
            self.response.headers['Content-Disposition'] = 'attachment; filename=' + slug + ".nzb"
            self.response.out.write(existing.content)
        else:
            self.not_found()


