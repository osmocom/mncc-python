#!/usr/bin/python

# Python interface to OsmoNITB MNCC (Mobile Network Call Control)
# interface
#
# (C) 2015 by Harald Welte <laforge@gnumonks.org>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.

import socket
import sys
import os
import mncc
import ctypes

class mncc_msg(mncc.gsm_mncc):
    def send(self):
        return buffer(self)[:]
    def receive(self, bytes):
        fit = min(len(bytes), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes, fit)
    def __str__(self):
        return 'mncc_msg(type=0x%04x, callref=%u, fields=0x%04x)' % (self.msg_type, self.callref, self.fields)
    def __unicode__(self):
        return u'mncc_msg(type=0x%04x, callref=%u, fields=0x%04x)' % (self.msg_type, self.callref, self.fields)

class mncc_rtp_msg(mncc.gsm_mncc_rtp):
    def send(self):
        return buffer(self)[:]
    def receive(self, bytes):
        fit = min(len(bytes), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes, fit)
    def __str__(self):
        return 'mncc_rtp_msg(type=0x%04x, callref=%u, ip=%x, port=%u)' % (self.msg_type, self.callref, self.ip, self.port)
    def __unicode__(self):
        return u'mncc_rtp_msg(type=0x%04x, callref=%u, ip=%x, port=%u)' % (self.msg_type, self.callref, self.ip, self.port)

class mncc_bridge_msg(mncc.gsm_mncc_bridge):
    def send(self):
        return buffer(self)[:]
    def receive(self, bytes):
        fit = min(len(bytes), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes, fit)
    def __str__(self):
        return 'mncc_bridge_msg(%u, %u)' % (self.callref[0], self.callref[1])
    def __unicode__(self):
        return u'mncc_bridge_msg(%u, %u)' % (self.callref[0], self.callref[1])

def mncc_number(number, num_type = 0, num_plan = 0, num_present = 1, num_screen = 0):
    return mncc.gsm_mncc_number(number = number, type = num_type,
                                plan = num_plan, present = num_present,
                                screen = num_screen)

class MnccSocket(object):
    def __init__(self, address = '/tmp/bsc_mncc'):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        print 'connecting to %s' % address
        try:
            self.sock.connect(address)
        except socket.error, errmsg:
            print >>sys.stderr, errmsg
            sys.exit(1)

        # FIXME: parse the HELLO message
        msg = self.recv()

    def send(self, msg):
        return self.sock.sendall(msg.send())

    def recv(self):
        data = self.sock.recv(1500)
        ms = mncc_msg()
        ms.receive(data)
        if ms.msg_type == mncc.MNCC_RTP_CREATE or ms.msg_type == mncc.MNCC_RTP_CONNECT or ms.msg_type == mncc.MNCC_RTP_FREE:
               ms = mncc_rtp_msg()
               ms.receive(data)
        return ms
