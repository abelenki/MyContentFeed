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
        match = regEx.search(itemTitle)
        return match


    def testBreakingBad_Normal(self):
        match = self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S07E11.720p.HDTV.x264-IMMERSE")
    	self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertIsNotNone(match.group(1))
        self.assertIsNotNone(match.group(2))
        self.assertIsNotNone(match.group(3))
        self.assertIsNone(match.group(4))

    def testBreakingBad_Proper(self):
    	match = self.__searchItemsBySearchStrings("breaking.bad", "Breaking.Bad.S05E07.PROPER.720p.HDTV.x264-EVOLVE")
    	self.assertIsNotNone(match)
        groupItems = match.groups()

        self.assertEquals(len(groupItems), 4)
        self.assertIsNotNone(match.group(1))
        self.assertIsNotNone(match.group(2))
        self.assertIsNotNone(match.group(3))
        self.assertIsNotNone(match.group(4))
    	