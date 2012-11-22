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

class testItemNameCreation(TestbedTest):
    
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
        return match


    def testBreakingBad_Normal(self):
        match = self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S07E11.720p.HDTV.x264-IMMERSE")
    	self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertIsNotNone(match.group(1))
        self.assertEquals(match.group(1), "Breaking.Bad")
        self.assertIsNotNone(match.group(2))
        self.assertIsNotNone(match.group(3))
        self.assertIsNone(match.group(4))

    def testBreakingBad_Proper(self):
    	match = self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S05E07.PROPER.720p.HDTV.x264-EVOLVE")
    	self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertIsNotNone(match.group(1))
        self.assertEquals(match.group(1), "Breaking.Bad")
        self.assertIsNotNone(match.group(2))
        self.assertIsNotNone(match.group(3))
        self.assertIsNotNone(match.group(4))

    def testTreme_Normal(self):
        match = self.__searchItemsBySearchStrings("treme", "Treme.S02E08.HDTV.x264-FIRST")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Treme")
        self.assertEquals(match.group(2), "02")
        self.assertEquals(match.group(3), "08")
        self.assertIsNone(match.group(4))

    def testNewsroom_1(self):
        match = self.__searchItemsBySearchStrings("newsroom", "The.Newsroom.S02E08.HDTV.x264-FIRST")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "The.Newsroom")
        self.assertEquals(match.group(2), "02")
        self.assertEquals(match.group(3), "08")
        self.assertIsNone(match.group(4))

    def testNewsroom_1(self):
        match = self.__searchItemsBySearchStrings("the.newsroom", "The.Newsroom.S02E08.HDTV.x264-FIRST")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "The.Newsroom")
        self.assertEquals(match.group(2), "02")
        self.assertEquals(match.group(3), "08")
        self.assertIsNone(match.group(4))

    def testTheHour_UK(self):
        match = self.__searchItemsBySearchStrings("hour uk 2011", "The.Hour.UK.2011.2x01.HDTV.x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Hour.UK.2011")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "01")
        self.assertIsNone(match.group(4))	

    def testTheHour_UK_2(self):
        match = self.__searchItemsBySearchStrings("hour UK 2011", "The.Hour.UK.2011.2x01.HDTV.x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Hour.UK.2011")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "01")
        self.assertIsNone(match.group(4))

    def testFridayNightDinner_US(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday.Night.Dinner.S02E04.HDTV.x264-RiVER")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "02")
        self.assertEquals(match.group(3), "04")
        self.assertIsNone(match.group(4))

    def testFridayNightDinner_UK(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x06.The_Mouse.720p_HDTV_x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "06")
        self.assertEquals(match.group(4), "The.Mouse")

    def testFridayNightDinner_UK_2(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x05.The_Yoghurts.HDTV_x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "05")
        self.assertEquals(match.group(4), "The.Yoghurts")

    def testFridayNightDinner_UK_3(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.Buggy.HDTV_x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "01")
        self.assertEquals(match.group(4), "Buggy")

    def testFridayNightDinner_UK_4(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x01.Buggy.PROPER.HDTV_x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "01")
        self.assertEquals(match.group(4), "Buggy.PROPER")

    def testFridayNightDinner_UK_5(self):
        match = self.__searchItemsBySearchStrings("friday night dinner", "Friday_Night_Dinner.2x06.The_Mouse.INTERNAL.720p_HDTV_x264-FoV")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Friday.Night.Dinner")
        self.assertEquals(match.group(2), "2")
        self.assertEquals(match.group(3), "06")
        self.assertEquals(match.group(4), "The.Mouse.INTERNAL")

    def testFridayNightDinner_UK_5(self):
        match = self.__searchItemsBySearchStrings("luther", "Luther.S01E01.FRENCH.720p.HDTV.x264-JMT")
        self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertEquals(match.group(1), "Luther")
        self.assertEquals(match.group(2), "01")
        self.assertEquals(match.group(3), "01")
        self.assertEquals(match.group(4), "FRENCH")
