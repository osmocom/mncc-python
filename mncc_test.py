#!/usr/bin/env python2

# Python testing tool for establishing calls via the OsmoNITB MNCC
# interface.
#
# (C) 2015 by Harald Welte <laforge@gnumonks.org>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.


from gsm_call_fsm import GsmCallFsm, GsmCallConnector, GSM48
from mncc_sock import MnccSocket
from thread import start_new_thread
import pykka
import logging as log
import signal, sys, time
import readline, code
import time

# MnccActor provides an interface for GsmCallFsm to send MNCC messages
class MnccActor(pykka.ThreadingActor):
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

# MNCC receive thread, broadcasting received MNCC packets to GsmCallFsm
def mncc_rx_thread(mncc_sock):
    while 1:
        msg = mncc_sock.recv()
        if msg.is_frame():
            log.warning("Dropping traffic frame: %s" % msg)
            continue

        log.debug("MnccActor RxMNCC %s, broadcasting to Call FSMs" % msg)
        # we simply broadcast to all calls
        pykka.ActorRegistry.broadcast({'type': 'mncc', 'msg': msg}, GsmCallFsm)

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
start_new_thread(mncc_rx_thread, (mncc_sock,))

# convenience wrapper
def connect_call(msisdn_a, msisdn_b, rtp_bridge = True, codecs = GSM48.AllCodecs):
    call_conn = GsmCallConnector.start(mncc_act, rtp_bridge, codecs).proxy()
    call_conn.start_call_ab(msisdn_a, msisdn_b)
    return call_conn

def calls(nr, ramp=1.0):
    if (nr & 1):
        print('Only even numbers allowed, because each invocation has two call legs')
	return
    nr /= 2
    for i in range(nr):
	a = 90001 + 2*i
	b = a + 1
	a = str(a)
	b = str(b)
	print('%d: connect_call(%r, %r)' % (i, a, b))
	connect_call(a, b)
	time.sleep(ramp)

# start a first bogus call

log.info("")
log.info("")
log.info("Start calls by typing:")
log.info('    c = connect_call("90001", "90002")')
log.info('    c.release()')
log.info('or')
log.info('    calls(200)')
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
