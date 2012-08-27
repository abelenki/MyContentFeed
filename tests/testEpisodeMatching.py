__author__ = 'Chris Barbara'

import os
import re
import string
import unittest
import logging

from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import users

from base import TestbedTest
from models import TrackedSeries

class testEpisodeMatching(TestbedTest):
    
    def __getRegExForSearchString(self, searchString):
        ts = TrackedSeries(name=searchString, slug=searchString, quality="HD", active=True, requester=users.get_current_user(),
            addDate=datetime.now(), minimumSeason=None)

        regexIfied = ts.getRegExSearchString()
        print regexIfied
        return re.compile(regexIfied, re.I)

    def __searchItemsBySearchStrings(self, searchString, itemTitle):
        regEx = self.__getRegExForSearchString(searchString)
        match = regEx.search(itemTitle)
        return match is not None


    def testBreakingBad(self):
    	self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S02E08.HDTV.x264-FIRST"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S07E11.720p.HDTV.x264-IMMERSE"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Inside.Breaking.Bad.S02E08.HDTV.x264-FIRST"), False)

    def testTreme(self):
    	self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S02E08.HDTV.x264-FIRST"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("Treme", "Extreme.Home.Make.Over.S02E08.HDTV.x264-FIRST"), False)
    	
    def testNewsroom(self):
    	self.assertEquals(self.__searchItemsBySearchStrings("newsroom", "The.Newsroom.S02E08.HDTV.x264-FIRST"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("the.newsroom", "The.Newsroom.S02E08.HDTV.x264-FIRST"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("newsroom", "Wheres.My.Newsroommate.Today.Live.2012.S02E08.HDTV.x264-FIRST"), False)

    def testGirls(self):
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Girls.S02E08.HDTV.x264-FIRST"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "New.Girl.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Bad.Girls.2012.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Bad Girls 2012 S02E08 HDTV x264 - FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Bad.Girls.Club.2012.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Bad.GirlsClub.2012.S02E08.HDTV.x264-FIRST"), False)

    def testDVDRips(self):
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S04.DVDRip.XviD-REWARD"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S04E23.DVDRip.XviD-REWARD"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S04E23.BDRip.x264-REWARD"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S02E08.HDTV.x264-FIRST"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.720p.HDTV.x264-IMMERSE"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.720i.HDTV.x264-IMMERSE"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.Athletes.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.1080p.HDTV.x264-IMMERSE"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.1080i.HDTV.x264-IMMERSE"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.480p.HDTV.x264-IMMERSE"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("fringe", "Fringe.S07E11.480i.HDTV.x264-IMMERSE"), True)

    def testPropersAndInternals(self):
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.REPACK.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.PROPER.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.INTERNAL.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.REAL.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.REPACK.720p.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.PROPER.720p.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.INTERNAL.720p.HDTV.x264-FiHTV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S01E10.REAL.720p.HDTV.x264-FiHTV"), True)
