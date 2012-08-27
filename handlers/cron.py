__author__ = 'Chris Barbara'

import datetime
import calendar
import logging
import os
import string
import time
import json

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import deferred
#from google.appengine.api import taskqueue
import webapp2

from datetime import datetime
from models import TrackedSeries, FileSource
from feeds import filesourceparsing
from time import mktime

def searchTvShowsDeferred(activeShowKeys):
    if activeShowKeys is None:
        logging.info("No activeShowKeys found, exiting searchTvShowsDeferred")
        return
    if len(activeShowKeys) == 0:
        logging.info("0 activeShowKeys found, exiting searchTvShowsDeferred")
        return

    activeShows = []
    for key in activeShowKeys:
        show = TrackedSeries.get(key)
        if show is not None:
            activeShows.append(show)

    if len(activeShows) == 0:
        logging.info("0 activeShows found from the keys, exiting searchTvShowsDeferred")
        return

    allSources = memcache.get("sources")
    if allSources is None:
        allSources = FileSource.all().order("name").fetch(1000)
        if allSources is not None:
            memcache.add("sources", allSources)
        else:
            return

    if filesourceparsing.ParseAndSearch.go(activeShows, allSources):
        invalidate_cache()


def invalidate_cache():
    if not memcache.delete("currentFeedContent"):
        logging.error("Memcache delete failed on currentFeedContent")

    memcache.delete("matchedfiles")

    #no real need to immedietly refresh the feed, let it happen on next page load
    #taskqueue.add(url='/feed', method="GET")

class BaseHandler(webapp2.RequestHandler):

    def retrieve(self, key):
        item = memcache.get(key)
        if item is not None:
            return item
        else:
            item = self.data()
            if item is not None and not memcache.add(key, item):
                logging.error("Memcache set failed on %s" % key)
        return item


class SearchTvShowsHandler(BaseHandler):

    def get(self):
        allTvShows = self.retrieve("shows")

        activeShowKeys = []
        if allTvShows is not None:
            for show in allTvShows:
                if show.active:
                    activeShowKeys.append(show.sid())

        if len(activeShowKeys) > 0:
            memcache.add("SearchTvShowsHandler",activeShowKeys)

            deferred.defer(searchTvShowsDeferred, activeShowKeys)
            #searchTvShowsDeferred(activeShowKeys)

            self.response.set_status(200)
        else:
            self.response.set_status(304)

    def data(self):
        return TrackedSeries.all().order("name").fetch(1000)


class SearchMoviesHandler(BaseHandler):
    def get(self):

        self.response.set_status(200)
