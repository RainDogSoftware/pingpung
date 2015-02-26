from unittest import TestCase, mock
from pplib import pping
from PyQt4 import QtCore
import time

from pingpung import pingpung as pp
#from pplib import pping

__author__ = 'Josh Price'

# I've never attempted unit tests on threads before.  I'm going to have to work on that before attempting it here.
# So let's just be sure we've got our variable assignments right.


class TestPingThread(TestCase):
    def test_thread_attribs(self):
        this_thread = pp.PingThread(1, 2, 3, 4, 5, 6)

        self.assertEqual(this_thread.ip, 1)
        self.assertEqual(this_thread.ping_count, 2)
        self.assertEqual(this_thread.interval, 3)
        self.assertEqual(this_thread.packet_size, 4)
        self.assertEqual(this_thread.tab_id, 5)
        self.assertEqual(this_thread.start_num, 6)







