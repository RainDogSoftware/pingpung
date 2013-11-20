import sys
from PyQt4 import QtGui, QtCore
from lib import pping
import time
from itertools import count

class PingThread(QtCore.QThread):

    def __init__(self, ip, pingCount, interval, tabID):
        self.ip = ip
        self.pingCount = pingCount
        self.interval = interval
        self.tabID = tabID
        super(PingThread, self).__init__()
        
    def run(self):
        count = 0
        # Needs improvement
        while (count < self.pingCount) or (self.pingCount == 0):
            count += 1
            self.result = pping.do_one(self.ip, 1000, count, 55)
            self.result["tabID"] = self.tabID
            #print(self.result)
            self.emit(QtCore.SIGNAL('complete'), self.result)
            time.sleep(self.interval)

class PingPungGui(QtGui.QWidget):
    
    def showResult(self, result):
        #print(result)
        tabObject = self.tabObjects[result["tabID"]]
        if result["Success"]:
            tabObject.stats["Success Count"] += 1
            output = "%s %i - %s - from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'], result['Message'], result['Responder'], result['Delay'])
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
        self.connect(sender, QtCore.SIGNAL('complete'), self.showResult)
    
    def __init__(self):
        super(PingPungGui, self).__init__()
        self.counterIter = count()
        self.tabObjects = {}
        self.initUI()
        
    def initTabs(self):
        # returns layout containing tab bar
        self.tabWidget = QtGui.QTabWidget()
        self.newTab("Initial Tab")
        
    def newTab(self, *args, name = "New Tab"):
        index = self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), name)
        self.tabWidget.setCurrentIndex(index)
        
    def removeTab(self, tabID):
        if tabID != 0:
            self.tabWidget.removeTab(tabID)
        
    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PingPung')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        
        self.initTabs()
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.tabWidget)
        self.setLayout(mainLayout)
    
        self.show()    
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Second Tab")
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Third Tab")
        
    ############# Main GUI Building function ###################
    def populateTab(self, tabObject):
        tabID = next(self.counterIter)
        self.tabObjects[tabID] = tabObject
        self.threads = []  
        
        def clearStats():
            return {"Success Count":0,
                    "Fail Count":0}
                                  
        def startPing(*args):
            ip = tabObject.ipBox.text()
            pingCount = int(tabObject.pingCountBox.text())
            interval = int(tabObject.intervalBox.text())
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), ip)
            
            outputText = "Starting ping to %s. \n Interval: %i seconds \n Count: %i \n" % (ip, interval, pingCount)
            tabObject.outputBox.insertPlainText(outputText) 
        
            tabObject.thread = PingThread(ip, pingCount, interval, tabID)
            self.connect_slots(tabObject.thread)
            tabObject.thread.start()
            tabObject.startPingButton.setEnabled(False)
            tabObject.stopPingButton.setEnabled(True)


        def stopPing(*args):
            tabObject.outputBox.insertPlainText("Stopping!\n")
            tabObject.thread.terminate()
            tabObject.stats = clearStats()
            tabObject.startPingButton.setEnabled(True)
            tabObject.stopPingButton.setEnabled(False)
            
        def clearLog(*args):
            tabObject.outputBox.clear()
            
        def saveLog(*args):
            file_types = "Plain Text (*.txt);;Plain Text (*.log)"
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.', file_types)
            fname = open(filename, 'w')
            fname.write(tabObject.outputBox.toPlainText())
            fname.close() 
            
        tabObject.stats = clearStats()
        
        tabLayout = QtGui.QGridLayout()
        
        # New Tab
        tabObject.newTabButton = QtGui.QPushButton("New Tab", self)
        tabObject.newTabButton.clicked.connect(self.newTab)
        tabLayout.addWidget(tabObject.newTabButton,0,1)
        
        # Close tab
        tabObject.closeTabButton = QtGui.QPushButton("Close Tab", self)
        tabObject.closeTabButton.clicked.connect(lambda: self.removeTab(self.tabWidget.currentIndex()))
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
        
        # Start Button
        tabObject.startPingButton = QtGui.QPushButton('Start', self)
        tabObject.startPingButton.clicked.connect(startPing)
        tabLayout.addWidget(tabObject.startPingButton,3,11)
        
        # Stop Button
        tabObject.stopPingButton = QtGui.QPushButton('Stop', self)
        tabObject.stopPingButton.clicked.connect(stopPing)
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
        tabObject.clearLogButton.clicked.connect(clearLog)
        tabLayout.addWidget(tabObject.clearLogButton,19,11)        
        
        # Save Log button
        tabObject.saveLogButton = QtGui.QPushButton('Save Log', self)
        tabObject.saveLogButton.clicked.connect(saveLog)
        tabLayout.addWidget(tabObject.saveLogButton,19,12)
        
        tabObject.setLayout(tabLayout)
        
        return tabObject
          
def main():
    app = QtGui.QApplication(sys.argv)
    ex = PingPungGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 