__author__ = 'Chris Barbara'

import os
import re
import string
import unittest

from google.appengine.ext import db
from google.appengine.api import users

from base import TestbedTest
from io import BytesIO
from handlers import feeds
from feeds import contentFetching

class testDownloadZip(TestbedTest):

	#your going to want to replace these with your own nzbmatrix.com cookie values
	sourceUsername = "XXXXXXXXXX"
	sourcePassword = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"

	def testZipFileUrl(self):
		cf = contentFetching.ContentFetcher(
			"Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS",
			"http://nzbmatrix.com/nzb-details.php?id=1366606&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		self.assertEquals(cf.testGetZipFileUrl(), "http://nzbmatrix.com/nzb-download.php?id=1366606&name=Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS")

	def testZipFileUrlWithSpaces(self):
		cf = contentFetching.ContentFetcher(
			"Attack of the 50 Foot Cheerleader HDTV x264 - SYS",
			"http://nzbmatrix.com/nzb-details.php?id=1366606&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		self.assertEquals(cf.testGetZipFileUrl(), "http://nzbmatrix.com/nzb-download.php?id=1366606&name=Attack%20of%20the%2050%20Foot%20Cheerleader%20HDTV%20x264%20-%20SYS")

	def testDownloadFile(self):
		cf = contentFetching.ContentFetcher(
			"Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS",
			"http://nzbmatrix.com/nzb-details.php?id=1366606&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		zipFileUrl = "http://www.chrisbarbara.com/mytvfeedtests/sampledata.txt"
		#"http://nzbmatrix.com/nzb-download.php?id=1366606&name=Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS"

		self.assertEquals(cf.testDownloadZipFile(zipFileUrl), True)
		content = cf.testGetZipFileContent()
		self.assertIsNotNone(content)

		bytes = BytesIO("simple sample data")
		self.assertEqual(content.getvalue(),bytes.getvalue())

	def testDownloadSampleZipFile(self):
		cf = contentFetching.ContentFetcher(
			"Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS",
			"http://nzbmatrix.com/nzb-details.php?id=1366606&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		zipFileUrl = "http://www.chrisbarbara.com/mytvfeedtests/sampledata.zip"

		self.assertEquals(cf.testDownloadZipFile(zipFileUrl), True)
		content = cf.testGetZipFileContent()
		self.assertIsNotNone(content)

		f = open("tests/sampledata.zip", "rb")
		bytes = BytesIO(f.read())
		f.close()
		self.assertEqual(content.getvalue(),bytes.getvalue())


	def testDownloadZipFile(self):
		cf = contentFetching.ContentFetcher(
			"The Avengers 2012 DVDRip XviD AC3 NYDIC",
			"http://nzbmatrix.com/nzb-details.php?id=1358789&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		
		zipFileUrl = cf.testGetZipFileUrl()
		self.assertEquals(zipFileUrl, "http://nzbmatrix.com/nzb-download.php?id=1358789&name=The%20Avengers%202012%20DVDRip%20XviD%20AC3%20NYDIC")
		
		#NOTE: you will want to uncomment this return value out if your running out of files to DL daily
		#return
		self.assertEquals(cf.testDownloadZipFile(zipFileUrl), True)
		content = cf.testGetZipFileContent()
		self.assertIsNotNone(content)

		f = open("tests/sampledata.zip", "rb")
		bytes = BytesIO(f.read())
		f.close()
		self.assertEqual(content.getvalue(),bytes.getvalue())

	def testExtractNzbFromZipFile(self):
		cf = contentFetching.ContentFetcher(
			"Attack.of.the.50.Foot.Cheerleader.HDTV.x264-SYS",
			"http://nzbmatrix.com/nzb-details.php?id=1366606&hit=1",
			self.sourceUsername, self.sourcePassword
		)
		
		f = open("tests/sampledata.zip", "rb")
		bytes = BytesIO(f.read())
		f.close()

		self.assertEqual(cf.testExtractNzbFromZipFile(bytes), True)

		nzbFile = open("tests/sampledata.nzb", "r")
		self.assertEqual(cf.testGetNzbContent(), nzbFile.read() )
		nzbFile.close()

