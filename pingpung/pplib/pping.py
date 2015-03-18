#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
"""
    A pure python ping implementation using raw sockets.
  
    (This is Python 3 port of https://github.com/jedie/python-ping)
  
    Note that ICMP messages can only be sent from processes running as root
    (in Windows, you must run this script as 'Administrator').
  
    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.
  
    Bugs are naturally mine. I'd be glad to hear about them. There are
    certainly word - size dependencies here.
  
    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.
  
    Original Version from Matthew Dixon Cowles:
      -> ftp://ftp.visi.com/users/mdc/ping.py
  
    Rewrite by Jens Diemer:
      -> http://www.python-forum.de/post-69122.html#69122
  
    Rewrite by George Notaras:
      -> http://www.g-loaded.eu/2009/10/30/python-ping/
  
    Enhancements by Martin Falatic:
      -> http://www.falatic.com/index.php/39/pinging-with-python
      
    Library rewrite for QT application by Josh Price
      -> https://github.com/RainDogSoftware/pingpung
  
    Revision history
    ~~~~~~~~~~~~~~~~
    February 2015
    --------------
    Large overhaul to turn this application into a library for PingPung
    https://github.com/RainDogSoftware/pingpung
    - Josh Price
  
    October 12, 2011
    --------------
    Merged updates from the main project
      -> https://github.com/jedie/python-ping
  
    September 12, 2011
    --------------
    Bugfixes + cleanup by Jens Diemer
    Tested with Ubuntu + Windows 7
  
    September 6, 2011
    --------------
    Cleanup by Martin Falatic. Restored lost comments and docs. Improved
    functionality: constant time between pings, internal times consistently
    use milliseconds. Clarified annotations (e.g., in the checksum routine).
    Using unsigned data in IP & ICMP header pack/unpack unless otherwise
    necessary. Signal handling. Ping-style output formatting and stats.
  
    August 3, 2011
    --------------
    Ported to py3k by Zach Ware. Mostly done by 2to3; also minor changes to
    deal with bytes vs. string changes (no more ord() in checksum() because
    >source_string< is actually bytes, added .encode() to data in
    send_one_ping()).  That's about it.
  
    March 11, 2010
    --------------
    changes by Samuel Stauffer:
    - replaced time.clock with default_timer which is set to
      time.clock on windows and time.time on other systems.
  
    November 8, 2009
    ----------------
    Improved compatibility with GNU/Linux systems.
  
    Fixes by:
     * George Notaras -- http://www.g-loaded.eu
    Reported by:
     * Chris Hallman -- http://cdhallman.blogspot.com
  
    Changes in this release:
     - Re-use time.time() instead of time.clock(). The 2007 implementation
       worked only under Microsoft Windows. Failed on GNU/Linux.
       time.clock() behaves differently under the two OSes[1].
  
    [1] http://docs.python.org/library/time.html#time.clock
  
    May 30, 2007
    ------------
    little rewrite by Jens Diemer:
     -  change socket asterisk import to a normal import
     -  replace time.time() with time.clock()
     -  delete "return None" (or change to "return" only)
     -  in checksum() rename "str" to "source_string"
  
    December 4, 2000
    ----------------
    Changed the struct.pack() calls to pack the checksum and ID as
    unsigned. My thanks to Jerome Poincheval for the fix.
  
    November 22, 1997
    -----------------
    Initial hack. Doesn't do much, but rather than try to guess
    what features I (or others) will want in the future, I've only
    put in what I need now.
  
    December 16, 1997
    -----------------
    For some reason, the checksum bytes are in the wrong order when
    this is run under Solaris 2.X for SPARC but it works right under
    Linux x86. Since I don't know just what's wrong, I'll swap the
    bytes always and then do an htons().
  
    ===========================================================================
    IP header info from RFC791
      -> http://tools.ietf.org/html/rfc791)
  
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |Version|  IHL  |Type of Service|          Total Length         |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |         Identification        |Flags|      Fragment Offset    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  Time to Live |    Protocol   |         Header Checksum       |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                       Source Address                          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Destination Address                        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options                    |    Padding    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  
    ===========================================================================
    ICMP Echo / Echo Reply Message header info from RFC792
      -> http://tools.ietf.org/html/rfc792
  
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |     Type      |     Code      |          Checksum             |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |           Identifier          |        Sequence Number        |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |     Data ...
        +-+-+-+-+-
  
    ===========================================================================
    ICMP parameter info:
      -> http://www.iana.org/assignments/icmp-parameters/icmp-parameters.xml
  
    ===========================================================================
    An example of ping's typical output:
  
    PING heise.de (193.99.144.80): 56 data bytes
    64 bytes from 193.99.144.80: icmp_seq=0 ttl=240 time=127 ms
    64 bytes from 193.99.144.80: icmp_seq=1 ttl=240 time=127 ms
    64 bytes from 193.99.144.80: icmp_seq=2 ttl=240 time=126 ms
    64 bytes from 193.99.144.80: icmp_seq=3 ttl=240 time=126 ms
    64 bytes from 193.99.144.80: icmp_seq=4 ttl=240 time=127 ms
  
    ----heise.de PING Statistics----
    5 packets transmitted, 5 packets received, 0.0% packet loss
    round-trip (ms)  min/avg/max/med = 126/127/127/127
  
    ===========================================================================
"""
  
#=============================================================================#
import sys
import socket
import struct
import select
import time
import datetime
import itertools


# This is how we manage multi-threading.  In addition to the sequence number, we include an identifier integer.  The
# cycling generator below is how we efficiently create that id.  It is used to match the sending tab to the appropriate
# reply.  This means we can theoretically support 65535 tabs all running a ping at the same time.
#
# Can't honestly say I've tested that though.
id_gen = itertools.cycle(range(0, 65536))

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time
  
#=============================================================================#
# ICMP parameters
  
ICMP_ECHOREPLY = 0  # Echo reply (per RFC792)
ICMP_ECHO = 8  # Echo request (per RFC792)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer
  
MAX_SLEEP = 1000
#=============================================================================#
# Exceptions


class SocketError(Exception):
    pass  
  

class AddressError(Exception):
    pass
#=============================================================================#


def checksum(source_string):
    """
    A port of the functionality of in_cksum() from ping.c
    Ideally this would act on the string as a series of 16-bit ints (host
    packed), but this works.
    Network data is big-endian, hosts are typically little-endian
    """
    count_to = (int(len(source_string)/2))*2
    _sum = 0
    count = 0

    while count < count_to:
        if sys.byteorder == "little":
            lo_byte = source_string[count]
            hi_byte = source_string[count + 1]
        else:
            lo_byte = source_string[count + 1]
            hi_byte = source_string[count]
        _sum += hi_byte * 256 + lo_byte
        count += 2
  
    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if count_to < len(source_string):  # Check for odd length
        lo_byte = source_string[len(source_string)-1]
        _sum += lo_byte
  
    _sum &= 0xffffffff  # Truncate _sum to 32 bits (a variance from ping.c, which
                      # uses signed ints, but overflow is unlikely in ping)
  
    _sum = (_sum >> 16) + (_sum & 0xffff)    # Add high 16 bits to low 16 bits
    _sum += (_sum >> 16)                    # Add carry from above (if any)
    answer = ~_sum & 0xffff              # Invert and truncate to 16 bits
    answer = socket.htons(answer)
  
    return answer
  

#=============================================================================#
def ping(dest_ip, timeout, seq_number, num_data_bytes):
    """
    Core pping function.
    """

    try:  # One could use UDP here
        this_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except socket.error:
        raise SocketError("Unable to create socket.  Verify app is running as root/admin.  \nSee README for details.")
  
    # To make "unique" socket IDs for safe threading.  
    # Each ping gets a socket ID number from a 1-65535 cycling iterator.
    socket_id = next(id_gen)
  
    try:
        sent_time = _send_one_ping(this_socket, dest_ip, socket_id, seq_number, num_data_bytes)
    except AddressError:
        raise

    recv_time, data_size, iph_src_ip, icmp_seq_number, iph_ttl = _receive_one_ping(this_socket, socket_id, timeout)
  
    this_socket.close()
    
    result = {}
    if recv_time:
        delay = (recv_time-sent_time)*1000
        
        result["Success"] = True
        result["Message"] = "Success"
    else:
        delay = None
        result["Success"] = False
        result["Message"] = "Request Timed Out"
        
    result["Responder"] = socket.inet_ntoa(struct.pack("!I", iph_src_ip))
    result["SeqNumber"] = icmp_seq_number
    result["Delay"] = delay
    result["PacketSize"] = num_data_bytes
    result["Timestamp"] = str(datetime.datetime.now()).split('.')[0]
  
    return result
  

#=============================================================================#
def _send_one_ping(this_socket, dest_ip, socket_id, seq_number, num_data_bytes):
    """
    Send one ping to the given >destIP<.
    """
    try:
        dest_ip = socket.gethostbyname(dest_ip)
    except socket.error:
        raise AddressError
  
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    packet_checksum = 0
  
    # Make a dummy heder with a 0 checksum.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, packet_checksum, socket_id, seq_number
    )
  
    pad_bytes = []
    start_value = 0x42
    for i in range(start_value, start_value + num_data_bytes):
        pad_bytes += [(i & 0xff)]  # Keep chars in the 0-255 range
    data = bytes(pad_bytes)
  
    # Calculate the checksum on the data and the dummy header.
    packet_checksum = checksum(header + data)  # Checksum is in network order
  
    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, packet_checksum, socket_id, seq_number
    )
  
    packet = header + data
    send_time = time.time()
    try:
        this_socket.sendto(packet, (dest_ip, 1))  # Port number is irrelevant for ICMP
    except socket.error:
        raise SocketError 
  
    return send_time
  

#=============================================================================#
def _receive_one_ping(this_socket, socket_id, timeout):
    """
    Receive the ping from the socket. Timeout = in ms
    """
    time_left = timeout/1000
  
    while True:  # Loop while waiting for packet or timeout
        started_select = time.time()
        what_ready = select.select([this_socket], [], [], time_left)
        how_long_in_select = (time.time() - started_select)
        #TODO:  Don't return crap data, throw exception
        if not what_ready[0]:  # Timeout
            return None, 0, 0, 0, 0
  
        time_received = time.time()
  
        rec_packet, addr = this_socket.recvfrom(ICMP_MAX_RECV)
  
        ip_header = rec_packet[:20]
        iph_version, iph_type_of_svc, iph_length, iph_id, iph_flags, iph_ttl, iph_protocol, \
        iph_checksum, iph_src_ip, iph_dest_ip = struct.unpack("!BBHHHBBHII", ip_header)
  
        icmp_header = rec_packet[20:28]
        icmp_type, icmp_code, icmp_checksum, icmp_packet_id, icmp_seq_number = struct.unpack("!BBHHH", icmp_header)
  
        if icmp_packet_id == socket_id:  # Our packet
            data_size = len(rec_packet) - 28
            return time_received, data_size, iph_src_ip, icmp_seq_number, iph_ttl
  
        time_left = time_left - how_long_in_select
        #TODO:  Don't return crap data, throw exception
        if time_left <= 0:
            return None, 0, 0, 0, 0