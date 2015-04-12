#
# A simple http server for saving hi scores
# pyweek - PyAr2 - Typos Pocus
#

import urllib2
import xml.dom.minidom
import hiscore_server

HISCORE_SERVER = 'typospocus.servegame.org'
HISCORE_PORT = 8080

hiscore_server.HiScoreData.HISCORE_FILENAME = 'hi_scores_local.txt'

class HiScoreClient:

    def __init__(self):
        self.__dom = None
        self.__hiscores = []
        self.__internet = True

    #
    #  add Hi Scores
    #
    def addLocalHiScore( self, score, name ):
        data = hiscore_server.Handle(hiscore_server.HiScoreData)
        data.addHiScore( score, name, 'localhost' )

    def addHiScore( self, score, name ):
        if self.__internet:
            try:
                urllib2.urlopen('http://%s:%s/addHiScore/%d/%s' % (HISCORE_SERVER,HISCORE_PORT,score,name) )
            except Exception, e:
                print 'Internet connection failed... using local hiscores'
                self.__internet = False
                self.addLocalHiScore( score, name )
        else:
                self.addLocalHiScore( score, name )


    #
    # list Hi Scores
    #
    def listLocalHiScores( self ):
        data = hiscore_server.Handle(hiscore_server.HiScoreData)
        self.__hiscores = data.listHiScores()

    def listHiScores( self ):
        if self.__internet:
            try:
                f = urllib2.urlopen('http://%s:%s/listHiScoresInXML'% (HISCORE_SERVER,HISCORE_PORT) )
                document = f.read()
                self.__dom = xml.dom.minidom.parseString(document)
                self.handleXMLScores()

            except Exception, e:
                print 'Internet connection failed... using local hiscores'
                self.__internet = False
                self.listLocalHiScores()
        else:
            self.listLocalHiScores()

        return self.__hiscores

    def handleXMLScores(self):
        self.__hiscores = []
        entries = self.__dom.getElementsByTagName("entry")
        for entry in entries:
            score = entry.getElementsByTagName("score")[0]
            scoreStr = self.getText(score.childNodes)
            name= entry.getElementsByTagName("name")[0]
            nameStr = self.getText(name.childNodes)
            ipaddr = entry.getElementsByTagName("ipaddress")[0]
            ipaddrStr = self.getText(ipaddr.childNodes)
            theTime = entry.getElementsByTagName("when")[0]
            theTimeStr = self.getText(theTime.childNodes)
            self.__hiscores.append( (int(scoreStr), nameStr, ipaddrStr, theTimeStr) )

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

if __name__ == '__main__':
    a = HiScoreClient()
    print a.listHiScores()
    for i in range(1,100):
        a.addHiScore(i,'usu,<>,ario_test_%s' % i )
    print a.listHiScores()
