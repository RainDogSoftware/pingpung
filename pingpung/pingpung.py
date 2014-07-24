import sys
import time
from itertools import count

from PyQt4 import QtGui, QtCore
from lib import pping, audio


class PingThread(QtCore.QThread):

    def __init__(self, ip, ping_count, interval, packet_size, tab_id):
        self.ip = ip
        self.ping_count = ping_count
        self.interval = interval
        self.packet_size = packet_size
        self.tab_id = tab_id
        super(PingThread, self).__init__()
        
    def run(self):
        count = 0
        while (count < self.ping_count) or (self.ping_count == 0):
            count += 1
            # Cannot accept sequence number > 65535.  This resets seq number but does not affect stats totals
            if count > 65535:
                count = 0
            try:
                self.result = pping.ping(self.ip, 1000, count, self.packet_size)
            except pping.SocketError:
                self.emit(QtCore.SIGNAL('error'), "Socket error.  Verify that program is running as root/admin.")
                break
            except pping.AddressError:
                self.emit(QtCore.SIGNAL('error'), "Address error.  Bad IP address or domain name.")
                break
            else:
                self.result["tabID"] = self.tab_id
                self.emit(QtCore.SIGNAL('complete'), self.result)
                time.sleep(self.interval)
                

class PingPungGui(QtGui.QMainWindow):

    def __init__(self):
        super(PingPungGui, self).__init__()
        self.counter_iter = count()
        self.tab_objects = {}
        self.init_ui()

    def show_result(self, result):
        tab_object = self.tab_objects[result["tabID"]]

        if result["Success"]:
            if tab_object.audio_checkBox.checkState() == 2 and tab_object.alert_success_button.isChecked():
                audio.play("pingpung/data/woohoo.wav")

            tab_object.stats["Success Count"] += 1
            output = "%s %i - %s - %i bytes from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'], result['Message'], result["PacketSize"], result['Responder'], result['Delay'])
        else:
            if tab_object.audio_checkBox.checkState() == 2 and tab_object.alert_failure_button.isChecked():
                audio.play("pingpung/data/doh.wav")

            tab_object.stats["Fail Count"] += 1
            output = "%s %i - %s \n" % (result["Timestamp"], result['SeqNumber'], result['Message'])
                
        output_box = tab_object.output_box
        output_box.moveCursor(QtGui.QTextCursor.End)
        output_box.insertPlainText(output)
        output_box.moveCursor(QtGui.QTextCursor.End)
        
        summary_box = tab_object.summary_box
        num_good = tab_object.stats["Success Count"]
        num_bad = tab_object.stats["Fail Count"]
        percent = (num_good /(num_bad + num_good)) * 100
        summary_box.setPlainText("Success Count:    %i \nFail Count:       %i \nPercent Success:  %i" % (num_good, num_bad,percent))
    
    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self.show_error)
        
    def init_tabs(self):
        # returns layout containing tab bar
        self.tab_widget = QtGui.QTabWidget()


        plus_button = QtGui.QPushButton("+", self)
        plus_button.clicked.connect(self.new_tab)
        self.tab_widget.setCornerWidget(plus_button)

        self.new_tab("Initial Tab")
        
    def new_tab(self, somebool, name="New Tab"):
        this_tab = self.populate_tab(QtGui.QWidget())
        index = self.tab_widget.addTab(this_tab, name)
        self.tab_widget.setCurrentIndex(index)
        
    def remove_tab(self, tab_id):
        if tab_id != 0:
            self.tab_widget.removeTab(tab_id)
        
    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PingPung')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        
        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')

        exit_action.triggered.connect(QtGui.qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)
        
        
        self.init_tabs()
        #mainLayout = QtGui.QGridLayout()
        #mainLayout.addWidget(self.tabWidget)
        #self.main_widget = QtGui.QWidget
        self.setCentralWidget(self.tab_widget)
    
        self.show()    
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Second Tab")
        #self.tabWidget.addTab(self.populateTab(QtGui.QWidget()), "Third Tab")
        
    def show_error(self, message):
            QtGui.QMessageBox.about(self, "OH TEH NOES!", message)
    
        
    ############# Main GUI Building function ###################
    def populate_tab(self, tab_object):
        tab_id = next(self.counter_iter)
        self.tab_objects[tab_id] = tab_object
        self.threads = []  
        
        def clear_stats():
            return {"Success Count":0,
                    "Fail Count":0}
                                  
        def start_ping(*args):
            ip = tab_object.ip_box.text().strip()
            ping_count = int(tab_object.ping_count_box.text())
            interval = int(tab_object.interval_box.text())
            packet_size = int(tab_object.packet_size_box.text())
            if len(tab_object.session_label_box.text()) >= 1:
                label_text = " ".join([tab_object.session_label_box.text(),"-", ip])
            else:
                label_text = ip
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), label_text)
            
            output_text = "Starting ping to %s. \n Interval: %i seconds \n Count: %i \n" % (ip, interval, ping_count)
            tab_object.output_box.insertPlainText(output_text)
        
            tab_object.thread = PingThread(ip, ping_count, interval, packet_size, tab_id)
            self.connect_slots(tab_object.thread)
            
            tab_object.thread.start()
            #TODO: Do this with signals instead of function calls, make it a single toggle, errors should toggle off
            tab_object.start_ping_button.setEnabled(False)
            tab_object.stop_ping_button.setEnabled(True)


        def stop_ping(*args):
            tab_object.output_box.insertPlainText("Stopping!\n")
            tab_object.thread.terminate()
            tab_object.stats = clear_stats()
            tab_object.start_ping_button.setEnabled(True)
            tab_object.stop_ping_button.setEnabled(False)
            
        def clear_log(*args):
            tab_object.output_box.clear()
            
        def save_log(*args):
            file_types = "Plain Text (*.txt);;Plain Text (*.log)"
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.', file_types)
            try:
                fname = open(filename, 'w')
                fname.write(tab_object.summary_box.toPlainText() + "\n\n")
                fname.write(tab_object.output_box.toPlainText())
                fname.close() 
            except: #Yeah, I know, blanket exceptions are not a great idea.  This won't stay this way forever.  
                self.show_error("Unable to save log file")
                raise
            
        tab_object.stats = clear_stats()
        
        tab_layout = QtGui.QGridLayout()
        
        # New Tab
        tab_object.new_tab_button = QtGui.QPushButton("New Tab", self)
        tab_object.new_tab_button.clicked.connect(self.new_tab)
        tab_layout.addWidget(tab_object.new_tab_button,0,1)
        
        # Close tab
        tab_object.close_tab_button = QtGui.QPushButton("Close Tab", self)
        tab_object.close_tab_button.clicked.connect(lambda: self.remove_tab(self.tab_widget.currentIndex()))
        tab_layout.addWidget(tab_object.close_tab_button,0,2)
        
        # Spacing hacks.  TODO:  learn better QT layout =P
        tab_object.spacer = QtGui.QLabel("")
        tab_layout.addWidget(tab_object.spacer,1,1)
        for i in range(4,11):
          tab_object.spacer = QtGui.QLabel("              ")
          tab_layout.addWidget(tab_object.spacer,0,i)
        
        # Ip address box
        tab_object.ip_label = QtGui.QLabel("Remote IP Address")
        tab_layout.addWidget(tab_object.ip_label,2,1)
        tab_object.ip_box = QtGui.QLineEdit("127.0.0.1")
        tab_object.ip_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.ip_box,3,1)
        
        # Session Label Box
        tab_object.session_label = QtGui.QLabel("Session Label (Optional)")
        tab_layout.addWidget(tab_object.session_label,2,2)
        tab_object.session_label_box = QtGui.QLineEdit("")
        tab_layout.addWidget(tab_object.session_label_box,3,2)
        
        # Ping count box
        tab_object.ping_count_label = QtGui.QLabel("Count (0=infinite)")
        tab_layout.addWidget(tab_object.ping_count_label,2,3)
        tab_object.ping_count_box = QtGui.QLineEdit("0")
        tab_layout.addWidget(tab_object.ping_count_box,3,3)
        
        # Interval Box
        tab_object.interval_label = QtGui.QLabel("Interval (seconds)")
        tab_layout.addWidget(tab_object.interval_label,2,4)
        tab_object.interval_box = QtGui.QLineEdit("1")
        tab_layout.addWidget(tab_object.interval_box, 3,4)
        
        # Packet Size
        tab_object.packet_size_label = QtGui.QLabel("Packet Size (bytes)")
        tab_layout.addWidget(tab_object.packet_size_label,2,5)
        tab_object.packet_size_box = QtGui.QLineEdit("64")
        tab_layout.addWidget(tab_object.packet_size_box, 3,5)
        
        # Start Button
        tab_object.start_ping_button = QtGui.QPushButton('Start', self)
        tab_object.start_ping_button.clicked.connect(start_ping)
        tab_layout.addWidget(tab_object.start_ping_button,3,11)
        
        # Stop Button
        tab_object.stop_ping_button = QtGui.QPushButton('Stop', self)
        tab_object.stop_ping_button.clicked.connect(stop_ping)
        tab_object.stop_ping_button.setEnabled(False)
        tab_layout.addWidget(tab_object.stop_ping_button,3,12)
        
        # Output Box
        tab_object.output_box = QtGui.QPlainTextEdit()
        #tabObject.output_box.insertPlainText()
        tab_object.output_box.setReadOnly(True)
        tab_layout.addWidget(tab_object.output_box,4,1,16,10)
        
        # Summary Box
        tab_object.summary_box = QtGui.QPlainTextEdit()
        tab_layout.addWidget(tab_object.summary_box,4,11,11,2)
        
        # Clear Log button
        tab_object.clear_log_button = QtGui.QPushButton('Clear Log', self)
        tab_object.clear_log_button.clicked.connect(clear_log)
        tab_layout.addWidget(tab_object.clear_log_button,19,11)
        
        # Save Log button
        tab_object.save_log_button = QtGui.QPushButton('Save Log', self)
        tab_object.save_log_button.clicked.connect(save_log)
        tab_layout.addWidget(tab_object.save_log_button,19,12)

        # Audio options
        tab_object.audio_option_box = QtGui.QGroupBox("Audio Options")
        tab_object.audio_checkBox = QtGui.QCheckBox("Enable audio alerts")
        tab_object.alert_success_button = QtGui.QRadioButton("Alert on Success")
        tab_object.alert_failure_button = QtGui.QRadioButton("Alert on Failure")
        tab_object.alert_success_button.setChecked(True)
        tab_object.audio_checkBox.setChecked(True)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tab_object.audio_checkBox)
        vbox.addWidget(tab_object.alert_success_button)
        vbox.addWidget(tab_object.alert_failure_button)

        vbox.addStretch(1)
        tab_object.audio_option_box.setLayout(vbox)
        tab_layout.addWidget(tab_object.audio_option_box, 15,11,4,2)

        tab_object.setLayout(tab_layout)
        
        return tab_object
          
def main():
    app = QtGui.QApplication(sys.argv)
    ex = PingPungGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 