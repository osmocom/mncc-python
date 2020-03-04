#!/usr/bin/env python2

# Python interface to OsmoNITB MNCC (Mobile Network Call Control)
# interface
#
# (C) 2015 by Harald Welte <laforge@gnumonks.org>
# (C) 2018 by Vadim Yanitskiy <axilirator@gmail.com>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.

import logging as log
import socket
import os
import mncc
import ctypes

class mncc_msg_common:
    def send(self):
        return buffer(self)[:] + bytes('\0')
    def receive(self, bytes):
        fit = min(len(bytes), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes, fit)

    # Message type matching
    def is_rtp(self):
        return self.msg_type in (mncc.MNCC_RTP_CREATE,
            mncc.MNCC_RTP_CONNECT, mncc.MNCC_RTP_FREE)
    def is_frame(self):
        return self.msg_type in (mncc.GSM_TCHF_FRAME,
            mncc.GSM_TCHH_FRAME, mncc.GSM_TCHF_FRAME_EFR,
            mncc.GSM_TCH_FRAME_AMR, mncc.GSM_BAD_FRAME)

class mncc_msg(mncc.gsm_mncc, mncc_msg_common):
    def __str__(self):
        return 'mncc_msg(type=0x%04x, callref=%u, fields=0x%04x)' % (self.msg_type, self.callref, self.fields)
    def __unicode__(self):
        return u'mncc_msg(type=0x%04x, callref=%u, fields=0x%04x)' % (self.msg_type, self.callref, self.fields)

class mncc_hello_msg(mncc.gsm_mncc_hello, mncc_msg_common):
    def __str__(self):
        return 'mncc_hello_msg(version=0x%04x)' % (self.version)
    def __unicode__(self):
        return u'mncc_hello_msg(version=0x%04x)' % (self.version)

class mncc_data_frame_msg(mncc.gsm_data_frame, mncc_msg_common):
    def __str__(self):
        return 'mncc_data_frame(type=0x%04x, codec=%s, callref=%u)' \
            % (self.msg_type, self.codec_str(), self.callref)
    def __unicode__(self):
        return u'mncc_data_frame(type=0x%04x, codec=%s, callref=%u)' \
            % (self.msg_type, self.codec_str(), self.callref)

    def codec_str(self):
        if self.msg_type == mncc.GSM_TCHF_FRAME:
            return "FR"
        elif self.msg_type == mncc.GSM_TCHH_FRAME:
            return "HR"
        elif self.msg_type == mncc.GSM_TCHF_FRAME_EFR:
            return "EFR"
        elif self.msg_type == mncc.GSM_TCH_FRAME_AMR:
            return "AMR"
        elif self.msg_type == mncc.GSM_BAD_FRAME:
            return "(BFI)"
        else:
            return "(???)"

class mncc_rtp_msg(mncc.gsm_mncc_rtp, mncc_msg_common):
    def __str__(self):
        return 'mncc_rtp_msg(type=0x%04x, callref=%u, ip=%x, port=%u)' % (self.msg_type, self.callref, self.ip, self.port)
    def __unicode__(self):
        return u'mncc_rtp_msg(type=0x%04x, callref=%u, ip=%x, port=%u)' % (self.msg_type, self.callref, self.ip, self.port)

class mncc_bridge_msg(mncc.gsm_mncc_bridge, mncc_msg_common):
    def __str__(self):
        return 'mncc_bridge_msg(%u, %u)' % (self.callref[0], self.callref[1])
    def __unicode__(self):
        return u'mncc_bridge_msg(%u, %u)' % (self.callref[0], self.callref[1])

def mncc_number(number, num_type = 0, num_plan = 0, num_present = 1, num_screen = 0):
    return mncc.gsm_mncc_number(number = number, type = num_type,
                                plan = num_plan, present = num_present,
                                screen = num_screen)

def mncc_bearer_cap(codecs_permitted):
    speech_ver = ctypes.c_int * 8
    speech_types = speech_ver()
    index = 0

    for codec in codecs_permitted:
        speech_types[index] = codec
        index = index + 1

    speech_types[index] = -1
    return mncc.gsm_mncc_bearer_cap(coding = 0, speech_ctm=0, radio = 1, speech_ver = speech_types, transfer = 0, mode = 0)

class MnccSocketBase(object):
    def send(self, msg):
        return self.sock.sendall(msg.send())

    def send_msg(self, msg):
        data = buffer(msg)[:]
        return self.sock.sendall(data)

    def recv(self):
        data = self.sock.recv(1500)
        ms = mncc_msg()
        ms.receive(data)
        if ms.is_rtp():
               ms = mncc_rtp_msg()
               ms.receive(data)
        elif ms.is_frame():
               ms = mncc_data_frame_msg()
               ms.receive(data)
        elif ms.msg_type == mncc.MNCC_SOCKET_HELLO:
               ms = mncc_hello_msg()
               ms.receive(data)
        return ms

class MnccSocket(MnccSocketBase):
    def __init__(self, address = '/tmp/bsc_mncc'):
        super(MnccSocketBase, self).__init__()
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        log.info('Connecting to %s' % address)
        self.sock.connect(address)

        # Check the HELLO message
        self.check_hello()

    def check_hello(self):
        log.debug('Waiting for HELLO message...')
        msg = self.recv()

        # Match expected message type
        if msg.msg_type != mncc.MNCC_SOCKET_HELLO:
            raise AssertionError('Received an unknown (!= MNCC_SOCKET_HELLO) '
                'message: %s\n' % msg)

        # Match expected protocol version
        if msg.version != mncc.MNCC_SOCK_VERSION:
            raise AssertionError('MNCC protocol version mismatch '
                '(0x%04x vs 0x%04x)\n' % (msg.version, mncc.MNCC_SOCK_VERSION))

        # Match expected message sizes / offsets
        if (msg.mncc_size < ctypes.sizeof(mncc.gsm_mncc) or
            msg.data_frame_size != ctypes.sizeof(mncc.gsm_data_frame) or
            msg.called_offset != mncc.gsm_mncc.called.offset or
            msg.signal_offset != mncc.gsm_mncc.signal.offset or
            msg.emergency_offset != mncc.gsm_mncc.emergency.offset or
            msg.lchan_type_offset != mncc.gsm_mncc.lchan_type.offset):
                raise AssertionError('MNCC message alignment mismatch\n')

        log.info('Received %s' % msg)

class MnccSocketServer(object):
    def __init__(self, address = '/tmp/bsc_mncc'):
        os.unlink(address)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.bind(address)
        self.sock.listen(5)

    def accept(self):
        (fd,_) = self.sock.accept()
        sock = MnccSocketBase()
        sock.sock = fd
        return sock
