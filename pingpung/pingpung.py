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
    """
    A QThread subclass for running the pings.
    :param args:
    :return:

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
        self.emit(QtCore.SIGNAL('suite_complete'), self.tab_id)

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
        self.tab_button.clicked.connect(self._new_tab)
        self.ui.tab_bar.tabCloseRequested.connect(self._remove_tab)

        # Menu actions
        self.ui.actionExit.triggered.connect(QtGui.qApp.quit)
        self.ui.actionAbout_PingPung.triggered.connect(self._show_about)

        # Always start with one tab
        self._new_tab()

        self.ui.show()
        sys.exit(app.exec_())

    def _show_about(self):
        """
        Loads and displays the About page of the UI
        :return:
        """
        self.about = uic.loadUi("ppui/about.ui")
        self.about.show()

    def _run_button_action(self, tab_ui):
        #if this tab contains a running thread, terminate it
        if not self._set_inactive(tab_ui.tab_id):
            self._set_active(tab_ui.tab_id)

    def _connect_slots(self, sender):
        # ♫ Connect the slots.  Lalalalala. ♫
        self.connect(sender, QtCore.SIGNAL('complete'), self._show_result)
        self.connect(sender, QtCore.SIGNAL('error'), self._show_error)
        self.connect(sender, QtCore.SIGNAL('set_state_inactive'), self._set_inactive)
        self.connect(sender, QtCore.SIGNAL('set_state_active'), self._set_active)
        self.connect(sender, QtCore.SIGNAL('suite_complete'), self._suite_complete)


    ############################################################################################
    # Tab management

    def _new_tab(self, *args):
        """

        :param args:
        :return:
        """
        # Tab contents are in their own object, as each tab needs to operate independently of the others in all cases.
        # As noted in __init__, tabs must have an unchanging ID number for thread support
        tab_ui = uic.loadUi('ppui/pptab.ui')
        tab_ui.tab_id = next(self.counter_iter)
        tab_ui.last_num = -1

        # We keep an OrderedDict of the ping statistics for each tab.  This is used directly by the stats table
        tab_ui.stat_dict = self.get_default_stats()
        self._refresh_stat_display(tab_ui)

        # This is a dictionary of tabs keyed by ID number, so that they can be referenced later even if index changes
        self.tabs[tab_ui.tab_id] = tab_ui

        # Connect enter key to start/stop ping in tab, connect start/stop button as well
        tab_ui.ip_line.returnPressed.connect(lambda: self._run_button_action(tab_ui))
        tab_ui.session_line.returnPressed.connect(lambda: self._run_button_action(tab_ui))
        tab_ui.ping_count_line.returnPressed.connect(lambda: self._run_button_action(tab_ui))
        tab_ui.interval_line.returnPressed.connect(lambda: self._run_button_action(tab_ui))
        tab_ui.toggle_start.clicked.connect(lambda: self._run_button_action(tab_ui))
        tab_ui.toggle_start.setStyleSheet("background-color: #88DD88")

        # Connect the clear/save log buttons to actions
        tab_ui.clear_log_button.clicked.connect(lambda: self._clear_log(tab_ui))
        tab_ui.save_log_button.clicked.connect(lambda: self.save_log(tab_ui))

        # Always start with one tab
        self.ui.tab_bar.addTab(tab_ui, _("New Tab"))
        self.ui.tab_bar.setCurrentWidget(tab_ui)

    def _remove_tab(self, index):
        """
        Removes this tab as long as it is not the only remaining tab
        :param index:
        :return:
        """

        if self.ui.tab_bar.count() >= 2:
            tab_ui = self.ui.tab_bar.widget(index) # Get the tab object
            self._set_inactive(tab_ui.tab_id)       # Stop the ping (by id, NOT index)
            self.ui.tab_bar.removeTab(index)       # Remove the tab from UI (by index)
            self.tabs.pop(tab_ui.tab_id)           # Clear it from tabs dictionary
            tab_ui.setParent(None)                 # Free the object for garbage collection

    #def _current_index(self):
    #    current = self.ui.tab_bar.currentWidget()
    #    return self.ui.tab_bar.indexOf(current)

    def _get_index(self, tab_ui):
        return self.ui.tab_bar.indexOf(tab_ui)


    ############################################################################################
    # Stats & Data

    def _clear_log(self, tab_ui):
        """
        Clear the main output window, stat data dict, reset ping sequence number,  reset stats display table
        :param tab_ui: the tab instance to work on
        :return:
        """
        tab_ui.output_textedit.clear()
        tab_ui.stat_dict = self.get_default_stats()
        tab_ui.last_num = -1
        self._refresh_stat_display(tab_ui)

    def save_log(self, tab_ui):
        """
        Save the contents of the main output box to a plain text file of the user's choosing
        :param tab_ui: the tab instance to work on
        :return:
        """
        file_types = "Plain Text (*.txt);;Plain Text (*.log)"
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Log file', '.', file_types)
        if len(filename) > 0:  # Making sure the user selected a file (didn't hit Cancel)
            file_handle = open(filename, 'w')
            try:
                raise IndexError
                file_handle.write(tab_ui.output_textedit.toPlainText())
                file_handle.close()
            except Exception as e:
                # I don't normally do blanket exceptions, but in this case any error means we can't save file so
                # it all has the same effect.  Notify the user and move along.
                self._show_error("Unable to save log file.", e)

    def _show_result(self, result):
        """
        This method accepts the result dictionary from a ping and updates the text in the output box and the color of
        the tab text depending on the result.  It also initiates playback of success/fail sounds if the option is
        enabled in GUI
        :param result: The disctionary containing the results of the last ping
        :return:
        """
        # The ID number of the tab which sent the ping is provided by the PingThread class
        tab_ui = self.tabs[result["tabID"]]
        index = self._get_index(tab_ui)

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

        self._update_stats(result, tab_ui)

    @staticmethod
    def get_default_stats():
        """
        Takes no arguments, returns the disctionary to be used in the stats display
        :return:
        """
        return OrderedDict([("Success", 0),
                            ("Failure", 0),
                            ("", ""),
                            ("% Success", 0),
                            ("Highest Latency", ""),
                            ("Lowest Latency", ""),
                            ("Average Latency", ""),
                           ])

    @staticmethod
    def format_output_success(result):
        """
        This method accepts the result dictionary from a successful ping and generates colorized output
        :param result:
        :return: An html-formatted colorized string containing the timestamp, sequence number, text, packet size and
        responding IP from a successful ping
        """
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
        """
        This method accepts the result disctionary from a ping and generates colorized output
        :param result:
        :return: An html-formatted string containing the timestamp and error message
        """
        output = "<font color='red'>{:s} - {:s}</font>".format(result["Timestamp"], result['Message'])
        return output

    def _show_error(self, message, optional=""):
        QtGui.QMessageBox.about(self, "I'm sad now.", "\n".join([_(message), str(optional)]))

    def _refresh_stat_display(self, tab_ui):
        for row, key in enumerate(tab_ui.stat_dict.keys()):
            tab_ui.stats_table.setItem(row, 0, QtGui.QTableWidgetItem(key))
            tab_ui.stats_table.setItem(row, 1, QtGui.QTableWidgetItem(str(tab_ui.stat_dict[key])))

    def _update_stats(self, result, tab_ui):
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

        # TODO: Average latency

        tab_ui.stat_dict["% Success"] = round((tab_ui.stat_dict["Success"] / (tab_ui.stat_dict["Failure"] +
                                                                              tab_ui.stat_dict["Success"])) * 100, 2)
        self._refresh_stat_display(tab_ui)

    ############################################################################################
    # Ping Management

    def _suite_complete(self, id):
        """
        This is called when a limited number of pings have been specified.  It resets the appropriate counters, sets
        the program state to inacive, and adds a completion notice to the output box.
        :param id: The id number (not index) of the relevant tab
        :return:
        """
        tab_ui = self.tabs[id]

        # Some shorter variable names for brevity in upcoming list comprehension
        sd = tab_ui.stat_dict
        ot = tab_ui.output_textedit

        # Don't bother trying to clean/speed this up by putting a single <strong> tag around all lines at once, the gui
        # will only apply it to that one line.  Means we've got to <strong> each line individually.
        ot.append(_("<strong>Test Suite Complete</strong>"))
        [ot.append("<strong>{:s} {:s}</strong>".format(x, str(y))) for x,y in sd.items()]

        tab_ui.last_num = -1 # so sequence will start from 0 on next suite start
        self._set_inactive(id)

    def _set_inactive(self, id):
        """
        Sets the tab to the inactive state, including gui changes and terminating the thread
        :param id: The id number of the tab to set as inactive
        :return:
        """
        tab_ui = self.tabs[id]
        tab_ui.toggle_start.setText(_("Start"))
        tab_ui.toggle_start.setStyleSheet("background-color: #88DD88")
        index = self._get_index(tab_ui)
        self.ui.tab_bar.setTabIcon(index, QtGui.QIcon(""))

        if hasattr(tab_ui, "thread") and hasattr(tab_ui.thread, "isRunning") and (tab_ui.thread.isRunning() is True):
            tab_ui.thread.terminate()
            tab_ui.output_textedit.append(_("Pausing..."))
            return True
        else:
            return False

    def _set_active(self, id):
        """
        Sets the tab to active state, including gui changes and starting the ping thread
        :param id: The id number of the tab to set as active
        :return:
        """
        tab_ui = self.tabs[id]
        index = self._get_index(tab_ui)
        # Default to black text (in case tab text is colored from previous session)
        self.ui.tab_bar.tabBar().setTabTextColor(index, QtGui.QColor(0, 0, 0))

        try:
            ip = tab_ui.ip_line.text().strip()
            ping_count = int(tab_ui.ping_count_line.text().strip())
            interval = int(tab_ui.interval_line.text().strip())
            label = tab_ui.session_line.text().strip()
            packet_size = int(tab_ui.packet_size_line.text().strip())
        except ValueError as e:
            self._show_error("Invalid input\n" + str(e))
            return

        if packet_size > 65535:
                raise ValueError(_("Packet size too ridiculously large"))
        # We treat start/stop as start/pause, and a new session is indicated by a -1 sequence number
        # If positive, pick up from that sequence number
        if tab_ui.last_num > 0:
            seq_num = tab_ui.last_num
        else:
            seq_num = 0

        # Without this check, you could run an infitine ping (count 0), pause it, then run a finite ping with a count
        # lower than last_num, and it would instantly think the suite is complete.  Semi-obscure bug but worth a fix.
        if ping_count > 0:
            seq_num = 0

        tab_ui.output_textedit.append(_("Starting..."))
        tab_ui.thread = PingThread(ip, ping_count, interval, packet_size, tab_ui.tab_id, seq_num)
        self._connect_slots(tab_ui.thread)
        # Not in a try/except block because the thread does its own error checking and reports via signals
        tab_ui.thread.start()

        tab_ui.toggle_start.setText(_("Pause"))
        tab_ui.toggle_start.setStyleSheet("background-color: #DD8888")
        self.ui.tab_bar.setTabIcon(index, QtGui.QIcon("data/play.ico"))

        # No sense placing a hyphen if there's nothing on the other side
        if len(label) < 1:
            self.ui.tab_bar.setTabText(index, ip)
        else:
            self.ui.tab_bar.setTabText(index, " - ".join([ip, label]))

if __name__ == '__main__':
    PingPung()