import time
import urllib2
from BeautifulSoup import BeautifulSoup

class StatisticsParser():
    
    def __init__(self, user, password, ip = "127.0.0.1"):
        self.__user = user
        self.__pswd = password
        self.__ip = ip
        
        self.__top_level_url = "http://%s" % (self.__ip)
        self.__trafficMeter =  self.__top_level_url + "/traffic_meter.htm"
        
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
        parsed_rows = []
        errors = []
        try:
            html = urllib2.urlopen(self.__trafficMeter)
            soup = BeautifulSoup(html.read())
            # get table with statistics and divide on rows (without table header)
            rows = soup.find("table", border="1", cellspacing="0", cellpadding="0", width="100%").findAll("tr")[2:]
            for row in rows:
                # get columns on every row
                cells = row.findAll("td")
                # there we are getting data from every column
                field_name = cells[0].find("span").getText().encode("utf-8")
                Connection_Time = cells[1].find("span").getText().encode("utf-8")
                Upload_Avg = cells[2].findAll("p")
                Download_Avg = cells[3].findAll("p")
                Total_Avg = cells[4].findAll("p")
                
                # prepare for appending to result list
                upload_avg_list = []
                download_avg_list = []
                total_avg_list = []
                for item in Upload_Avg:
                    upload_avg_list.append(int(item.getText().replace('/', '').strip()))
                for item in Download_Avg:
                    download_avg_list.append(int(item.getText().replace('/', '').strip()))
                for item in Total_Avg:
                    total_avg_list.append(int(item.getText().replace('/', '').strip()))
                    
                parsed_rows.append((field_name, Connection_Time, upload_avg_list, download_avg_list, total_avg_list))
        except urllib2.HTTPError, ex:
            errors.append("HTTP Error %d: %s" % (ex.code, ex.msg))
        return parsed_rows, errors