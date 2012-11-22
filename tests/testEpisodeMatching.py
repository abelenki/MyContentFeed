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
        searchTitle = string.replace(itemTitle, "_", ".")
        match = regEx.search(searchTitle)
        if match is not None:
            groupItems = match.groups()
            if(len(groupItems) > 3) and (match.group(4) is not None):
                    return self.__isEpisodeNameOrProperText(match.group(4))
            return True
        return False

    def __isEpisodeNameOrProperText(self, text):
        if self.__isDifferentLanguage(text, "FRENCH") or self.__isDifferentLanguage(text, "GERMAN") or self.__isDifferentLanguage(text, "HEBREW") or self.__isDifferentLanguage(text, "SPANISH"):
            return False
        
        normalized = text.lower()
        if normalized.endswith("proper") or normalized.endswith("repack") or normalized.endswith("internal") or normalized.endswith("real"):
            return True

        return True

    def __isDifferentLanguage(self, text, language):
        return (text.endswith(language) or text.find("."+language+".") <> -1 or text.find("."+language) <> -1)

    def testBreakingBad(self):
    	self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S02E08.HDTV.x264-FIRST"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S07E11.720p.HDTV.x264-IMMERSE"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Inside.Breaking.Bad.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S07E11.INTERNAL.720p.HDTV.x264-IMMERSE"), True)

    def testTreme(self):
    	self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S02E08.HDTV.x264-FIRST"), True)
    	self.assertEquals(self.__searchItemsBySearchStrings("Treme", "Extreme.Home.Make.Over.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Extreme.Home.Make.Over.S02E08.HDTV.x264-FIRST"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("treme", "Treme.S02E08.PROPER.HDTV.x264-FIRST"), True)
    	
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
        self.assertEquals(self.__searchItemsBySearchStrings("girls", "Girls.S02E08.REPACK.HDTV.x264-FIRST"), True)

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

    def testTheHour(self):
        self.assertEquals(self.__searchItemsBySearchStrings("the hour uk 2011", "The.Hour.UK.2011.2x01.HDTV.x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("the hour UK 2011", "The.Hour.UK.2011.2x01.HDTV.x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("hour uk 2011", "The.Hour.UK.2011.2x02.HDTV.x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("hour UK 2011", "The.Hour.UK.2011.2x02.HDTV.x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("the hour uk", "The.Hour.UK.2011.2x01.HDTV.x264-FoV"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("the hour UK", "The.Hour.UK.2011.2x01.HDTV.x264-FoV"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("hour uk", "The.Hour.UK.2011.2x02.HDTV.x264-FoV"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("hour UK", "The.Hour.UK.2011.2x02.HDTV.x264-FoV"), False)

    def testFridayNightDinner(self):
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday.Night.Dinner.S02E04.HDTV.x264-RiVER"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday.Night.Dinner.S02E03.HDTV.x264-TLA"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x06.The_Mouse.720p_HDTV_x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x05.The_Yoghurts.HDTV_x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.Buggy.HDTV_x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday.Night.Dinner.2x05.The.Yoghurts.HDTV_x264-FoV"), True)

    def testFridayNightDinner_Languages(self):
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.French.Fries.HDTV_x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.French.Fries.FRENCH.HDTV_x264-FoV"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.Fuck.The.French.HDTV_x264-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.Fuck.The.French.FRENCH.HDTV_x264-FoV"), False)

    def testLuther(self):
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.2x04.HDTV.XviD-FoV"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S02E04.HDTV.XviD-fov"), True)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S01E01.FRENCH.720p.HDTV.x264-JMT"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S01E01.The.Episode.Name.FRENCH.720p.HDTV.x264-JMT"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S01E01.The.Episode.Name.FRENCH.PROPER.720p.HDTV.x264-JMT"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S01E01.The.Episode.Name.FRENCH.INTERNAL.720p.HDTV.x264-JMT"), False)
        self.assertEquals(self.__searchItemsBySearchStrings("luther", "Luther.S01E01.The.Episode.Name.720p.HDTV.x264-JMT"), True)
