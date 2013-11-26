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
    November 2013
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
import sys, socket, struct, select, time
import datetime
import itertools

id_gen = itertools.cycle(range(0,65535))

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time
  
#=============================================================================#
# ICMP parameters
  
ICMP_ECHOREPLY  =    0 # Echo reply (per RFC792)
ICMP_ECHO       =    8 # Echo request (per RFC792)
ICMP_MAX_RECV   = 2048 # Max size of incoming buffer
  
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
    countTo = (int(len(source_string)/2))*2
    _sum = 0
    count = 0

    while count < countTo:
        if sys.byteorder == "little":
            loByte = source_string[count]
            hiByte = source_string[count + 1]
        else:
            loByte = source_string[count + 1]
            hiByte = source_string[count]
        _sum += hiByte * 256 + loByte
        count += 2
  
    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if countTo < len(source_string): # Check for odd length
        loByte = source_string[len(source_string)-1]
        _sum += loByte
  
    _sum &= 0xffffffff # Truncate _sum to 32 bits (a variance from ping.c, which
                      # uses signed ints, but overflow is unlikely in ping)
  
    _sum = (_sum >> 16) + (_sum & 0xffff)    # Add high 16 bits to low 16 bits
    _sum += (_sum >> 16)                    # Add carry from above (if any)
    answer = ~_sum & 0xffff              # Invert and truncate to 16 bits
    answer = socket.htons(answer)
  
    return answer
  
#=============================================================================#
def ping(destIP, timeout, mySeqNumber, numDataBytes):
    """
    Core pypinglib function.  
    """

    delay = None
  
    try: # One could use UDP here, but it's obscure
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except socket.error:
        raise SocketError
  
    # To make "unique" socket IDs for safe threading.  
    # Each ping gets a socket ID number from a 1-65535 cycling iterator.  
    # Theoretically, this means that it can support over 65000 simultaneous pings
    # without worrying about a socket ID clash
    socketID = next(id_gen)
  
    try:
        sentTime = _send_one_ping(mySocket, destIP, socketID, mySeqNumber, numDataBytes)
    except AddressError:
        raise

    recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL = _receive_one_ping(mySocket, socketID, timeout)
  
    mySocket.close()
    
    result = {}
    if recvTime:
        delay = (recvTime-sentTime)*1000     
        
        result["Success"] = True
        result["Message"] = "Success"
    else:
        delay = None
        result["Success"] = False
        result["Message"] = "Request Timed Out"
        
    result["Responder"] = socket.inet_ntoa(struct.pack("!I", iphSrcIP))
    result["SeqNumber"] = icmpSeqNumber
    result["Delay"] = delay
    result["Timestamp"] = str(datetime.datetime.now()).split('.')[0]
  
    return result
  
#=============================================================================#
def _send_one_ping(mySocket, destIP, socketID, mySeqNumber, numDataBytes):
    """
    Send one ping to the given >destIP<.
    """
    try:
        destIP  =  socket.gethostbyname(destIP)
    except socket.error:
        raise AddressError
  
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
  
    # Make a dummy heder with a 0 checksum.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, myChecksum, socketID, mySeqNumber
    )
  
    padBytes = []
    startVal = 0x42
    for i in range(startVal, startVal + numDataBytes):
        padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
    data = bytes(padBytes)
  
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data) # Checksum is in network order
  
    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, myChecksum, socketID, mySeqNumber
    )
  
    packet = header + data
  
    sendTime = time.time()
  
    try:
        mySocket.sendto(packet, (destIP, 1)) # Port number is irrelevant for ICMP
    except socket.error as e:
        raise SocketError 
  
    return sendTime
  
#=============================================================================#
def _receive_one_ping(mySocket, socketID, timeout):
    """
    Receive the ping from the socket. Timeout = in ms
    """
    timeLeft = timeout/1000
  
    while True: # Loop while waiting for packet or timeout
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        #TODO:  Don't return crap data, throw exception
        if not whatReady[0]: # Timeout
            return None, 0, 0, 0, 0
  
        timeReceived = time.time()
  
        recPacket, addr = mySocket.recvfrom(ICMP_MAX_RECV)
  
        ipHeader = recPacket[:20]
        iphVersion, iphTypeOfSvc, iphLength, \
        iphID, iphFlags, iphTTL, iphProtocol, \
        iphChecksum, iphSrcIP, iphDestIP = struct.unpack(
            "!BBHHHBBHII", ipHeader
        )
  
        icmpHeader = recPacket[20:28]
        icmpType, icmpCode, icmpChecksum, \
        icmpPacketID, icmpSeqNumber = struct.unpack(
            "!BBHHH", icmpHeader
        )
  
        if icmpPacketID == socketID: # Our packet
            dataSize = len(recPacket) - 28
            return timeReceived, dataSize, iphSrcIP, icmpSeqNumber, iphTTL
  
        timeLeft = timeLeft - howLongInSelect
        #TODO:  Don't return crap data, throw exception
        if timeLeft <= 0:
            return None, 0, 0, 0, 0
  

  

  

 