import sys
import time
from itertools import count

from PyQt4 import QtCore, QtGui

from pplib import pping, audio
from ppui import maingui, pptab

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


class PingPung(QtGui.QMainWindow):
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        super(PingPung, self).__init__()

        self.ui = maingui.Ui_MainWindow()
        self.ui.setupUi(self)

        # Hack until I can get Designer to only start with 1 tab
        self.ui.tab_bar.removeTab(0)
        self.ui.tab_bar.removeTab(0)

        # Preparing to handle multiple tabs of pings.  We keep a dict in self.tabs so that they can be referenced by
        # id number, as assigned by the counter below.  It's worth noting that this is because index number in tab
        # bar widget is not enough.  If a tab's index number changes while the ping thread is running, crazy
        # things could happen
        self.tabs = {}
        self.counter_iter = count()

        # Always start with one tab
        self.new_tab()
        self.new_tab()

        self.show()
        sys.exit(app.exec_())

    def new_tab(self, name="New Tab"):
        # Tab contents are in their own object, as each tab needs to operate independently of the others in all cases
        tab_ui = pptab.Ui_tab_container()
        new_tab_object = QtGui.QWidget()
        tab_ui.setupUi(new_tab_object)
        tab_ui.tab_id = next(self.counter_iter)
        # This is a dictionary of tabs keyed by ID number, so that they can be referenced later even if index changes
        self.tabs[tab_ui.tab_id] = tab_ui
        tab_ui.ip_line.returnPressed.connect(lambda: self.start_ping(tab_ui))
        tab_ui.toggle_start.clicked.connect(lambda: self.start_ping(tab_ui))

        self.ui.tab_bar.addTab(new_tab_object, name)

    def start_ping(self, tab_ui):
        ip = tab_ui.ip_line.text().strip()
        # TODO:  Try/catch with error gui
        ping_count = int(tab_ui.ping_count_line.text().strip())
        interval = int(tab_ui.interval_line.text().strip())

        # Initialize the thread with appropriate data, connect the slots (lalalalala) and start
        tab_ui.thread = PingThread(ip, ping_count, interval, 64, tab_ui.tab_id)
        self.connect_slots(tab_ui.thread)
        tab_ui.thread.start()

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('complete'), self.show_result)
        #self.connect(sender, QtCore.SIGNAL('error'), self.show_error)
        #self.connect(sender, QtCore.SIGNAL('complete'), lambda: print("huzzah!"))
        self.connect(sender, QtCore.SIGNAL('error'), lambda: print("failz!"))

    def show_result(self, result):
        tab_ui = self.tabs[result["tabID"]]
        #tab_index = self.ui.tab_bar.indexOf(tab_ui)
        if result["Success"]:
            print(result)

            output = "%s %i - %s - %i bytes from %s  time=%i ms \n" % (result["Timestamp"], result['SeqNumber'],
                                                                       result['Message'], result["PacketSize"],
                                                                       result['Responder'], result['Delay'])
            output_box = tab_ui.output_textedit
            output_box.moveCursor(QtGui.QTextCursor.End)
            output_box.insertPlainText(output)
            output_box.moveCursor(QtGui.QTextCursor.End)
            #tab_ui.output_textedit.a

        self.update_stats(result, tab_ui)
        #stats = tab_ui.stats_table
        #rows = stats.rowCount()
        #cols = stats.columnCount()
        #for row in range(result): # Yeah right here
        #    stats.setItem(row,0,QtGui.QTableWidgetItem("stuff"))
        #stats.setItem(0,0,QtGui.QTableWidgetItem("stuff"))

    def update_stats(self, result, tab_ui):
        pass


if __name__ == '__main__':
    PingPung()