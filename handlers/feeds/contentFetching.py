__author__ = 'Chris Barbara'

import logging
import urllib
import urllib2
import string

from io import BytesIO
from zipfile import ZipFile

class ContentFetcher(object):
    def __init__(self,itemTitle,itemUrl,sourceUsername,sourcePassword):
        self.sourceUsername = sourceUsername
        self.sourcePassword = sourcePassword
        self.itemTitle = itemTitle
        self.itemUrl = itemUrl

    sourceUsername = None
    sourcePassword = None
    itemTitle = None
    itemUrl = None
    zipFileContent = None
    nzbContent = None

    def getContent(self):
        zipFileUrl = self.__getZipFileUrl()
        if self.__downloadZipFile(zipFileUrl):
            if self.__extractNzbFromZipFile():
                return self.nzbContent

        return None

    def __findNzb(self, namelist):
        for x in namelist:
            if string.find(string.lower(x),".nzb") != -1:
                return x
        return None

    def __extractNzbFromZipFile(self):
        returnValue = False
        try:
            zipF = ZipFile(self.zipFileContent, 'r')
            nzbFileName = self.__findNzb(zipF.namelist())
            if nzbFileName is not None:
                logging.info("NZB Name: " + nzbFileName)
                
                zipExtFile = zipF.open(nzbFileName)
                self.nzbContent = zipExtFile.read()
                returnValue = True
            else:
                loggin.warn("Could not find any .nzb in this zip file for " + self.itemTitle)

            zipF.close()
        except Exception as ex:
            logging.error( "__extractNzbFromZipFile: Error!" )
            logging.error( ex )

        return returnValue

    def __downloadZipFile(self,zipFileUrl):
        try:
            req = urllib2.Request(zipFileUrl)
            req.add_header('Referer', self.itemUrl)
            req.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)")
            req.add_header('Cookie', "uid=" + self.sourceUsername + "; pass=" + self.sourcePassword)
            
            response = urllib2.urlopen(req)

            f = BytesIO(response.read())
            self.zipFileContent = f
            return True
        except Exception as ex:
            logging.error( "__downloadZipFile: Error trying to download " + zipFileUrl )
            logging.error( ex )

        return False

    def __getZipFileUrl(self):
        detailsPageUrl = self.itemUrl
        zipFileUrl = string.replace(detailsPageUrl,"nzb-details.php","nzb-download.php")
        zipFileUrl = string.replace(zipFileUrl,"&hit=1","")
        name = urllib.quote(self.itemTitle)
        zipFileUrl = zipFileUrl + "&name=" + name
        
        logging.debug(zipFileUrl)
        
        return zipFileUrl


    def testGetZipFileUrl(self):
        return self.__getZipFileUrl()

    def testDownloadZipFile(self,zipFileUrl):
        return self.__downloadZipFile(zipFileUrl)

    def testGetZipFileContent(self):
        return self.zipFileContent

    def testExtractNzbFromZipFile(self, zipContent):
        self.zipFileContent = zipContent
        return self.__extractNzbFromZipFile()

    def testGetNzbContent(self):
        return self.nzbContent

