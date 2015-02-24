from unittest import TestCase, mock
from pplib import pping
from PyQt4 import QtCore
import time

from pingpung import pingpung as pp
#from pplib import pping

__author__ = 'josh'


class TestPingThread(TestCase):
    def test_thread_attribs(self):
        this_thread = pp.PingThread(1, 2, 3, 4, 5, 6)

        self.assertEqual(this_thread.ip, 1)
        self.assertEqual(this_thread.ping_count, 2)
        self.assertEqual(this_thread.interval, 3)
        self.assertEqual(this_thread.packet_size, 4)
        self.assertEqual(this_thread.tab_id, 5)
        self.assertEqual(this_thread.start_num, 6)

    def test_run(self):
        # Mock over the signal sending

        # Mock over the actual ping call, confirm it's mocked
        mock_result = {"Success": True,
                       "Message": "Success",
                       "Responder": "1.1.1.1",
                       "SeqNumber": 42,
                       "Delay": 42,
                       "PacketSize": 42,
                       "Timestamp": "Yesterday?"}
        pping.ping = mock.MagicMock(return_value=mock_result)
        self.assertEqual(pping.ping("junk"), mock_result)

        # Then "run" some pings
        this_thread = pp.PingThread(1, 2, 3, 4, 5, 6)






