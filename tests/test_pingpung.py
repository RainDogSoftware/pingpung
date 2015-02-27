import sys
import unittest
from unittest import TestCase, mock
from PyQt4 import QtCore, QtGui

from pingpung import pingpung as pp

__author__ = 'Josh Price'
class TestPingPung(TestCase):
    def setUp(self):
        '''Create the GUI'''
        self.app = QtGui.QApplication(sys.argv)
        self.form = pp.PingPung()

    def test_properties(self):
        # Init has no return value, so we're mainly checking properties
        self.assertTrue(hasattr(self.form, 'tabs'))
        self.assertIsInstance(self.form.tabs, dict)
        self.assertTrue(hasattr(self.form, 'counter_iter'))
        self.assertTrue(hasattr(self.form, 'tab_button'))
        self.assertTrue(hasattr(self.form, 'ui'))
        self.assertTrue(hasattr(self.form.ui, 'tab_bar'))

        pass

    def test_add_tab(self):
        pass

    def test_woozle_wozzle(self):
        pass

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()