import sys
import time
import os.path
from itertools import count

from PyQt4 import QtGui, QtCore
from pplib import pping, audio


class PingThread(QtCore.QThread):
    """ A QThread subclass for running the pings.

    Args:
        ip - the IP address or domain name of the target to ping
        ping_count - how many times to run this ping before the thread terminates
        interval - the time to sleep between pings
        packet_size - number of bytes to send per ping
        tab_id - the ID number of the tab which started the thread.
            This is used to match ping response to the correct tab.

    The results of a ping are sent via Qt Signals.  Errors initializing the ping are sent with a string describing the
    error, while the complete ping signal (including timeouts and such) includes a dictionary with the detailed results,
    as provided by the ping library in use.
    """

    def __init__(self, ip, ping_count, interval, packet_size, tab_id):
        self.ip = ip
        self.ping_count = ping_count
        self.interval = interval
        self.packet_size = packet_size
        self.tab_id = tab_id
        super(PingThread, self).__init__()

    def run(self):
        pcount = 0
        while (pcount < self.ping_count) or (self.ping_count == 0):
            pcount += 1
            # Cannot accept sequence number > 65535.  This resets seq number but does not affect stats totals
            if pcount > 65535:
                pcount = 0
            try:
                self.result = pping.ping(self.ip, 1000, pcount, self.packet_size)
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
        """
        Reads the result dict as sent by signal handler and updates log as well as the summary stats.
        """
        tab_object = self.tab_objects[result["tabID"]]
        tab_index = self.tab_widget.indexOf(tab_object)

        if result["Success"]:
            self.tab_widget.tabBar().setTabTextColor(tab_index, QtGui.QColor(0, 128, 0))
            if tab_object.audio_checkBox.checkState() == 2 and tab_object.alert_success_button.isChecked():
                audio.play("data/woohoo.wav")

            tab_object.stats["Success Count"] += 1
            output = "%s %i - %s - %i bytes from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'],
                                                                       result['Message'], result["PacketSize"],
                                                                       result['Responder'], result['Delay'])
        else:
            self.tab_widget.tabBar().setTabTextColor(tab_index, QtGui.QColor(128, 0, 0))
            if tab_object.audio_checkBox.checkState() == 2 and tab_object.alert_failure_button.isChecked():
                audio.play("data/doh.wav")

            tab_object.stats["Fail Count"] += 1
            output = "%s %i - %s \n" % (result["Timestamp"], result['SeqNumber'], result['Message'])

        output_box = tab_object.output_box
        output_box.moveCursor(QtGui.QTextCursor.End)
        output_box.insertPlainText(output)
        output_box.moveCursor(QtGui.QTextCursor.End)

        summary_box = tab_object.summary_box
        num_good = tab_object.stats["Success Count"]
        num_bad = tab_object.stats["Fail Count"]
        percent = (num_good / (num_bad + num_good)) * 100
        summary_box.setPlainText("Success Count:    %i \nFail Count:       %i \nPercent Success:  %i" % (num_good,
                                                                                                         num_bad,
                                                                                                         percent))

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self.show_error)

    def init_tabs(self):
        # returns layout containing tab bar
        self.tab_widget = QtGui.QTabWidget()

        plus_button = QtGui.QPushButton("+", self)
        plus_button.clicked.connect(self.new_tab)
        self.tab_widget.setCornerWidget(plus_button)
        self.tab_widget.setMovable(True)

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

        self.setWindowIcon(QtGui.QIcon("data/icon.ico"))

        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')

        exit_action.triggered.connect(QtGui.qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        self.init_tabs()
        self.setCentralWidget(self.tab_widget)

        self.show()

    def show_error(self, message):
        QtGui.QMessageBox.about(self, "OH TEH NOES!", message)

    # ############ Main GUI Building function ###################
    def populate_tab(self, tab_object):
        """This method adds all the required GUI widgets to each tab and contains the start and stop methods that
        launch and end a batch of pings.

        This method is much much too long.
        """

        # Each tab gets an ID number as assigned by a generator.  This is NOT the same as the tab widget's index number,
        # as that changes when tabs are moved/deleted.  This ID is constant throughout the runtime of app and is used
        # to identify which tab sent (and should receive) data from a particular ping.
        tab_id = next(self.counter_iter)

        self.tab_objects[tab_id] = tab_object
        # TODO: Delete this?  Seems to be unused.
        self.threads = []

        def clear_stats():
            return {"Success Count": 0,
                    "Fail Count": 0}

        def start_ping(*args):
            ip = tab_object.ip_box.text().strip()
            ping_count = int(tab_object.ping_count_box.text())
            interval = int(tab_object.interval_box.text())
            packet_size = int(tab_object.packet_size_box.text())
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.currentIndex(), QtGui.QColor(0, 0, 0))

            # If the Session Label box has something in it, include that in the tab's title bar.
            if len(tab_object.session_label_box.text()) >= 1:
                label_text = " ".join([tab_object.session_label_box.text(), "-", ip])
            else: # Otherwise just show IP in tab title
                label_text = ip
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), label_text)

            output_text = "Starting ping to %s. \n Interval: %i seconds \n Count: %i \n" % (ip, interval, ping_count)
            tab_object.output_box.insertPlainText(output_text)

            # Initialize the thread with appropriate data, connect the slots (lalalalala) and start
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
            """
            Dumps the contents of the output text box into a file as plain text
            """
            file_types = "Plain Text (*.txt);;Plain Text (*.log)"
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.', file_types)
            try:
                fname = open(filename, 'w')
                fname.write(tab_object.summary_box.toPlainText() + "\n\n")
                fname.write(tab_object.output_box.toPlainText())
                fname.close()
            except:  #Yeah, I know, blanket exceptions are not a great idea.  This won't stay this way forever.
                self.show_error("Unable to save log file")
                raise

        tab_object.stats = clear_stats()
        tab_layout = QtGui.QGridLayout()

        # New Tab
        tab_object.new_tab_button = QtGui.QPushButton("New Tab", self)
        tab_object.new_tab_button.clicked.connect(self.new_tab)
        tab_layout.addWidget(tab_object.new_tab_button, 0, 1)

        # Close tab
        tab_object.close_tab_button = QtGui.QPushButton("Close Tab", self)
        tab_object.close_tab_button.clicked.connect(lambda: self.remove_tab(self.tab_widget.currentIndex()))
        tab_layout.addWidget(tab_object.close_tab_button, 0, 2)

        # Spacing hacks.  TODO:  learn better QT layout =P
        tab_object.spacer = QtGui.QLabel("")
        tab_layout.addWidget(tab_object.spacer, 1, 1)
        for i in range(4, 11):
            tab_object.spacer = QtGui.QLabel("              ")
            tab_layout.addWidget(tab_object.spacer, 0, i)

        # Ip address box
        tab_object.ip_label = QtGui.QLabel("Remote IP Address")
        tab_layout.addWidget(tab_object.ip_label, 2, 1)
        tab_object.ip_box = QtGui.QLineEdit("127.0.0.1")
        tab_object.ip_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.ip_box, 3, 1)

        # Session Label Box
        tab_object.session_label = QtGui.QLabel("Session Label (Optional)")
        tab_layout.addWidget(tab_object.session_label, 2, 2)
        tab_object.session_label_box = QtGui.QLineEdit("")
        tab_object.session_label_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.session_label_box, 3, 2)

        # Ping count box
        tab_object.ping_count_label = QtGui.QLabel("Count (0=infinite)")
        tab_layout.addWidget(tab_object.ping_count_label, 2, 3)
        tab_object.ping_count_box = QtGui.QLineEdit("0")
        tab_object.ping_count_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.ping_count_box, 3, 3)

        # Interval Box
        tab_object.interval_label = QtGui.QLabel("Interval (seconds)")
        tab_layout.addWidget(tab_object.interval_label, 2, 4)
        tab_object.interval_box = QtGui.QLineEdit("1")
        tab_object.interval_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.interval_box, 3, 4)

        # Packet Size
        tab_object.packet_size_label = QtGui.QLabel("Packet Size (bytes)")
        tab_layout.addWidget(tab_object.packet_size_label, 2, 5)
        tab_object.packet_size_box = QtGui.QLineEdit("64")
        tab_object.packet_size_box.returnPressed.connect(start_ping)
        tab_layout.addWidget(tab_object.packet_size_box, 3, 5)

        # Start Button
        tab_object.start_ping_button = QtGui.QPushButton('Start', self)
        tab_object.start_ping_button.clicked.connect(start_ping)
        tab_layout.addWidget(tab_object.start_ping_button, 3, 11)

        # Stop Button
        tab_object.stop_ping_button = QtGui.QPushButton('Stop', self)
        tab_object.stop_ping_button.clicked.connect(stop_ping)
        tab_object.stop_ping_button.setEnabled(False)
        tab_layout.addWidget(tab_object.stop_ping_button, 3, 12)

        # Output Box
        tab_object.output_box = QtGui.QPlainTextEdit()
        #tabObject.output_box.insertPlainText()
        tab_object.output_box.setReadOnly(True)
        tab_layout.addWidget(tab_object.output_box, 4, 1, 16, 10)

        # Summary Box
        tab_object.summary_box = QtGui.QPlainTextEdit()
        tab_layout.addWidget(tab_object.summary_box, 4, 11, 11, 2)

        # Clear Log button
        tab_object.clear_log_button = QtGui.QPushButton('Clear Log', self)
        tab_object.clear_log_button.clicked.connect(clear_log)
        tab_layout.addWidget(tab_object.clear_log_button, 19, 11)

        # Save Log button
        tab_object.save_log_button = QtGui.QPushButton('Save Log', self)
        tab_object.save_log_button.clicked.connect(save_log)
        tab_layout.addWidget(tab_object.save_log_button, 19, 12)

        # Audio options
        tab_object.audio_option_box = QtGui.QGroupBox("Audio Options")
        tab_object.audio_checkBox = QtGui.QCheckBox("Enable audio alerts")
        tab_object.alert_success_button = QtGui.QRadioButton("Alert on Success")
        tab_object.alert_failure_button = QtGui.QRadioButton("Alert on Failure")
        tab_object.alert_success_button.setChecked(True)
        tab_object.audio_checkBox.setChecked(False)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tab_object.audio_checkBox)
        vbox.addWidget(tab_object.alert_success_button)
        vbox.addWidget(tab_object.alert_failure_button)

        vbox.addStretch(1)
        tab_object.audio_option_box.setLayout(vbox)
        tab_layout.addWidget(tab_object.audio_option_box, 15, 11, 4, 2)

        tab_object.setLayout(tab_layout)

        return tab_object


def main():
    app = QtGui.QApplication(sys.argv)
    ex = PingPungGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 