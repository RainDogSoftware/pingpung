# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pplib/tab.ui'
#
# Created: Mon Sep  1 12:09:43 2014
#      by: PyQt4 UI code generator 4.10.3
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
        tab_container.resize(777, 631)
        self.gridLayoutWidget = QtGui.QWidget(tab_container)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 781, 631))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit_3 = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout.addWidget(self.lineEdit_3, 1, 1, 1, 1)
        self.textEdit = QtGui.QTextEdit(self.gridLayoutWidget)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 2, 0, 1, 4)
        self.lineEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 1, 3, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout.addWidget(self.lineEdit_2, 1, 2, 1, 1)
        self.ip_line = QtGui.QLineEdit(self.gridLayoutWidget)
        self.ip_line.setObjectName(_fromUtf8("ip_line"))
        self.gridLayout.addWidget(self.ip_line, 1, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 1, 4, 1, 1)
        self.ip_line_label = QtGui.QLabel(self.gridLayoutWidget)
        self.ip_line_label.setObjectName(_fromUtf8("ip_line_label"))
        self.gridLayout.addWidget(self.ip_line_label, 0, 0, 1, 1)

        self.retranslateUi(tab_container)
        QtCore.QMetaObject.connectSlotsByName(tab_container)

    def retranslateUi(self, tab_container):
        tab_container.setWindowTitle(_translate("tab_container", "tab_container", None))
        self.pushButton.setText(_translate("tab_container", "PushButton", None))
        self.ip_line_label.setText(_translate("tab_container", "IP or Domain Name", None))

