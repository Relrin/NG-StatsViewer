#! /usr/bin/env python
import os
import time
import ConfigParser
import HtmlParser
from PyQt4 import QtGui, QtCore, uic

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
        self.__update_per = 1
        if os.path.exists("NG-StatsViewer.cfg"):
            try:
                config = ConfigParser.RawConfigParser()
                config.read('NG-StatsViewer.cfg')
                self.__login = config.get('UserData', 'login')
                self.__password = config.get('UserData', 'password')
                self.__ip = config.get('UpdateData', 'ip')
                self.__update_per = int(config.get('UpdateData', 'update_time'))
            except ConfigParser.NoOptionError, ex:
                self.__login = self.__password = self.__ip = ""
                self.__update_per = 1
        
        self.window = uic.loadUi("ui/options.ui")
        self.window.LoginEdit.setText(self.__login)
        self.window.PasswordEdit.setText(self.__password)
        self.window.IpLineEdit.setText(self.__ip)
        self.window.UpdateSpinBox.setValue(self.__update_per)
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
        self.window.hide()

    def exit(self):
        QtCore.QCoreApplication.instance().quit()

class WorkThread(QtCore.QThread):
    def __init__(self, login, password, ip, interval = 5):
        QtCore.QThread.__init__(self)
        self.__parser = HtmlParser.StatisticsParser(login, password, ip)
        self.__interval = interval
 
    def run(self):
        while(True):
            th_data = str(self.__parser.getNewStats())
            self.emit(QtCore.SIGNAL('add(QString)'), th_data)
            time.sleep(self.__interval - 0.25)

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QtGui.QIcon("ui/icons/tray.png"))
        # menu in tray
        self.right_menu = RightClickMenu()
        self.setContextMenu(self.right_menu)
    
        self.activated.connect(self.click_trap)
        
        self.string = "Getting data from modem..."
        self.thread = None

    def click_trap(self, value):
        # left click!
        if value == self.Trigger: 
            QtCore.QTimer.singleShot(1, self.app_stats)
    
    def get_data(self, data_str):
        data = eval(str(data_str))
        new_string = "%-18s  %+8s %+10s\n" % (" ", "Upload", "Download")
        new_string += "%-10s  %12s %+12s\n" % (data[0][0][0], data[0][0][2][0], data[0][0][3][0])
        new_string += "%-10s  %10s %+12s\n" % (data[0][1][0], data[0][1][2][0], data[0][1][3][0])
        new_string += "%-10s  %10s %+12s\n" % (data[0][2][0], data[0][2][2][0], data[0][2][3][0])
        self.string = new_string
    
    def app_init(self):
        self.showMessage("NG StatsViewer", "Please, enter user/password/ip in [Options] section")    
    
    def app_stats(self):
        self.showMessage("NG StatsViewer", self.string)  
    
    def welcome(self):
        self.showMessage("NG StatsViewer", "Succesfully started...")
    
    def show(self):
        QtGui.QSystemTrayIcon.show(self)
        if not os.path.exists("NG-StatsViewer.cfg"):
            QtCore.QTimer.singleShot(1, self.app_init)
        else:
            QtCore.QTimer.singleShot(1, self.welcome)
            # read config
            login = password = ip = ""
            update_per = 1
            try:
                config = ConfigParser.RawConfigParser()
                config.read('NG-StatsViewer.cfg')
                login = config.get('UserData', 'login')
                password = config.get('UserData', 'password')
                ip = config.get('UpdateData', 'ip')
                update_per = int(config.get('UpdateData', 'update_time'))
            except ConfigParser.NoOptionError, ex:
                login = password = ip = ""
                update_per = 1
            # create thread and catching signal from him
            self.thread = WorkThread(login, password, ip, update_per)
            self.connect(self.thread, QtCore.SIGNAL("add(QString)"), self.get_data)
            self.thread.start()

def main():
    app = QtGui.QApplication([])
    tray = SystemTrayIcon()
    tray.show()
    app.exec_()

if __name__ == '__main__':
    main()