__author__ = 'Chris Barbara'

import logging
import re

from datetime import datetime
from django.conf import settings

from utils import slugify
from feedparser import feedparser
from models import TrackedSeries, FileSource, MatchedFile
from contentFetching import ContentFetcher

class ParseAndSearch(object):

    @staticmethod
    def go(activeShows, allSources):
        fd = FeedDownloader()
        latestSourcesAndFeedItems = fd.loadSources(allSources)

        if latestSourcesAndFeedItems == None or len(latestSourcesAndFeedItems) == 0:
            logging.info("No items loaded from the sources, exiting ParseAndSearch.go")
            return False

        somethingChanged = False
        for show in activeShows:
            for loadedSource in latestSourcesAndFeedItems:
                if loadedSource.source.quality == show.quality:
                    logging.debug("Going to search the source " + loadedSource.source.name + " for the show " + show.name)
                    
                    searcher = FeedItemSearcher(loadedSource, show)
                    if searcher.isNewFileFound() == True:
                        matchedFilesToCreate = searcher.createMatchedFilesCreators()
                        
                        for mf in matchedFilesToCreate:
                            if mf.create():
                                somethingChanged = True

        return somethingChanged

class FeedDownloader(object):

    def loadSources(self, allSources):
        latestFeedItems = []

        for src in allSources:
            srcItems = self.fetchSource(src)
            if srcItems is not None:
                latestFeedItems.append(SourceAndItems(src,srcItems))

        return latestFeedItems

    def fetchSource(self,source):
        feedUrl = source.rssUrl
        feed = None
        try:
            feed = feedparser.parse( feedUrl )
            logging.debug("loaded the source from " + feedUrl)
        except Exception as ex:
            logging.error( "Error calling " + feedUrl )
            logging.error( ex )
            return None

        return self.parseFeed(feed,source.quality)

    def parseFeed(self,feed,quality):
        parsedItems = []
        for item in feed[ "items" ]:
            parsedItems.append( FeedItem(item,quality) )

        return parsedItems

class SourceAndItems(object):
    def __init__(self, source, feedItems):
        self.source = source
        self.feedItems = feedItems

    source = None
    feedItems = None 

class FeedItem(object):
    def __init__(self, item, quality):
        self.title = item["title"]
        self.url = item["link"]
        self.quality = quality

    title = ""
    url = ""
    quality = "SD"

    def __eq__(self, other):
        return self.title == other.title

    def __hash__(self):
        return self.title.__hash__()

class FeedItemSearcher(object):
    def __init__(self, sourceAndItems, show ):
        self.source = sourceAndItems.source
        self.items = sourceAndItems.feedItems
        self.show = show

    source = None
    items = None
    show = None

    allMatchingFiles = None

    def isNewFileFound(self):
        searchString = self.show.getRegExSearchString()
        #logging.debug("using the regex: " + searchString)
        return self.__searchItemsBySearchStrings(searchString)

    def __searchItemsBySearchStrings(self, searchString):
        found = False
        regEx = re.compile(searchString, re.I)

        for item in self.items:
            match = regEx.search(item.title)
            if match is not None:
                found = True
                originalTitle = item.title

                item.title = match.group(1) + " S" + match.group(2) + "E" + match.group(3)

                groupItems = match.groups()
                if(len(groupItems) > 3) and (match.group(4) is not None):
                    item.title = item.title + " " + match.group(4)

                item.title = item.title + " (" + item.quality + ")"

                logging.debug("the file " + originalTitle + " has been converted to " + item.title + " and found as a match for " + self.show.name)

                if self.allMatchingFiles == None:
                    self.allMatchingFiles = set([item])
                else:
                    self.allMatchingFiles.add(item)

        return found

    def createMatchedFilesCreators(self):
        ret = []
        for match in self.allMatchingFiles:
            ret.append(MatchedFilesCreator(self.show, self.source, match))
        return ret

class MatchedFilesCreator(object):
    def __init__(self, show, source, item):
        self.source = source
        self.item = item
        self.show = show

    source = None
    item = None
    show = None

    def create(self):
        name = self.item.title
        slug = slugify.slugify(name)

        existing = MatchedFile.get_by_slug(slug)
        if existing:
            logging.debug("the file " + name + " already exists")
            return False

        url = None
        content = None

        if self.source.zipped == False and self.source.authorizationRequired == False:
            url = self.item.url
        else:
            content = self.getContentForFile()
            if content is None:
                logging.warn("no content found when looking for " + name + ", no matching file will be created")
                return False
            url = settings.SITE_URL + MatchedFile.get_url_for_slug(slug) + "/content"

        logging.info("Adding the new matched file " + name)
        newFile = MatchedFile( name=name, slug=slug, date=datetime.now(), fileUrl=url, content=content,
            source=self.source, series=self.show )
        newFile.put()

        return True

    def getContentForFile(self):
        cf = ContentFetcher(self.item.title, self.item.url, self.source.authUsername, self.source.authPassword)
        return cf.getContent()

