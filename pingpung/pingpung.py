import sys
import time
from itertools import count
from gettext import gettext as _

from PyQt4 import QtCore, QtGui, uic

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
        self.ping_count = int(ping_count)
        self.interval = interval
        self.packet_size = packet_size
        self.tab_id = tab_id
        super(PingThread, self).__init__()

    def run(self):
        pcount = 0
        while (pcount < self.ping_count) or (self.ping_count == 0):
            pcount += 1
            # Cannot accept sequence number > 65535.  This resets seq number but does not affect stats totals
            if pcount > 65535: pcount = 0

            self.result = pping.ping(self.ip, 1000, pcount, self.packet_size)
            self.result["tabID"] = self.tab_id
            self.emit(QtCore.SIGNAL('complete'), self.result)
            time.sleep(self.interval)


class PingPung(QtGui.QMainWindow):
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        super(PingPung, self).__init__()

        self.ui = uic.loadUi('ppui/maingui.ui')


        # Preparing to handle multiple tabs of pings.  We keep a dict in self.tabs so that they can be referenced by
        # id number, as assigned by the counter below.  It's worth noting that this is because index number in tab
        # bar widget is not enough.  If a tab's index number changes while the ping thread is running, crazy
        # things could happen.  This is always why they're kept in a dict instead of a list or something dynamically
        # numbered.
        self.tabs = {}
        self.counter_iter = count()

        # Functionality for adding and removing tabs
        self.tabButton = QtGui.QToolButton(self)
        self.tabButton.setText('+')
        self.ui.tab_bar.setCornerWidget(self.tabButton)
        self.tabButton.clicked.connect(self.new_tab)
        self.ui.tab_bar.tabCloseRequested.connect(self.ui.tab_bar.removeTab)

        # Always start with one tab
        #self.new_tab()
        self.new_tab()

        self.ui.show()
        sys.exit(app.exec_())

    def new_tab(self, *args):
        # Tab contents are in their own object, as each tab needs to operate independently of the others in all cases
        tab_ui = uic.loadUi('ppui/pptab.ui')
        tab_ui.tab_id = next(self.counter_iter)
        self.init_stats(tab_ui)

        # This is a dictionary of tabs keyed by ID number, so that they can be referenced later even if index changes
        self.tabs[tab_ui.tab_id] = tab_ui

        # Connect enter key to start/stop ping in tab, connect start/stop button as well
        tab_ui.ip_line.returnPressed.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.toggle_start.clicked.connect(lambda: self.run_button_action(tab_ui))

        # Connect the clear/save log buttons to actions
        tab_ui.clear_log_button.clicked.connect(lambda: self.clear_log(tab_ui))
        tab_ui.save_log_button.clicked.connect(lambda: self.save_log(tab_ui))


        self.ui.tab_bar.addTab(tab_ui, _("New Tab"))

    def clear_log(self, tab_ui):
        tab_ui.output_textedit.clear()
        stats = tab_ui.stats_table
        stats.setItem(0,1, QtGui.QTableWidgetItem("0"))
        stats.setItem(1,1, QtGui.QTableWidgetItem("0"))

    def save_log(self, tab_ui):
        file_types = "Plain Text (*.txt);;Plain Text (*.log)"
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Log file', '.', file_types)
        if len(filename) > 0:
            file_handle = open(filename, 'w')
            try:
                file_handle.write(tab_ui.output_textedit.toPlainText())
                file_handle.close()
            except Exception as e:
                # I don't normally do blanket exceptions, but in this case any error means we can't save file so
                # it all has the same effect.  Notify the user and move along.
                self.show_error("Unable to save log file")

    def current_index(self):
        """
         Because we're using 2 forms, one for the main window ui and one for the tabs, the tab widget
         as supplied by Qt Designer is not a "normal" tab widget.  We've got to use it to retrieve the index of the
         widget
        """
        current = self.ui.tab_bar.currentWidget()
        return self.ui.tab_bar.indexOf(current)

    def start_ping(self, tab_ui):
        ip = tab_ui.ip_line.text().strip()
        ping_count = tab_ui.ping_count_line.text().strip()
        interval = int(tab_ui.interval_line.text().strip())

        # Check if running, then initialize the thread with appropriate data, connect the slots (lalalalala) and start
        try:
            tab_ui.thread.terminate()
        except AttributeError:
            pass

        # Initialize the thread with appropriate data, connect the slots (lalalalala) and start
        tab_ui.thread = PingThread(ip, ping_count, interval, 64, tab_ui.tab_id)

        self.connect_slots(tab_ui.thread)
        tab_ui.toggle_start.setText(_("Stop"))

        try:
            tab_ui.thread.start()
        except ValueError:
            self.show_error("Invalid input")
        except pping.SocketError:
            self.show_error("Socket Error.  verify that programming is running as root/admin.  See README for details.")
        except pping.AddressError:
            self.show_error("Address error.  Check IP/domain setting.")


    def run_button_action(self, tab_ui):
        #if this tab contains a running thread, terminate it
        if hasattr(tab_ui, "thread") and hasattr(tab_ui.thread, "isRunning") and (tab_ui.thread.isRunning() is True):
            tab_ui.thread.terminate()
            tab_ui.toggle_start.setText(_("Start"))
        else:
            ip = tab_ui.ip_line.text().strip()
            # TODO:  Try/catch with error gui
            ping_count = int(tab_ui.ping_count_line.text().strip())
            interval = int(tab_ui.interval_line.text().strip())
            tab_ui.thread = PingThread(ip, ping_count, interval, 64, tab_ui.tab_id)
            self.connect_slots(tab_ui.thread)
            tab_ui.thread.start()

            # Update GUI labels
            tab_ui.toggle_start.setText("Stop")
            self.ui.tab_bar.setTabText(self.current_index(), " ".join([ip,tab_ui.session_line.text()]))

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self.show_error)

    def show_result(self, result):
        # The ID number of the tab which sent the ping is provided by the PingThread class
        tab_ui = self.tabs[result["tabID"]]
        index = self.ui.tab_bar.indexOf(tab_ui)

        if result["Success"]:
            self.ui.tab_bar.tabBar().setTabTextColor(index, QtGui.QColor(0, 128, 0))
            output = "%s %i - %s - %i bytes from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'],
                                                                       result['Message'], result["PacketSize"],
                                                                       result['Responder'], result['Delay'])
            if tab_ui.toggle_audio.isChecked() and tab_ui.alert_success.isChecked():
                audio.play("data/woohoo.wav")
        else:
            self.ui.tab_bar.tabBar().setTabTextColor(index, QtGui.QColor(128, 0, 0))
            output = "%s %i - %s \n" % (result["Timestamp"], result['SeqNumber'], result['Message'])
            if tab_ui.toggle_audio.isChecked() and tab_ui.alert_failure.isChecked():
                audio.play("data/doh.wav")

        # Move cursor to end, append text, move to end again.  Because reasons.
        output_box = tab_ui.output_textedit
        output_box.moveCursor(QtGui.QTextCursor.End)
        output_box.insertPlainText(_(output))
        output_box.moveCursor(QtGui.QTextCursor.End)

        self.update_stats(result, tab_ui)

    def show_error(self, message):
        QtGui.QMessageBox.about(self, "I'm sad now.", _(message))


    def init_stats(self, tab_ui):
        stat_list = (("Success", "0"),
                     ("Failures", "0"),
                     ("", ""),
                     ("% Success", ""),
                     ("Highest Latency", "NI"),
                     ("Lowest Latency", "NI"),
        )
        for row, item in enumerate(stat_list):
            tab_ui.stats_table.setItem(row,0, QtGui.QTableWidgetItem(item[0]))
            tab_ui.stats_table.setItem(row,1, QtGui.QTableWidgetItem(item[1]))

        """tab_ui.stats_table.setItem(0,0,QtGui.QTableWidgetItem("Successes"))
        tab_ui.stats_table.setItem(0,1,QtGui.QTableWidgetItem("0"))

        tab_ui.stats_table.setItem(1,0,QtGui.QTableWidgetItem("Failures"))
        tab_ui.stats_table.setItem(1,1,QtGui.QTableWidgetItem("0"))

        tab_ui.stats_table.setItem(2,0,QtGui.QTableWidgetItem("% Success"))
        tab_ui.stats_table.setItem(2,1,QtGui.QTableWidgetItem(""))"""

    def update_stats(self, result, tab_ui):
        #TODO: Make init_stats and update_stats use a common data structure.  Probably dict.
        stats = tab_ui.stats_table
        num_good = int(stats.item(0,1).text())
        num_bad = int(stats.item(1,1).text())
        if result["Success"]:
            # Update success and fail counts.  The math must be done with integers (of course) but table expects strings
            num_good = int(num_good) + 1
            stats.setItem(0, 1, QtGui.QTableWidgetItem(str(num_good)))
        else:
            num_bad = int(num_bad) +1
            stats.setItem(1, 1, QtGui.QTableWidgetItem(str(num_bad)))

        percent = round((num_good / (num_bad + num_good)) * 100, 2)
        stats.setItem(3,1, QtGui.QTableWidgetItem(str(percent)))

if __name__ == '__main__':
    PingPung()