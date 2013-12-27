import sys
from PyQt4 import QtGui, QtCore
from lib import pping
import time
import ipaddress
from itertools import count

class PingThread(QtCore.QThread):

    def __init__(self, ip, pingCount, interval, packet_size, tabID):
        self.ip = ip
        self.pingCount = pingCount
        self.interval = interval
        self.packet_size = packet_size
        self.tabID = tabID
        super(PingThread, self).__init__()
        
    def run(self):
        count = 0
        while (count < self.pingCount) or (self.pingCount == 0):
            count += 1
            try:
                self.result = pping.ping(self.ip, 1000, count, self.packet_size)
            except pping.SocketError:
                self.emit(QtCore.SIGNAL('error'), "Socket error.  Verify that program is running as root/admin.")
                break
            except pping.AddressError:
                self.emit(QtCore.SIGNAL('error'), "Address error.  Bad IP address or domain name.")
                break
            else:
                self.result["tabID"] = self.tabID
                self.emit(QtCore.SIGNAL('complete'), self.result)
                time.sleep(self.interval)
                

class PingPungGui(QtGui.QWidget):
    
    def show_result(self, result):
        tabObject = self.tabObjects[result["tabID"]]
        if result["Success"]:
            tabObject.stats["Success Count"] += 1
            output = "%s %i - %s - %i bytes from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'], result['Message'], result["PacketSize"], result['Responder'], result['Delay'])
        else:
            tabObject.stats["Fail Count"] += 1
            output = "%s %i - %s \n" % (result["Timestamp"], result['SeqNumber'], result['Message'])
                
        outputBox = tabObject.outputBox
        outputBox.moveCursor(QtGui.QTextCursor.End)
        outputBox.insertPlainText(output)
        outputBox.moveCursor(QtGui.QTextCursor.End)
        
        summaryBox = tabObject.summaryBox
        numGood = tabObject.stats["Success Count"]
        numBad = tabObject.stats["Fail Count"]
        percent = (numGood /(numBad + numGood)) * 100
        summaryBox.setPlainText("Success Count:    %i \nFail Count:       %i \nPercent Success:  %i" % (numGood, numBad,percent))
    
    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self.show_error)
    
    def __init__(self):
        super(PingPungGui, self).__init__()
        self.counterIter = count()
        self.tabObjects = {}
        self.init_ui()
        
    def init_tabs(self):
        # returns layout containing tab bar
        self.tabWidget = QtGui.QTabWidget()
        self.new_tab("Initial Tab")
        
    def new_tab(self, *args, name = "New Tab"):
        index = self.tabWidget.addTab(self.populate_tab(QtGui.QWidget()), name)
        self.tabWidget.setCurrentIndex(index)
        
    def remove_tab(self, tabID):
        if tabID != 0:
            self.tabWidget.removeTab(tabID)
        
    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PingPung')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        
        self.init_tabs()
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.tabWidget)
        self.setLayout(mainLayout)
    
        self.show()    
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Second Tab")
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Third Tab")
        
    def show_error(self, message):
            QtGui.QMessageBox.about(self, "OH TEH NOES!", message)
    
        
    ############# Main GUI Building function ###################
    def populate_tab(self, tabObject):
        tabID = next(self.counterIter)
        self.tabObjects[tabID] = tabObject
        self.threads = []  
        
        def clear_stats():
            return {"Success Count":0,
                    "Fail Count":0}
                                  
        def start_ping(*args):
            ip = tabObject.ipBox.text()
            pingCount = int(tabObject.pingCountBox.text())
            interval = int(tabObject.intervalBox.text())
            packet_size = int(tabObject.packet_size_box.text())
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), ip)
            
            outputText = "Starting ping to %s. \n Interval: %i seconds \n Count: %i \n" % (ip, interval, pingCount)
            tabObject.outputBox.insertPlainText(outputText) 
        
            tabObject.thread = PingThread(ip, pingCount, interval, packet_size, tabID)
            self.connect_slots(tabObject.thread)
            
            tabObject.thread.start()
            tabObject.startPingButton.setEnabled(False)
            tabObject.stopPingButton.setEnabled(True)


        def stop_ping(*args):
            tabObject.outputBox.insertPlainText("Stopping!\n")
            tabObject.thread.terminate()
            tabObject.stats = clear_stats()
            tabObject.startPingButton.setEnabled(True)
            tabObject.stopPingButton.setEnabled(False)
            
        def clear_log(*args):
            tabObject.outputBox.clear()
            
        def save_log(*args):
            file_types = "Plain Text (*.txt);;Plain Text (*.log)"
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.', file_types)
            try:
                fname = open(filename, 'w')
                fname.write(tabObject.outputBox.toPlainText())
                fname.close() 
                raise Exception
            except: #Yeah, I know, blanket exceptions are not a great idea.  This won't stay this way forever.  
                self.show_error("Unable to save log file")
            
        tabObject.stats = clear_stats()
        
        tabLayout = QtGui.QGridLayout()
        
        # New Tab
        tabObject.newTabButton = QtGui.QPushButton("New Tab", self)
        tabObject.newTabButton.clicked.connect(self.new_tab)
        tabLayout.addWidget(tabObject.newTabButton,0,1)
        
        # Close tab
        tabObject.closeTabButton = QtGui.QPushButton("Close Tab", self)
        tabObject.closeTabButton.clicked.connect(lambda: self.remove_tab(self.tabWidget.currentIndex()))
        tabLayout.addWidget(tabObject.closeTabButton,0,2)
        
        # Spacing hacks.  TODO:  learn better QT layout =P
        tabObject.ipLabel = QtGui.QLabel("")
        tabLayout.addWidget(tabObject.ipLabel,1,1)
        for i in range(4,11):
          tabObject.ipLabel = QtGui.QLabel("              ")
          tabLayout.addWidget(tabObject.ipLabel,0,i)
        
        # Ip address box
        tabObject.ipLabel = QtGui.QLabel("Remote IP Address")
        tabLayout.addWidget(tabObject.ipLabel,2,1)
        tabObject.ipBox = QtGui.QLineEdit("8.8.8.8")
        tabLayout.addWidget(tabObject.ipBox,3,1)
        
        # Ping count box
        tabObject.pingCountLabel = QtGui.QLabel("Count (0=infinite)")
        tabLayout.addWidget(tabObject.pingCountLabel,2,2)
        tabObject.pingCountBox = QtGui.QLineEdit("0")
        tabLayout.addWidget(tabObject.pingCountBox,3,2)
        
        # Interval Box
        tabObject.intervalLabel = QtGui.QLabel("Interval (seconds)")
        tabLayout.addWidget(tabObject.intervalLabel,2,3)
        tabObject.intervalBox = QtGui.QLineEdit("1")
        tabLayout.addWidget(tabObject.intervalBox, 3,3)
        
        # Packet Size
        tabObject.packet_size_label = QtGui.QLabel("Packet Size (bytes)")
        tabLayout.addWidget(tabObject.packet_size_label,2,4)
        tabObject.packet_size_box = QtGui.QLineEdit("64")
        tabLayout.addWidget(tabObject.packet_size_box, 3,4)
        
        # Start Button
        tabObject.startPingButton = QtGui.QPushButton('Start', self)
        tabObject.startPingButton.clicked.connect(start_ping)
        tabLayout.addWidget(tabObject.startPingButton,3,11)
        
        # Stop Button
        tabObject.stopPingButton = QtGui.QPushButton('Stop', self)
        tabObject.stopPingButton.clicked.connect(stop_ping)
        tabObject.stopPingButton.setEnabled(False)
        tabLayout.addWidget(tabObject.stopPingButton,3,12)
        
        # Output Box
        tabObject.outputBox = QtGui.QPlainTextEdit()
        tabObject.outputBox.insertPlainText("Enter an IP address above and click Start. \n")
        tabObject.outputBox.setReadOnly(True)
        tabLayout.addWidget(tabObject.outputBox,4,1,16,10)
        
        # Summary Box
        tabObject.summaryBox = QtGui.QPlainTextEdit()
        tabLayout.addWidget(tabObject.summaryBox,4,11,15,8)
        
        # Clear Log button
        tabObject.clearLogButton = QtGui.QPushButton('Clear Log', self)
        tabObject.clearLogButton.clicked.connect(clear_log)
        tabLayout.addWidget(tabObject.clearLogButton,19,11)        
        
        # Save Log button
        tabObject.saveLogButton = QtGui.QPushButton('Save Log', self)
        tabObject.saveLogButton.clicked.connect(save_log)
        tabLayout.addWidget(tabObject.saveLogButton,19,12)
        
        tabObject.setLayout(tabLayout)
        
        return tabObject
          
def main():
    app = QtGui.QApplication(sys.argv)
    ex = PingPungGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 