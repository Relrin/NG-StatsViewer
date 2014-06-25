import time
import urllib2
from BeautifulSoup import BeautifulSoup

class StatisticsParser():
    
    def __init__(self, user, password, ip = "127.0.0.1"):
        self.__user = user
        self.__pswd = password
        self.__ip = ip
        
        self.__top_level_url = "http://%s" % (self.__ip)
        self.__stattbl =  self.__top_level_url + "/RST_stattbl.htm"
        
        self.__InitAuth()
    
    def setIpAddress(self, newIp):
        self.__ip =  newIp
    
    def getIpAddress(self):
        return self.__ip
    
    def __InitAuth(self):
        """
            Creating objects, which using for auth at main page of yours ADSL
        """
        self.__passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.__passman.add_password(None, self.__top_level_url, self.__user, self.__pswd)
        self.__auth_handler = urllib2.HTTPBasicAuthHandler(self.__passman)
        self.__opener = urllib2.build_opener(self.__auth_handler)
        urllib2.install_opener(self.__opener)
    
    def getNewStats(self):
        """
            Get new statistics from modem
        """
        parsed_colums = []
        errors = []
        try:
            html = urllib2.urlopen(self.__stattbl)
            soup = BeautifulSoup(html.read())
            # get table with statistics and divide on rows (without table header)
            rows = soup.find("table", border="0", width="102%").findAll("tr")
            # getting data from columns
            # first step: getting TxPkts, RxPkts, Tx B/s, Rx B/s,
            cells_packets = rows[4].findAll("td")
            parsed_colums.append(int(cells_packets[2].find("span").getText().encode("utf-8")))
            parsed_colums.append(int(cells_packets[3].find("span").getText().encode("utf-8")))
            parsed_colums.append(int(cells_packets[5].find("span").getText().encode("utf-8")))
            parsed_colums.append(int(cells_packets[6].find("span").getText().encode("utf-8")))
            # second step: getting info about connection speed
            cells_connection_speed = rows[13].findAll("td")
            parsed_colums.append(cells_connection_speed[1].getText().encode("utf-8"))
            parsed_colums.append(cells_connection_speed[2].getText().encode("utf-8"))
        except urllib2.HTTPError, ex:
            errors.append("HTTP Error %d: %s" % (ex.code, ex.msg))
        return parsed_colums, errors
