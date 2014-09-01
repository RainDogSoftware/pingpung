from PyQt4 import QtGui
import sys
from itertools import count

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

	    # Set base window properties
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PingPung')
        self.setWindowIcon(QtGui.QIcon("data/icon.ico"))

        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        self.statusBar()

        # Add base widgets & tab bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        self.tab_bar = QtGui.QTabWidget()
        plus_button = QtGui.QPushButton("+", self)
        plus_button.clicked.connect(self.new_tab)
        self.tab_bar.setCornerWidget(plus_button)
        self.tab_bar.setMovable(True)

        #self.init_tabs()
        self.setCentralWidget(self.tab_bar)

        self.counter_iter = count()
        self.tab_objects = {}

        self.show()

    def new_tab(self, somebool, name="New Tab"):
        this_tab = PingTab()
        index = self.tab_bar.addTab(this_tab, name)
        self.tab_bar.setCurrentIndex(index)


class PingTab(QtGui.QWidget):
    def __init__(self):
        super(PingTab, self).__init__()

    tab_layout = QtGui.QGridLayout()


#def run_pingpung():
#    app = QtGui.QApplication(sys.argv)
#    ex = MainWindow()
#    sys.exit(app.exec_())