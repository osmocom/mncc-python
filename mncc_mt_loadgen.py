#!/usr/bin/env python3

# Python testing tool for establishing mobile-terminated calls using
# the OsmoMSC MNCC interface.  It wants to communicate via CTRL with a
# 'rtpsoucre' program which will take care of generating RtP flows
# for the MT calls that are established.
#
# (C) 2015, 2020 by Harald Welte <laforge@gnumonks.org>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.

RTPSOURCE_CTRL_IP = "127.0.0.1"
RTPSOURCE_CTRL_PORT = 11111


from gsm_call_fsm import GsmCallFsm, GSM48
from mncc_sock import MnccSocket
from ctrl import OsmoCtrlSimple
import threading
import pykka
import logging as log
import signal, sys, time
import readline, code
import socket
import struct
import mncc
from mncc_sock import mncc_rtp_msg

def int2ipstr(addr):
    '''Convert from an integer to a strinf-formatted IPv4 address'''
    return socket.inet_ntoa(struct.pack("!I", addr))

def ipstr2int(addr):
    '''Convert from a string-formatted IPv4 address to integer'''
    return struct.unpack("!I", socket.inet_aton(addr))[0]


class MnccActor(pykka.ThreadingActor):
    '''MnccActor provides an interface for GsmCallFsm to send MNCC messages'''
    def __init__(self, mncc_sock):
        super(MnccActor, self).__init__()
        self.mncc_sock = mncc_sock

    def on_receive(self, message):
        if message['type'] == 'send':
            msg = message['msg']
            log.debug('MnccActor TxMNCC %s' % msg)
            mncc_sock.send(msg)
        else:
            raise Exception('mncc', 'MnccActor Received unhandled %s' % message)

def mncc_rx_thread(mncc_sock):
    '''MNCC receive thread, broadcasting received MNCC packets to GsmCallFsm'''
    while 1:
        msg = mncc_sock.recv()
        if msg == None:
            raise Exception('mncc', 'MnccSocket disconnected')

        if msg.is_frame():
            log.warning("Dropping traffic frame: %s" % msg)
            continue

        log.debug("MnccActor RxMNCC %s, broadcasting to Call FSMs" % msg)
        # we simply broadcast to all calls
        pykka.ActorRegistry.broadcast({'type': 'mncc', 'msg': msg}, GsmCallFsm)


class RtpSourceCtrlActor(pykka.ThreadingActor):
    '''Actor for talking with the rtpsource program via an osmocom CTRL interface'''
    def __init__(self, ctrl_host, ctrl_port=11111):
        super(RtpSourceCtrlActor, self).__init__()
        self.ctrl = OsmoCtrlSimple(ctrl_host, ctrl_port)
        self.ctrl.connect()

    def _set_var(self, var, val):
        (res, var, val) = self.ctrl.do_set_get(var, val)
        log.debug('RtpSourceCtrlActor result=%s var=%s val=%s' % (res, var, val))
        return (res, var, val)

    def on_receive(self, message):
        if message['type'] == 'rtp_create':
            val = '%s,%s' % (message['cname'], message['codec'])
            (res, var, val) = self._set_var('rtp_create', val)
            v = val.split(',') # input looks like '1,127.23.23.23,37723'
            return {'cname': v[0], 'remote_host': v[1], 'remote_port': int(v[2])}
        elif message['type'] == 'rtp_connect':
            val = '%s,%s,%u,%u' % (message['cname'], message['remote_host'],
                                   message['remote_port'], message['payload_type'])
            (res, var, val) = self._set_var('rtp_connect', val)
            return res
        elif message['type'] == 'rtp_delete':
            (res, var, val) = self._set_var('rtp_delete', message['cname'])
            return res
        else:
            raise Exception('ctrl', 'RtpSourceCtrlActor Received unhandled %s' % message)


class MTCallRtpsource(pykka.ThreadingActor):
    '''Actor to start a network-initiated MT (mobile terminated) call to a given MSISDN,
       connecting the RTP flow to an extenal rtpsource program'''
    def __init__(self, mncc_act, ctrl_act, codecs_permitted = GSM48.AllCodecs):
        super(MTCallRtpsource, self).__init__()
        self.mncc_act = mncc_act
        self.ctrl_act = ctrl_act
        self.codecs_permitted = codecs_permitted
        self.call = GsmCallFsm.start(self.mncc_act, self.actor_ref, False, self.codecs_permitted)
        self.callref = self.call.ask({'type':'get_callref'})
        self.state = 'NULL'
        self.rtp_msc = None

    def start_call(self, msisdn_called, msisdn_calling, codec):
        '''Start a MT call from given [external] calling party to given mobile party MSISDN'''
        self.msisdn_called = msisdn_called
        self.msisdn_calling = msisdn_calling
        # allocate a RTP connection @ rtpsource
        r = self.ctrl_act.ask({'type':'rtp_create', 'cname':self.callref, 'codec':codec})
        self.ext_rtp_host = r['remote_host']
        self.ext_rtp_port = r['remote_port']
        # start the MNCC call FSM
        self.call.tell({'type':'start_mt_call',
                        'calling':self.msisdn_calling, 'called':self.msisdn_called})

    def release(self):
        self.call.tell({'type':'release'})

    def on_stop(self):
        # Attempt to do a graceful shutdown by deleting the RTP connection from rtpsource
        self.ctrl_act.ask({'type':'rtp_delete', 'cname':self.callref})
        self.call.stop()

    def on_failure(self, exception_type, exception_value, traceback):
        # on_stop() is not called in case of failure; fix that
        self.on_stop()

    def on_receive(self, message):
        if message['type'] == 'rtp_create_ind':
            # MSC+MGW informs us of the PLMN side IP/port
            mncc_rtp_ind = message['rtp']
            # tell external rtpsourc to connect to this address
            r = self.ctrl_act.ask({'type':'rtp_connect', 'cname':self.callref,
                                   'remote_host': int2ipstr(mncc_rtp_ind.ip),
                                   'remote_port': mncc_rtp_ind.port,
                                   'payload_type':3})
            # tell MSC to connect to ip/port @ rtpsource
            mncc_rtp_conn = mncc_rtp_msg(msg_type=mncc.MNCC_RTP_CONNECT, callref=self.callref,
                                         ip=ipstr2int(self.ext_rtp_host), port=self.ext_rtp_port)
            self.mncc_act.tell({'type': 'send', 'msg': mncc_rtp_conn})
        elif message['type'] == 'call_state_change':
            if message['new_state'] == 'NULL':
                # Call FSM has reached the NULL state again (call terminated)
                # on_stop() will clean up the RTP connection at rtpsource
                self.stop()


# capture SIGINT (Ctrl+C) and stop all actors
def sigint_handler(signum, frame):
    pykka.ActorRegistry.stop_all()
    sys.exit(0)

log.basicConfig(level = log.DEBUG,
    format = "%(levelname)s %(filename)s:%(lineno)d %(message)s")

signal.signal(signal.SIGINT, sigint_handler)

# start the MnccSocket and associated pykka actor + rx thread
mncc_sock = MnccSocket()
mncc_act = MnccActor.start(mncc_sock)
rx_t = threading.Thread(target=mncc_rx_thread, args=(mncc_sock,))
rx_t.start()

# connect via CTRL to rtpsource
rtpctrl_act = RtpSourceCtrlActor.start(RTPSOURCE_CTRL_IP, RTPSOURCE_CTRL_PORT)

# convenience wrapper
def mt_call(msisdn_called, msisdn_calling='123456789', codecs=GSM48.AllCodecs, codec='GSM_FR'):
    call_conn = MTCallRtpsource.start(mncc_act, rtpctrl_act, codecs).proxy()
    call_conn.start_call(msisdn_called, msisdn_calling, codec)
    return call_conn

def calls(nr, ramp=1.0, codec='GSM_FR'):
    for i in range(nr):
        a = 90001 + i
        a = str(a)
        print("%d: mt_call(%r)" % (i, a))
        mt_call(a, codec=codec)
        time.sleep(ramp)

log.info("")
log.info("")
log.info("Start a single call by typing:")
log.info("    mt_call('90001')")
log.info("With a specific codec (default is 'GSM_FR'):")
log.info("    mt_call('90001', codec='GSM_EFR')")
log.info("Start multiple calls with (e.g. 4 calls with EFR):")
log.info("    calls(4, codec='GSM_EFR')")
log.info("")
log.info("")

# start a shell to enable the user to add more calls as needed
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
try:
    shell.interact()
except SystemExit:
    pass
# clan up after user leaves interactive shell
sigint_handler(signal.SIGINT, None)
