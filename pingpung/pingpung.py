import sys
import time
from collections import OrderedDict
from itertools import count
from gettext import gettext as _

from PyQt4 import QtCore, QtGui, uic

from pplib import pping, audio
from pplib.pptools import debug

############################################################################################
# Ping Thread
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

    def __init__(self, ip, ping_count, interval, packet_size, tab_id, start_num):
        super(PingThread, self).__init__()
        self.ip = ip
        self.ping_count = int(ping_count)
        self.interval = int(interval)
        self.packet_size = int(packet_size)
        self.tab_id = int(tab_id)
        self.start_num = start_num


    def run(self):
        seq_num = self.start_num
        while (seq_num < self.ping_count) or (self.ping_count == 0):
            seq_num += 1
            # Cannot accept sequence number > 65535.  This resets seq number but does not affect stats totals
            if seq_num > 65535:
                seq_num = 0

            try:
                self.result = pping.ping(self.ip, 5000, seq_num, self.packet_size)
            except ValueError:
                self.emit(QtCore.SIGNAL('error'), _("Invalid input"))
                break
            except pping.SocketError:
                self.emit(QtCore.SIGNAL('error'), _("Socket Error.  Check ip/domain and be certain app is running as root/admin"))
                break
            except pping.AddressError:
                self.emit(QtCore.SIGNAL('error'), _("Address error.  Check IP/domain setting."))
                break

            self.result["tabID"] = self.tab_id
            self.emit(QtCore.SIGNAL('complete'), self.result)
            time.sleep(self.interval)
        self.emit(QtCore.SIGNAL('suite_complete'), {"tabID": self.tab_id})

############################################################################################
# Main
class PingPung(QtGui.QMainWindow):
    ############################################################################################
    # UI Setup
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
        self.tab_button = QtGui.QToolButton(self)
        self.tab_button.setText('+')
        self.ui.tab_bar.setCornerWidget(self.tab_button)
        self.tab_button.clicked.connect(self.new_tab)
        self.ui.tab_bar.tabCloseRequested.connect(self.ui.tab_bar.removeTab)

        # Menu actions
        self.ui.actionExit.triggered.connect(QtGui.qApp.quit)
        self.ui.actionAbout_PingPung.triggered.connect(self.show_about)

        # Always start with one tab
        self.new_tab()

        self.ui.show()
        sys.exit(app.exec_())

    def show_about(self):
        #TODO:  Figure out why this window just flashes up briefly
        about = uic.loadUi("ppui/about.ui")
        about.show()

    def run_button_action(self, tab_ui):
        #if this tab contains a running thread, terminate it
        if not self._set_inactive(tab_ui.tab_id):
            self._set_active(tab_ui.tab_id)

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self.show_error)
        self.connect(sender, QtCore.SIGNAL('set_state_inactive'), self._set_inactive)
        self.connect(sender, QtCore.SIGNAL('set_state_active'), self._set_active)
        self.connect(sender, QtCore.SIGNAL('suite_complete'), self._suite_complete)


    ############################################################################################
    # Tab management

    def new_tab(self, *args):
        # Tab contents are in their own object, as each tab needs to operate independently of the others in all cases.
        # As noted in __init__, tabs must have an unchanging ID number for thread support
        tab_ui = uic.loadUi('ppui/pptab.ui')
        tab_ui.tab_id = next(self.counter_iter)
        tab_ui.last_num = -1

        # We keep an OrderedDict of the ping statistics for each tab.  This is used directly by the stats table
        tab_ui.stat_dict = self.get_default_stats()
        self.refresh_stat_display(tab_ui)

        # This is a dictionary of tabs keyed by ID number, so that they can be referenced later even if index changes
        self.tabs[tab_ui.tab_id] = tab_ui

        # Connect enter key to start/stop ping in tab, connect start/stop button as well
        tab_ui.ip_line.returnPressed.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.session_line.returnPressed.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.ping_count_line.returnPressed.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.interval_line.returnPressed.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.toggle_start.clicked.connect(lambda: self.run_button_action(tab_ui))
        tab_ui.toggle_start.setStyleSheet("background-color: #88DD88")

        # Connect the clear/save log buttons to actions
        tab_ui.clear_log_button.clicked.connect(lambda: self.clear_log(tab_ui))
        tab_ui.save_log_button.clicked.connect(lambda: self.save_log(tab_ui))

        self.ui.tab_bar.addTab(tab_ui, _("New Tab"))

    def current_index(self):
        current = self.ui.tab_bar.currentWidget()
        return self.ui.tab_bar.indexOf(current)

    def get_index(self, tab_ui):
        return self.ui.tab_bar.indexOf(tab_ui)


    ############################################################################################
    # Stats & Data

    @staticmethod
    def get_default_stats():
        return OrderedDict([("Success", 0),
                            ("Failure", 0),
                            ("", ""),
                            ("% Success", 0),
                            ("Highest Latency", ""),
                            ("Lowest Latency", ""),
                           ])

    def clear_log(self, tab_ui):
        tab_ui.output_textedit.clear()
        tab_ui.stat_dict = self.get_default_stats()
        tab_ui.last_num = -1
        self.refresh_stat_display(tab_ui)

    def save_log(self, tab_ui):
        file_types = "Plain Text (*.txt);;Plain Text (*.log)"
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Log file', '.', file_types)
        if len(filename) > 0:  # Making sure the user selected a file (didn't hit Cancel)
            file_handle = open(filename, 'w')
            try:
                file_handle.write(tab_ui.output_textedit.toPlainText())
                file_handle.close()
            except Exception as e:
                # I don't normally do blanket exceptions, but in this case any error means we can't save file so
                # it all has the same effect.  Notify the user and move along.
                self.show_error("Unable to save log file")

    ############################################################################################
    # Ping Management

    def _suite_complete(self, result):
        tab_ui = self.tabs[result["tabID"]]
        tab_ui.output_textedit.append(_("Test Suite Complete"))
        tab_ui.last_num = -1
        self._set_inactive(result["tabID"])

    def _set_inactive(self, id):
        tab_ui = self.tabs[id]
        tab_ui.toggle_start.setText(_("Start"))
        tab_ui.toggle_start.setStyleSheet("background-color: #88DD88")
        index = self.get_index(tab_ui)
        self.ui.tab_bar.setTabIcon(index, QtGui.QIcon(""))
        if hasattr(tab_ui, "thread") and hasattr(tab_ui.thread, "isRunning") and (tab_ui.thread.isRunning() is True):
            tab_ui.thread.terminate()
            return True
        else:
            return False

    def _set_active(self, id):
        tab_ui = self.tabs[id]
        self.setWindowIcon(QtGui.QIcon("data/icon.ico"))

        try:
            ip = tab_ui.ip_line.text().strip()

            ping_count = int(tab_ui.ping_count_line.text().strip())
            interval = int(tab_ui.interval_line.text().strip())
        except ValueError:
            self.show_error("Invalid input")
            return

        if tab_ui.last_num > 0:
            seq_num = tab_ui.last_num
        else:
            seq_num = 0

        tab_ui.thread = PingThread(ip, ping_count, interval, 64, tab_ui.tab_id, seq_num)
        self.connect_slots(tab_ui.thread)
        tab_ui.thread.start()
        tab_ui.toggle_start.setText(_("Pause"))
        tab_ui.toggle_start.setStyleSheet("background-color: #DD8888")

        index = self.get_index(tab_ui)
        self.ui.tab_bar.setTabIcon(index, QtGui.QIcon("data/play.ico"))

        tab_ui.setStyleSheet('QTabBar::tab {background-color: red;}')
        self.ui.tab_bar.setTabText(self.current_index(), " - ".join([ip, tab_ui.session_line.text()]))


    def show_result(self, result):
        # The ID number of the tab which sent the ping is provided by the PingThread class
        tab_ui = self.tabs[result["tabID"]]
        index = self.get_index(tab_ui)

        if result["Success"]:
            self.ui.tab_bar.tabBar().setTabTextColor(index, QtGui.QColor(0, 128, 0))
            output = self.format_output_success(result)
            tab_ui.last_num = result["SeqNumber"]
            if tab_ui.toggle_audio.isChecked() and tab_ui.alert_success.isChecked():
                audio.play("data/woohoo.wav")
        else:
            self.ui.tab_bar.tabBar().setTabTextColor(index, QtGui.QColor(128, 0, 0))
            output = self.format_output_failure(result)
            if tab_ui.toggle_audio.isChecked() and tab_ui.alert_failure.isChecked():
                audio.play("data/doh.wav")

        output_box = tab_ui.output_textedit
        output_box.append(_(output))
        self.last_num = result["SeqNumber"]

        self.update_stats(result, tab_ui)

    @staticmethod
    def format_output_success(result):
        delay = result["Delay"]
        if delay > 100:
            color = "red"
        elif delay > 50:
            color = "#FF9900"
        else:
            color = "green"

        ms = "<font color='{:s}'>{:.2f}</font>".format(color, delay)
        output = "{:s} {:d} - {:s} - {:d} bytes from {:s}  time={:s} ms".format(result["Timestamp"], result['SeqNumber'],
                                                                result['Message'], result["PacketSize"],
                                                                result['Responder'], ms)
        return output

    @staticmethod
    def format_output_failure(result):
        output = "<font color='red'>{:s} - {:s}</font>".format(result["Timestamp"], result['Message'])
        return output

    def show_error(self, message):
        QtGui.QMessageBox.about(self, "I'm sad now.", _(message))

    def refresh_stat_display(self, tab_ui):
        for row, key in enumerate(tab_ui.stat_dict.keys()):
            tab_ui.stats_table.setItem(row, 0, QtGui.QTableWidgetItem(key))
            tab_ui.stats_table.setItem(row, 1, QtGui.QTableWidgetItem(str(tab_ui.stat_dict[key])))

    def update_stats(self, result, tab_ui):
        if result["Success"]:
            tab_ui.stat_dict["Success"] += 1
            # This is sloppy,
            # TODO: come back and clean this up.
            high = tab_ui.stat_dict["Highest Latency"]
            low = tab_ui.stat_dict["Lowest Latency"]
            delay = round(result["Delay"], 2)

            if high == "":
                tab_ui.stat_dict["Highest Latency"] = delay
                high = result["Delay"]

            if low == "":
                tab_ui.stat_dict["Lowest Latency"] = delay
                low = result["Delay"]

            if result["Delay"] > high:
                tab_ui.stat_dict["Highest Latency"] = delay
            elif result["Delay"] < low:
                tab_ui.stat_dict["Lowest Latency"] = delay
        else:
            tab_ui.stat_dict["Failure"] += 1

        tab_ui.stat_dict["% Success"] = round((tab_ui.stat_dict["Success"] / (tab_ui.stat_dict["Failure"] +
                                                                              tab_ui.stat_dict["Success"])) * 100, 2)
        self.refresh_stat_display(tab_ui)

if __name__ == '__main__':
    PingPung()