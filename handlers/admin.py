__author__ = 'Chris Barbara'

import cgi
import logging
import os
import string

from datetime import datetime
from django.conf import settings
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db

from handlers import site
from models import FileSource, TrackedSeries, MatchedFile
from utils import slugify


def default_template_data():
    td = site.default_template_data()
    td["title"] = td["title"] + " Admin"
    return td

def invalidate_cache(cacheKey):
    if not memcache.delete(cacheKey):
        logging.error("Memcache delete failed on "+cacheKey)
    taskqueue.add(url='/', method="GET")


class RootHandler(site.BaseHandler):

    def get(self):
        self.render(default_template_data(), 'admin/index.html')


class SourcesHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["sources_selected"] = True
        td["sources"] = self.retrieve("sources")
        self.render(td, 'admin/sources.html')

    def data(self):
        return FileSource.all().order("name").fetch(1000)


class SourcesCreateHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["sources_selected"] = True
        td["action"] = "create"
        td["qualities"] = ["HD","SD"]

        self.render(td, 'admin/sources_create.html')


    def post(self):
        """
            name        -- string: The name of this file source
            slug        -- stirng: URL friendly version of the name
            rssUrl      -- string: The rss feed url 
            quality     -- string: The quality of the files in this source
            zipped      -- boolean: Are the files from this source zip files?
            authorizationRequired   -- boolean: When downloading the file, is authorization required?
            authUsername    -- string: authorization username
            authPassword    -- string: authorization password
        """
        name = self.request.get('name', default_value=None)
        rssUrl = self.request.get('rssUrl', default_value=None)
        quality = self.request.get('quality', default_value=None)
        zipped = self.request.get('zipped', default_value=False) == "true"
        authorizationRequired = self.request.get('authorizationRequired', default_value=False) == "true"
        authUsername = self.request.get('authUsername', default_value=None)
        authPassword = self.request.get('authPassword', default_value=None)

        if not name or not rssUrl or not quality:
            self.error(400, "Bad Data: Name: %s, rssUrl: %s, quality: %s" % (name, rssUrl, quality))
            return

        slug = slugify.slugify(name)
        existing_s = FileSource.get_by_slug(slug)

        if existing_s:
            self.error(400, "A source with this name already exists")
            return

        s = FileSource(name=name, slug=slug, rssUrl=rssUrl, quality=quality, zipped=zipped, authorizationRequired=authorizationRequired,
            authUsername=authUsername, authPassword=authPassword)
        s.put()

        invalidate_cache("sources")

        self.redirect("/admin/sources/"+slug)



class SourcesInstanceHandler(site.BaseHandler):

    def get(self, slug):
        source = FileSource.get_by_slug(slug)
        if source:
            td = default_template_data()
            td["sources_selected"] = True
            td["source"] = source
            td["qualities"] = ["HD","SD"]
            self.render(td, 'admin/sources_instance.html')
        else:
            self.not_found()


    def post(self, slug):
        """
            name        -- string: The name of this file source
            slug        -- stirng: URL friendly version of the name
            rssUrl      -- string: The rss feed url 
            quality     -- string: The quality of the files in this source
            zipped      -- boolean: Are the files from this source zip files?
            authorizationRequired   -- boolean: When downloading the file, is authorization required?
            authUsername    -- string: authorization username
            authPassword    -- string: authorization password
        """

        existing_s = FileSource.get_by_slug(slug)
        if not existing_s:
            self.error(400, "Cannot find an existing source to edit")
            return

        name = self.request.get('name', default_value=None)
        newSlug = slugify.slugify(name)
        rssUrl = self.request.get('rssUrl', default_value=None)
        quality = self.request.get('quality', default_value=None)
        zipped = self.request.get('zipped', default_value=False) == "true"
        authorizationRequired = self.request.get('authorizationRequired', default_value=False) == "true"
        authUsername = self.request.get('authUsername', default_value=None)
        authPassword = self.request.get('authPassword', default_value=None)

        if not name or not rssUrl or not quality:
            self.error(400, "Bad Data: Name: %s, rssUrl: %s, quality: %s" % (name, rssUrl, quality))
            return

        existing_s.name = name
        existing_s.slug = newSlug
        existing_s.rssUrl = rssUrl
        existing_s.quality = quality
        existing_s.zipped = zipped
        existing_s.authorizationRequired = authorizationRequired
        existing_s.authUsername = authUsername
        existing_s.authPassword = authPassword

        existing_s.put()

        invalidate_cache("sources")

        self.redirect("/admin/sources/"+newSlug)


class SourcesDeleteHandler(site.BaseHandler):

    def get(self, slug):
        existing = FileSource.get_by_slug(slug)
        if not existing:
            self.not_found()
            return

        if existing.files is not None:
            for mf in existing.files:
                mf.delete()

        existing.delete()
        invalidate_cache("sources")

        self.redirect("/admin/sources")



class TrackedSeriesHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["shows_selected"] = True
        td["shows"] =  self.retrieve("shows")
        self.render(td, 'admin/shows.html')

    def data(self):
        return TrackedSeries.all().order("name").fetch(1000)


class TrackedSeriesCreateHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["shows_selected"] = True
        td["action"] = "create"
        td["qualities"] = ["SD","HD"]

        self.render(td, 'admin/shows_create.html')


    def post(self):
        """
            name        -- string: The name of this tv series
            slug        -- stirng: URL friendly version of the name
            quality     -- string: The quality of the tv series to watch for
            requester   -- user: The user who first asked to track the show
            addDate     -- datetime: When this show started being tracked
            active      -- boolean: Is Active?
            minimumSeason -- integer: Lowest season number to care about
        """
        name = self.request.get('name', default_value=None)
        quality = self.request.get('quality', default_value=None)
        active = self.request.get('active', default_value=True) == "true"
        minimumSeasonTxt = self.request.get('minimumSeason', default_value=None)
        authUsername = self.request.get('authUsername', default_value=None)
        authPassword = self.request.get('authPassword', default_value=None)

        if not name or not quality:
            self.error(400, "Bad Data: Name: %s, quality: %s" % (name, quality))
            return

        name = string.replace(name, ".", " ")

        slug = slugify.slugify(name)
        existing_s = TrackedSeries.get_by_slug(slug)

        if existing_s:
            self.error(400, "A TV show with this name already exists")
            return

        minimumSeason = None
        if minimumSeasonTxt:
            minimumSeason = int(minimumSeasonTxt)

        s = TrackedSeries(name=name, slug=slug, quality=quality, active=active, requester=users.get_current_user(),
            addDate=datetime.now(), minimumSeason=minimumSeason)
        s.put()

        invalidate_cache("shows")

        self.redirect("/admin/shows/"+slug)



class TrackedSeriesInstanceHandler(site.BaseHandler):

    def get(self,slug):
        show = TrackedSeries.get_by_slug(slug)
        if show:
            td = default_template_data()
            td["shows_selected"] = True
            td["show"] = show
            td["minimumSeasonTxt"] = ""
            if show.minimumSeason != None:
                td["minimumSeasonTxt"] = show.minimumSeason

            td["qualities"] = ["SD","HD"]
            td["searchStrings"] = show.getRegExSearchString()

            self.render(td, 'admin/shows_instance.html')
        else:
            self.not_found()


    def post(self,slug):
        """
            name        -- string: The name of this tv series
            slug        -- stirng: URL friendly version of the name
            quality     -- string: The quality of the tv series to watch for
            requester   -- user: The user who first asked to track the show
            addDate     -- datetime: When this show started being tracked
            active      -- boolean: Is Active?
            minimumSeason -- integer: Lowest season number to care about
        """

        existing_s = TrackedSeries.get_by_slug(slug)
        if not existing_s:
            self.error(400, "Cannot find an existing TV show to edit")
            return

        name = self.request.get('name', default_value=None)
        quality = self.request.get('quality', default_value=None)
        active = self.request.get('active', default_value=True) == "true"
        minimumSeasonTxt = self.request.get('minimumSeason', default_value=None)
        authUsername = self.request.get('authUsername', default_value=None)
        authPassword = self.request.get('authPassword', default_value=None)

        if not name or not quality:
            self.error(400, "Bad Data: Name: %s, quality: %s" % (name, quality))
            return

        minimumSeason = None
        if minimumSeasonTxt:
            minimumSeason = int(minimumSeasonTxt)

        existing_s.name = name
        existing_s.slug = slugify.slugify(name)
        existing_s.quality = quality
        existing_s.active = active
        existing_s.minimumSeason = minimumSeason
        existing_s.put()

        invalidate_cache("shows")

        self.redirect("/admin/shows/"+existing_s.slug)


class TrackedSeriesDeleteHandler(site.BaseHandler):

    def get(self, slug):
        existing = TrackedSeries.get_by_slug(slug)
        if not existing:
            self.not_found()
            return

        if existing.files is not None:
            for mf in existing.files:
                mf.delete()

        existing.delete()
        invalidate_cache("shows")

        self.redirect("/admin/shows")



class FilesHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["files_selected"] = True
        td["files"] =  self.retrieve("matchedfiles")
        self.render(td, 'admin/files.html')

    def data(self):
        return MatchedFile.all().order("-date").fetch(1000)


class FilesInstanceHandler(site.BaseHandler):

    def get(self,slug):
        existing = MatchedFile.get_by_slug(slug)
        if existing:
            td = default_template_data()
            td["files_selected"] = True
            td["mf"] = existing
            td["hasContent"] = (existing.content is not None)
            
            self.render(td, 'admin/files_instance.html')
        else:
            self.not_found()


class FilesDeleteHandler(site.BaseHandler):

    def get(self, slug):
        existing = MatchedFile.get_by_slug(slug)
        if not existing:
            self.not_found()
            return

        existing.delete()
        invalidate_cache("matchedfiles")

        self.redirect("/admin/files")
