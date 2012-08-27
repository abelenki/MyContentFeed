__author__ = 'Chris Barbara'

import logging
import os
import string

from google.appengine.api import memcache
from google.appengine.ext import db
import webapp2

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson as json
from models import FileSource, TrackedSeries, MatchedFile


class FeedHandler(webapp2.RequestHandler):
    def get(self):
        td = {
            "newItems": self.retrieve("currentFeedContent")
        }
        self.response.out.write(render_to_string("feed.html", td))

    def retrieve(self, key):
        item = memcache.get(key)
        if item is not None:
            return item
        else:
            item = self.convertToRssItems( MatchedFile.all().order("-date").fetch(25) )
            if item is not None and not memcache.add(key, item):
                logging.error("Memcache set failed on %s" % key)
        return item

    def convertToRssItems(self, newFiles):
    	items = []
    	for newFile in newFiles:
    		items.append( RssItem(newFile) )
    	return items


class RssItem(object):
	def __init__(self, mFile):
		self.title = mFile.name
		self.guid = settings.SITE_URL + mFile.url()
		self.description = self.title
		self.pubDate = mFile.date.strftime("%a, %d %b %Y %H:%M:%S GMT") #<pubDate>Mon, 13 Aug 2012 00:59:56 GMT</pubDate>

		self.link = mFile.fileUrl

	title = ""
	link = ""
	description = ""
	pubDate = ""
	guid = ""
