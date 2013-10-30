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
            result = pping.do_one(self.ip, 1000, count, 55)
            result["tabID"] = self.tabID
            self.emit(QtCore.SIGNAL('complete'), result)
            time.sleep(self.interval)
            

class PingPungGui(QtGui.QWidget):
    
    def showResult(self, result):
        print(result)
        tabObject = self.tabObjects[result["tabID"]]
        if result["Success"] == True:
            tabObject.stats["Success Count"] += 1
            output = "%s %i - %s - from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'], result['Message'], result['Responder'], result['Delay'])
        else:
            tabObject.stats["Fail Count"] += 1
            output = "%s %i - %s \n" % (result["Timestamp"], result['SeqNumber'], result['Message'])
                
        
        
        outputBox = tabObject.outputBox
        outputBox.moveCursor(QtGui.QTextCursor.End)
        outputBox.insertPlainText("TABID %i - " % result["tabID"] + output)
        
        
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
        
    def newTab(self, name="New Tab"):
        self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), name)
        
    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PingPung')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        
        self.initTabs()
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.tabWidget)
        self.setLayout(mainLayout)
    
        self.show()    
        self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Second Tab")
        self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Third Tab")
        
    ############# Main GUI Building function ###################
    def populateTab(self, tabObject):
        tabID = next(self.counterIter)
        self.tabObjects[tabID] = tabObject
                
        def clearStats():
            return {"Success Count":0,
                    "Fail Count":0}
                                  
        def startPing(*args):
            ip = tabObject.ipBox.text()
            pingCount = int(tabObject.pingCountBox.text())
            interval = int(tabObject.intervalBox.text())
        
            outputText = "Starting ping to %s. \n Interval: %i seconds \n Count: %i \n" % (ip, interval, pingCount)
            tabObject.outputBox.insertPlainText(outputText) 
        
            tabObject.thread = PingThread(ip, pingCount, interval, tabID)
            self.connect_slots(tabObject.thread)
            tabObject.thread.start()

        def stopPing(*args):
            tabObject.outputBox.insertPlainText("Stopping!\n")
            tabObject.thread.terminate()
            tabObject.stats = clearStats()
            
        tabObject.stats = clearStats()
        
        tabLayout = QtGui.QGridLayout()
        #tabLayout.setSpacing(10)
        
        # Ip address box
        tabObject.ipLabel = QtGui.QLabel("Remote IP Address")
        tabLayout.addWidget(tabObject.ipLabel,1,1)
        tabObject.ipBox = QtGui.QLineEdit("8.8.8.8")
        tabLayout.addWidget(tabObject.ipBox,2,1)
        
        # Ping count box
        tabObject.pingCountLabel = QtGui.QLabel("Count (0=infinite)")
        tabLayout.addWidget(tabObject.pingCountLabel,1,2)
        tabObject.pingCountBox = QtGui.QLineEdit("0")
        tabLayout.addWidget(tabObject.pingCountBox,2,2)
        
        # Interval Box
        tabObject.intervalLabel = QtGui.QLabel("Interval (seconds)")
        tabLayout.addWidget(tabObject.intervalLabel,1,3)
        tabObject.intervalBox = QtGui.QLineEdit("1")
        tabLayout.addWidget(tabObject.intervalBox, 2,3)
        
        # Start Button
        tabObject.button = QtGui.QPushButton('Start', self)
        tabObject.button.clicked.connect(startPing)
        tabLayout.addWidget(tabObject.button,2,4)
        
        # Stop Button
        tabObject.button = QtGui.QPushButton('Stop', self)
        tabObject.button.clicked.connect(stopPing)
        tabLayout.addWidget(tabObject.button,2,5)
        
        # Output Box
        tabObject.outputBox = QtGui.QPlainTextEdit()
        tabObject.outputBox.insertPlainText("Enter an IP address above and click Start.  \
                                       A ping count of zero means infinite.\n")
        tabObject.outputBox.setReadOnly(True)
                                       
        # Summary Box
        tabObject.summaryBox = QtGui.QPlainTextEdit()
        tabLayout.addWidget(tabObject.summaryBox,3,4,6,2)
        
        tabLayout.addWidget(tabObject.outputBox,3,1,6,3)
        tabObject.setLayout(tabLayout)
        
        return tabObject
          
def main():
    app = QtGui.QApplication(sys.argv)
    ex = PingPungGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 