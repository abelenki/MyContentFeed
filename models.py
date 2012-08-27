__author__ = 'Chris Barbara'

import os
import datetime
import logging
import string
from google.appengine.ext import db


class FileSource(db.Model):
    """A source for files

    Properties:
    name        -- string: The name of this file source
    slug        -- stirng: URL friendly version of the name
    rssUrl      -- string: The rss feed url 
    quality     -- string: The quality of the files in this source
    zipped      -- boolean: Are the files from this source zip files?
    authorizationRequired   -- boolean: When downloading the file, is authorization required?
    authUsername    -- string: authorization username
    authPassword    -- string: authorization password

    """

    @staticmethod
    def get_by_slug(slug):
        return FileSource.all().filter('slug = ', slug).get()

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    quality = db.StringProperty(required=True,choices=["HD","SD"])
    rssUrl = db.StringProperty(required=True)
    quality = db.StringProperty(required=True)
    zipped = db.BooleanProperty(required=True)
    authorizationRequired = db.BooleanProperty(required=True)
    authUsername = db.StringProperty(required=False)
    authPassword = db.StringProperty(required=False)


    def url(self):
        return "/source/" + self.slug

    def sid(self):
        return unicode(self.key())


class TrackedSeries(db.Model):
    """A tv series to track

    Properties:
    name        -- string: The name of this tv series
    slug        -- stirng: URL friendly version of the name
    quality     -- string: The quality of the tv series to watch for
    requester   -- user: The user who first asked to track the show
    addDate     -- datetime: When this show started being tracked
    active      -- boolean: Is Active?
    minimumSeason -- integer: Lowest season number to care about

    """

    @staticmethod
    def get_by_slug(slug):
        return TrackedSeries.all().filter('slug = ', slug).get()

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    quality = db.StringProperty(required=True, choices=["HD","SD"])
    requester = db.UserProperty(required=True)
    addDate = db.DateTimeProperty(required=True)
    active = db.BooleanProperty(required=True)
    minimumSeason = db.IntegerProperty(required=False)

    def url(self):
        return "/series/" + self.slug

    def sid(self):
        return unicode(self.key())

    def getRegExSearchString(self):
        regexIfied = string.replace(self.name, " ", ".")
        regexIfied = string.replace(regexIfied, ".", "\.")
        regexIfied = "^(?:the\.)?(" + regexIfied + ")\.S(\d+)E(\d+)\.(?:(REPACK|PROPER|REAL|INTERNAL)\.)?(?:(?:(?:480|720|1080)[i|p])\.)?[P|H]DTV.*$"
        return regexIfied


class MatchedFile(db.Model):
    """A file from a feed that was a match

    Properties:
    name        -- string: The file name
    slug        -- stirng: URL friendly version of the name
    fileUrl     -- string: The original URL of the file
    date        -- datetime: When this file was found
    content     -- text: The actual file content

    source      -- FileSource: the source
    series      -- TrackedSeries: the series
    
    """

    @staticmethod
    def get_by_slug(slug):
        return MatchedFile.all().filter('slug = ', slug).get()

    @staticmethod
    def get_url_for_slug(slug):
        return "/file/" + slug

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    fileUrl = db.StringProperty(required=True)
    date = db.DateTimeProperty(required=True)
    content = db.TextProperty(required=False)

    source = db.ReferenceProperty(FileSource, required=True, collection_name="files")
    series = db.ReferenceProperty(TrackedSeries, required=True, collection_name="files")


    def url(self):
        return "/file/" + self.slug

    def sid(self):
        return unicode(self.key())

