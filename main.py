
__author__ = 'Chris Barbara'

import webapp2
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))

import appengine_config # Make sure this happens

from django.conf import settings

from google.appengine.api import memcache
from google.appengine.api import users
from handlers import site, admin, cron, feed

HOME = [
    ('/', site.HomePageHandler)
]
FEED = [
    (r'/feed', feed.FeedHandler)
]
FILES = [
    (r'/file/(.*)/content', site.FileContentHandler),
    (r'/file/(.*)', site.FileHandler)
]
CRON = [
    (r'/cron/fetch/tv', cron.SearchTvShowsHandler),
    (r'/cron/fetch/movies', cron.SearchMoviesHandler)
]
ADMIN = [
	(r'/admin', admin.RootHandler),
	(r'/admin/sources', admin.SourcesHandler),
	(r'/admin/sources/create', admin.SourcesCreateHandler),
    (r'/admin/sources/(.*)/delete', admin.SourcesDeleteHandler),
	(r'/admin/sources/(.*)', admin.SourcesInstanceHandler),

	(r'/admin/shows', admin.TrackedSeriesHandler),
	(r'/admin/shows/create', admin.TrackedSeriesCreateHandler),
    (r'/admin/shows/(.*)/delete', admin.TrackedSeriesDeleteHandler),
	(r'/admin/shows/(.*)', admin.TrackedSeriesInstanceHandler),

    (r'/admin/files', admin.FilesHandler),
    (r'/admin/files/(.*)/delete', admin.FilesDeleteHandler),
    (r'/admin/files/(.*)', admin.FilesInstanceHandler)
]

ROUTES = []
ROUTES.extend(HOME)
ROUTES.extend(FEED)
ROUTES.extend(FILES)
ROUTES.extend(CRON)
ROUTES.extend(ADMIN)
ROUTES.append((r'/.*$', site.NotFoundHandler))

if settings.DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)

app = webapp2.WSGIApplication(ROUTES, debug=settings.DEBUG)
