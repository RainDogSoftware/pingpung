# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ppui/pptab.ui'
#
# Created: Fri Sep  5 13:53:07 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_tab_container(object):
    def setupUi(self, tab_container):
        tab_container.setObjectName(_fromUtf8("tab_container"))
        tab_container.resize(891, 649)
        self.gridLayout_2 = QtGui.QGridLayout(tab_container)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.session_line = QtGui.QLineEdit(tab_container)
        self.session_line.setObjectName(_fromUtf8("session_line"))
        self.gridLayout.addWidget(self.session_line, 1, 1, 1, 1)
        self.interval_line = QtGui.QLineEdit(tab_container)
        self.interval_line.setObjectName(_fromUtf8("interval_line"))
        self.gridLayout.addWidget(self.interval_line, 1, 3, 1, 1)
        self.ping_count_line = QtGui.QLineEdit(tab_container)
        self.ping_count_line.setObjectName(_fromUtf8("ping_count_line"))
        self.gridLayout.addWidget(self.ping_count_line, 1, 2, 1, 1)
        self.ip_line = QtGui.QLineEdit(tab_container)
        self.ip_line.setObjectName(_fromUtf8("ip_line"))
        self.gridLayout.addWidget(self.ip_line, 1, 0, 1, 1)
        self.toggle_start = QtGui.QPushButton(tab_container)
        self.toggle_start.setObjectName(_fromUtf8("toggle_start"))
        self.gridLayout.addWidget(self.toggle_start, 1, 4, 1, 1)
        self.ip_line_label = QtGui.QLabel(tab_container)
        self.ip_line_label.setObjectName(_fromUtf8("ip_line_label"))
        self.gridLayout.addWidget(self.ip_line_label, 0, 0, 1, 1)
        self.stats_table = QtGui.QTableWidget(tab_container)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setRowCount(12)
        self.stats_table.setColumnCount(2)
        self.stats_table.setObjectName(_fromUtf8("stats_table"))
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(1, 0, item)
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(2, 0, item)
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(4, 0, item)
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(5, 0, item)
        item = QtGui.QTableWidgetItem()
        self.stats_table.setItem(6, 0, item)
        self.stats_table.horizontalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setMinimumSectionSize(40)
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.verticalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.stats_table, 2, 4, 1, 1)
        self.groupBox = QtGui.QGroupBox(tab_container)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.toggle_audio = QtGui.QCheckBox(self.groupBox)
        self.toggle_audio.setObjectName(_fromUtf8("toggle_audio"))
        self.verticalLayout.addWidget(self.toggle_audio)
        self.radioButton = QtGui.QRadioButton(self.groupBox)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.verticalLayout.addWidget(self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.verticalLayout.addWidget(self.radioButton_2)
        self.gridLayout.addWidget(self.groupBox, 3, 4, 1, 1)
        self.output_textedit = QtGui.QTextEdit(tab_container)
        self.output_textedit.setObjectName(_fromUtf8("output_textedit"))
        self.gridLayout.addWidget(self.output_textedit, 2, 0, 2, 4)
        self.label = QtGui.QLabel(tab_container)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(tab_container)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.label_3 = QtGui.QLabel(tab_container)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(tab_container)
        QtCore.QMetaObject.connectSlotsByName(tab_container)

    def retranslateUi(self, tab_container):
        tab_container.setWindowTitle(_translate("tab_container", "tab_container", None))
        self.interval_line.setText(_translate("tab_container", "1", None))
        self.ping_count_line.setText(_translate("tab_container", "5", None))
        self.ip_line.setText(_translate("tab_container", "127.0.0.1", None))
        self.toggle_start.setText(_translate("tab_container", "Start", None))
        self.ip_line_label.setText(_translate("tab_container", "IP or Domain Name", None))
        __sortingEnabled = self.stats_table.isSortingEnabled()
        self.stats_table.setSortingEnabled(False)
        self.stats_table.setSortingEnabled(__sortingEnabled)
        self.groupBox.setTitle(_translate("tab_container", "GroupBox", None))
        self.toggle_audio.setText(_translate("tab_container", "Enable Audio", None))
        self.radioButton.setText(_translate("tab_container", "Alert on Success", None))
        self.radioButton_2.setText(_translate("tab_container", "Alert on Failure", None))
        self.label.setText(_translate("tab_container", "Session Label", None))
        self.label_2.setText(_translate("tab_container", "Ping Count", None))
        self.label_3.setText(_translate("tab_container", "Interval", None))

