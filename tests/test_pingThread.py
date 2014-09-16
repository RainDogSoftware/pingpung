from unittest import TestCase, mock
from PyQt4 import QtCore

from pingpung import pingpung as pp
#from pplib import pping

__author__ = 'josh'


class TestPingThread(TestCase):
    def test_thread_object(self):
        this_thread = pp.PingThread(1,1,1,1,1)

    def test_run(self):
        pass