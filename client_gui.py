#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import ConfigParser
import HtmlParser
from PyQt4 import QtGui, QtCore, uic

def addDotsInNumbers(data):
    '''
        string with dot separated numbers, which inserted after every third digit from right to left
    '''
    result=''
    data=str(data).split(' ')
    for phrase in data:
        if phrase.isdigit() and len(phrase)>3:
            buf = phrase[::-1]
            result += format(int(buf), ',d')[::-1]+" "
        else:
            result += phrase+" "
    if result[-1] == ',':
        result[-1] = ""
    return str(result[:len(result)-1])

def addDotsInNumbers2(data):
    '''
        string with dot separated numbers, which inserted after every third digit from right to left
    '''
    result=''
    data=str(data).split(' ')
    for phrase in data:
        if phrase.isdigit() and len(phrase)>3:
            result += format(int(buf),',d')+" "
        else:
            result += phrase+" "
    return str(result[:len(result)-1])

class RightClickMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "Menu", parent)
        
        icon = QtGui.QIcon("ui/icons/options.png")
        action = QtGui.QAction(icon, "&Options", self)
        self.addAction(action)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.showOptionsWindow)

        icon = QtGui.QIcon("ui/icons/exit.png")
        action = QtGui.QAction(icon, "&Exit", self)
        self.addAction(action)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.exit)

        # options window
        self.__login = self.__password = self.__ip = ""
        self.__update_per = self.__koeff = 1
        if os.path.exists("NG-StatsViewer.cfg"):
            try:
                config = ConfigParser.RawConfigParser()
                config.read('NG-StatsViewer.cfg')
                self.__login = config.get('UserData', 'login')
                self.__password = config.get('UserData', 'password')
                self.__ip = config.get('UpdateData', 'ip')
                self.__update_per = int(config.get('UpdateData', 'update_time'))
                self.__koeff = int(config.get('UpdateData', 'koeff'))
            except ConfigParser.NoOptionError, ex:
                self.__login = self.__password = self.__ip = ""
                self.__update_per = self.__koeff = 1
        
        self.window = uic.loadUi("ui/options.ui")
        self.window.LoginEdit.setText(self.__login)
        self.window.PasswordEdit.setText(self.__password)
        self.window.IpLineEdit.setText(self.__ip)
        self.window.UpdateSpinBox.setValue(self.__update_per)
        self.window.KoeffSpinBox.setValue(self.__koeff)
        self.connect(self.window.CancelButton, QtCore.SIGNAL("clicked()"), self.closeOptionsWindow)
        self.connect(self.window.OkButton, QtCore.SIGNAL("clicked()"), self.saveOptionsWindow)

    def showOptionsWindow(self):
        self.window.show()

    def saveOptionsWindow(self):
        showDialog = False
        config = ConfigParser.RawConfigParser()
        
        config.add_section('UserData')
        if self.window.LoginEdit.text() != self.__login:
            showDialog = True
            config.set('UserData', 'login', self.window.LoginEdit.text())
        else:
            config.set('UserData', 'login', self.__login)
            
        if self.window.PasswordEdit.text() != self.__password:
            showDialog = True
            config.set('UserData', 'password', self.window.PasswordEdit.text())
        else:
            config.set('UserData', 'password', self.__password)
            
        config.add_section('UpdateData')
        if self.window.IpLineEdit.text() != self.__ip:
            showDialog = True
            config.set('UpdateData', 'ip', self.window.IpLineEdit.text())
        else:
            config.set('UpdateData', 'ip', self.__ip)
            
        if self.window.UpdateSpinBox.value() != self.__update_per:
            showDialog = True
            config.set('UpdateData', 'update_time', self.window.UpdateSpinBox.value())
        else:
            config.set('UpdateData', 'update_time', self.__update_per)
          
        if self.window.KoeffSpinBox.value() != self.__koeff:
            showDialog = True
            config.set('UpdateData', 'koeff', self.window.KoeffSpinBox.value())
        else:
            config.set('UpdateData', 'koeff', self.__koeff)    
            
        with open('NG-StatsViewer.cfg', 'wb') as configfile:
            config.write(configfile)
            
        if showDialog:
            QtGui.QMessageBox.information(None, "NG StatsViewer", "For using new preferences, please, restart this app...")
        self.window.hide()

    def closeOptionsWindow(self):
        self.window.LoginEdit.setText(self.__login)
        self.window.PasswordEdit.setText(self.__password)
        self.window.IpLineEdit.setText(self.__ip)
        self.window.UpdateSpinBox.setValue(self.__update_per)
        self.window.KoeffSpinBox.setValue(self.__koeff)
        self.window.hide()

    def exit(self):
        QtCore.QCoreApplication.instance().quit()

class WorkThread(QtCore.QThread):
    def __init__(self, login, password, ip, koeff, interval = 5):
        QtCore.QThread.__init__(self)
        self.__parser = HtmlParser.StatisticsParser(login, password, ip)
        self.__interval = interval
        self.__koeff = koeff
        self.__previos_data = [0, 0, 0, 0, '0 kbps', '0 kbps']
 
    def run(self):
        while(True):
            real_download = real_upload = "0"
            th_data, errors = self.__parser.getNewStats()
            if self.__previos_data[0] != 0:
                real_upload = "%s kbps" % int((((abs(th_data[0] - self.__previos_data[0]) / 1024.) / self.__interval) / 2.5) * self.__koeff )
            if self.__previos_data[1] != 0:
                real_download = "%s kbps" % int(((abs(th_data[1] - self.__previos_data[1]) / 1024.) / self.__interval) * self.__koeff * 20)
            self.__previos_data = th_data
            self.emit(QtCore.SIGNAL('add(QString)'), str(th_data + [real_download, real_upload]))
            time.sleep(self.__interval - 0.25)

class StatsWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.thread = None
        self.window = uic.loadUi("ui/stats.ui")
        self.window.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.init_thread()
    
    def get_data(self, data_str):
        data = eval(str(data_str))
        self.window.TxBs.setText("Tx : %s kbps" % addDotsInNumbers2(int(data[2]/1024.)))
        self.window.RxBs.setText("Rx : %s kbps" % addDotsInNumbers2(int(data[3]/1024.)))
        self.window.Real.setText("Real download: %s" % addDotsInNumbers(data[6]))
        self.window.Real2.setText("Real upload: %s" % addDotsInNumbers(data[7]))
    
    def init_thread(self):
        if os.path.exists("NG-StatsViewer.cfg"):
            # read config
            login = password = ip = ""
            update_per = koeff = 1
            try:
                config = ConfigParser.RawConfigParser()
                config.read('NG-StatsViewer.cfg')
                login = config.get('UserData', 'login')
                password = config.get('UserData', 'password')
                ip = config.get('UpdateData', 'ip')
                update_per = int(config.get('UpdateData', 'update_time'))
                koeff = int(config.get('UpdateData', 'koeff'))
            except ConfigParser.NoOptionError, ex:
                login = password = ip = ""
                update_per = koeff = 1
            # create thread and catching signal from him
            self.thread = WorkThread(login, password, ip, koeff, update_per)
            self.connect(self.thread, QtCore.SIGNAL("add(QString)"), self.get_data)
            self.thread.start()
            self.window.show()

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QtGui.QIcon("ui/icons/tray.png"))
        # menu in tray
        self.right_menu = RightClickMenu()
        self.setContextMenu(self.right_menu)
        # additional windows with stats
        self.stats_window = None
    
    def app_init(self):
        self.showMessage("NG StatsViewer", "Please, enter user/password/ip in [Options] section")    
    
    def welcome(self):
        self.showMessage("NG StatsViewer", "Succesfully started...")
    
    def show(self):
        QtGui.QSystemTrayIcon.show(self)
        if not os.path.exists("NG-StatsViewer.cfg"):
            QtCore.QTimer.singleShot(1, self.app_init)
        else:
            self.stats_window = StatsWindow()
            QtCore.QTimer.singleShot(1, self.welcome)

def main():
    app = QtGui.QApplication([])
    tray = SystemTrayIcon()
    tray.show()
    app.exec_()

if __name__ == '__main__':
    main()
