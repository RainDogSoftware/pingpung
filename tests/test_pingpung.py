from unittest import TestCase, mock
from PyQt4 import QtCore, QtGui

from pingpung import pingpung as pp

__author__ = 'Josh Price'
class TestPingPung(TestCase):

    def test_init(self):
        # Init has no return value, so we're mainly checking properties
        instance = pp.PingPung()

        self.assertTrue(hasattr(instance, 'tabs'))
        self.assertIsInstance(instance.tabs, dict)
        self.assertTrue(hasattr(instance, 'counter_iter'))
        self.assertTrue(hasattr(instance, 'tab_button'))
        self.assertTrue(hasattr(instance, 'ui'))
        self.assertTrue(hasattr(instance.ui, 'tab_bar'))

    def test_add_tab(self):
        instance = pp.PingPung()
        pass