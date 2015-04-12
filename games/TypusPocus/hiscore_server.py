#
# A simple http server for saving hi scores
# pyweek - PyAr2 - Typos Pocus
#

import SimpleHTTPServer
import BaseHTTPServer
import time
import os

class Singleton:
    __single = None
    def __init__( self ):
        if Singleton.__single:
            raise Singleton.__single
        Singleton.__single = self    

class HiScoreData( Singleton ):

    POINTS = 0
    COMMIT_TIME = 1         # added for comparing when the score is the same. older time wins
    NAME = 2
    WHEN = 3
    IPADDR = 4
   
    HISCORE_FILENAME = 'hi_scores.txt'
    
    def __init__( self ):
        Singleton.__init__( self )
        self.hiScores = []
        self.loadHiScores()
        self.save_counter = 0

    def loadHiScores(self):
        try:
            f = file(HiScoreData.HISCORE_FILENAME)
            self.hiScores = []
            for line in f.readlines():
                # ignore comments
                if line.startswith("#"):
                    continue
                (score,when,name,ipaddr) = line.split(',')
                self.hiScores.append( (int(score),float(when),name,ipaddr[:-1]) )
            f.close()
        except IOError:
            # file not found, no problem
            pass

    def saveHiScores(self):
        try:
            f = file(HiScoreData.HISCORE_FILENAME,'w')
            for i in self.hiScores:
                f.write('%i,%f,%s,%s\n' % ( i[0],i[1],i[2],i[3] ) )
            f.close()
        except Exception, e:
            print 'Could not save hi scores'
            print e

    def addHiScore( self, score, name, ipaddr):
        # safe replacement
        for l in name:
            if not l.isalnum():
                name = name.replace(l,'_')

        real_when = -time.time()
        self.hiScores.append( (int(score),real_when,name,ipaddr) )
        self.hiScores.sort()
        self.hiScores.reverse()

        self.save_counter += 1
        if self.save_counter % 1 == 0:
            self.saveHiScores()

    def listHiScores( self ):
        # only return the 50 first records
        return self.hiScores[:50]

def Handle( x = Singleton ):
    try:
        single = x()
    except Singleton, s:
        single = s
    return single    


class HiScoresHandler( SimpleHTTPServer.SimpleHTTPRequestHandler ):

    def hs_listHiScores(self):

        self.wfile.write('<!DOCTYPE html PUBLIC "-//w3c//dtd html 4.0 transitional//en">\n')
        self.wfile.write("<html>\n<head>\n<title>Typos Pocus - Hi Scores</title>\n</head>\n")
        linestr ="<body>\n"
        data = Handle(HiScoreData)

        linestr +='<center>'
        linestr +='<table BORDER=0 BGCOLOR="#dedede" NOSAVE>\n'
        linestr +="<th><center>Typos Pocus - Hi Scores</center></th>"
        linestr +="<tr>\n"
        linestr +="\t<td><b>Points</b></td>\n"
        linestr +="\t<td><b>Name</b></td>\n"
        linestr +="\t<td><b>IP Address</b></td>\n"
        linestr +="\t<td><b>When</b></td>\n"
        linestr +="</tr>\n"

        index = 0
        for item in data.listHiScores():
            if index % 2 == 0:
                linestr +='<tr BGCOLOR="#eeeeee" NOSAVE>\n'
            else:
                linestr +='<tr BGCOLOR="#dedede" NOSAVE>\n'

            index += 1

            linestr +="<!-- entry -->"
            try:
                for j in range(0,len(item)):
                    if j % len(item) == HiScoreData.COMMIT_TIME:
                        continue
                    linestr +="<td>%s</td>" % item[j]
                linestr +="<td>%s</td>" % time.ctime(-item[HiScoreData.COMMIT_TIME])
                linestr +="</tr>\n"
            except Exception, e:
                print 'Error:'
                print str(e)
                print item

        linestr +="</table>\n"
        linestr +='</center>\n'
        linestr +='</br></br>\n'
        linestr +='<p>Download the latest version of Typos Pocus from <a href="http://www.pyweek.org/e/PyAr2/">here</a>'
        linestr +="</body>\n</html>\n"
        self.wfile.write('\n' + linestr)

    def hs_listHiScoresInXML(self):

        data = Handle(HiScoreData)
        linestr = '<?xml version="1.0"?>\n'
        linestr += '<hiscores version="1.0">\n'

        for i in data.listHiScores():
            linestr += '\t<entry>\n'
            try:
                len_i = len(i)
                for j in range(0,len_i):
                    if j % len_i == 0:
                        linestr +="\t\t<score>%d</score>\n" % i[j]
                    if j % len_i == 1:
                        linestr +="\t\t<when>%f</when>\n" % -i[j]
                    if j % len_i == 2:
                        linestr +="\t\t<name>%s</name>\n" % i[j]
                    if j % len_i == 3:
                        linestr +="\t\t<ipaddress>%s</ipaddress>\n" % i[j]
            except Exception, e:
                print 'Error:'
                print str(e)
                print i
            linestr +="\t</entry>\n"
        linestr +='</hiscores>\n'
        self.wfile.write(linestr)

    def hs_(self):
        page = """
<!DOCTYPE html PUBLIC "-//w3c//dtd html 4.0 transitional//en">
<html>
<head><title>Typos Pocus - Hi Scores</title>
</head>
<body>
<h2>Welcome to Typos Pocus - Hi Scores</h2>
<P>Available commands:
<ul>
    <li><a href="listHiScores">listHiScores</a></li>
    <li><a href="listHiScoresInXML">listHiScoresInXML</a></li>
</ul>
</body>
</html>"""
        self.wfile.write(page)

    def hs_addHiScore(self):
        if len(self.hiscore_params) == 2:
            data = Handle(HiScoreData)
            data.addHiScore( self.hiscore_params[0], self.hiscore_params[1], self.client_address[0])
            self.wfile.write('<html><head><title>Hi Scores Added</title></head><body><h1>HiScore (%s,%s)Added</h1></body></html>' % ( self.hiscore_params[0], self.hiscore_params[1]) )
        else:            
            self.send_error(400, "invalid parameters")

    def do_GET(self):
        """Serve a GET request."""

        self.hiscore_command = self.path[1:].split('/')  

        if len(self.hiscore_command) > 0:
                mname = 'hs_' + self.hiscore_command[0]
                if not hasattr(self, mname):
                    self.send_error(501, "Unsupported method (%s)" % `self.hiscore_command[0]`)
                    return
                self.hiscore_params = self.hiscore_command[1:]
                method = getattr(self, mname)
                method()
        else:
            self.send_error(400, "Invalid request" )
            return

    def do_HEAD(self):
        pass

def main(HandlerClass = HiScoresHandler, ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == "__main__":
    print 'Remember: To change the listening port, just add the new one to the command line'
    print 'For example:'
    print '\tpython hiscore_server 80'
    main()
