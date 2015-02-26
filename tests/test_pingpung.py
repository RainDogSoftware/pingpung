from unittest import TestCase, mock
from PyQt4 import QtCore, QtGui

from pingpung import pingpung as pp

__author__ = 'Josh Price'
class TestPingPung(TestCase):
    def test_init(self):
        # Checking properties and variable assignment
        instance = pp.PingPung()

        #Check for tabs dict
        self.assertTrue(hasattr(instance, 'tabs'))
