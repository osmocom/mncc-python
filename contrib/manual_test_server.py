#!/usr/bin/env python2

import mncc
import mncc_sock
import ctypes
import socket

import logging as log

GSM340_PLAN_ISDN = 1
GSM340_TYPE_NATIONAL = 2

class MnccMessageBuilder(object):
    """
    I help in creating messages...
    """
    @staticmethod
    def build_hello():
        hello = mncc.gsm_mncc_hello()
        hello.msg_type = mncc.MNCC_SOCKET_HELLO
        hello.version = mncc.MNCC_SOCK_VERSION
        hello.mncc_size = ctypes.sizeof(mncc.gsm_mncc)
        hello.data_frame_size = ctypes.sizeof(mncc.gsm_data_frame)
        hello.called_offset = mncc.gsm_mncc.called.offset
        hello.signal_offset = mncc.gsm_mncc.signal.offset
        hello.emergency_offset = mncc.gsm_mncc.emergency.offset
        hello.lchan_type_offset = mncc.gsm_mncc.lchan_type.offset
        return hello

    @staticmethod
    def build_mncc_number(number):
        return mncc.gsm_mncc_number(
                type=GSM340_TYPE_NATIONAL,
                plan=GSM340_PLAN_ISDN,
                number=number)

    @staticmethod
    def build_setup_ind(calling, called, callref=1):
        setup = mncc.gsm_mncc()
        setup.msg_type = mncc.MNCC_SETUP_IND
        setup.callref = callref
        setup.fields = mncc.MNCC_F_CALLED | mncc.MNCC_F_CALLING
        setup.called = MnccMessageBuilder.build_mncc_number(called)
        setup.calling = MnccMessageBuilder.build_mncc_number(calling)
        return setup

    @staticmethod
    def build_setup_cmpl_ind(callref=1):
        setup = mncc.gsm_mncc()
        setup.msg_type = mncc.MNCC_SETUP_COMPL_IND
        setup.callref = callref
        return setup

    @staticmethod
    def build_rtp_msg(msg_type, callref, addr, port):
        return mncc.gsm_mncc_rtp(
                    msg_type=msg_type, callref=callref,
                    ip=addr, port=port,
                    #payload_type=3,
                    #payload_msg_type=mncc.GSM_TCHF_FRAME)
                    payload_type=98,
                    payload_msg_type=mncc.GSM_TCH_FRAME_AMR)

    @staticmethod
    def build_dtmf_start(callref, data):
        return mncc.gsm_mncc(
                    msg_type=mncc.MNCC_START_DTMF_IND,
                    callref=callref,
                    fields=mncc.MNCC_F_KEYPAD,
                    keypad=ord(data))

    @staticmethod
    def build_dtmf_stop(callref, data):
        return mncc.gsm_mncc(
                    callref=callref,
                    msg_type=mncc.MNCC_STOP_DTMF_IND)

def send_dtmf(callref):
    global conn

    conn.send_msg(MnccMessageBuilder.build_dtmf_start(callref, '1'))
    conn.send_msg(MnccMessageBuilder.build_dtmf_stop(callref, '1'))
    conn.send_msg(MnccMessageBuilder.build_dtmf_start(callref, '2'))
    conn.send_msg(MnccMessageBuilder.build_dtmf_stop(callref, '2'))


log.basicConfig(level = log.DEBUG,
    format = "%(levelname)s %(filename)s:%(lineno)d %(message)s")

server = mncc_sock.MnccSocketServer()
conn = server.accept()

# Say hello and set-up a call
conn.send_msg(MnccMessageBuilder.build_hello())
conn.send_msg(MnccMessageBuilder.build_setup_ind("1234", "5000"))
log.info("=> Sent hello + setup indication")

# Wait for the RTP crate.. and actknowledge it..
msg = conn.recv()
assert msg.msg_type == mncc.MNCC_RTP_CREATE
log.info("<= Received request to create a RTP socket")
conn.send_msg(MnccMessageBuilder.build_rtp_msg(mncc.MNCC_RTP_CREATE,
                                                msg.callref,
                                                #socket.INADDR_LOOPBACK, 4000))
                                                socket.INADDR_ANY, 4000))
log.info("=> Claimed socket was created...")

msg = conn.recv()
assert msg.msg_type == mncc.MNCC_CALL_PROC_REQ
log.info("<= Received proceeding...")



while True:
    msg = conn.recv()
    if msg.msg_type == mncc.MNCC_ALERT_REQ:
        log.info("=> I should alert...")
        continue
    if msg.msg_type == mncc.MNCC_RTP_CONNECT:
        conn.send_msg(MnccMessageBuilder.build_rtp_msg(mncc.MNCC_RTP_CONNECT,
                                                msg.callref,
                                                socket.INADDR_LOOPBACK, 4000))
        log.info("=> I needed to connect RTP...")
        continue
    if msg.msg_type == mncc.MNCC_SETUP_RSP:
        log.info("=> Call is connected?")
        conn.send_msg(MnccMessageBuilder.build_setup_cmpl_ind(msg.callref))
        send_dtmf(msg.callref)
        continue

    log.debug(msg)
