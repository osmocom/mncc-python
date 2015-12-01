#!/usr/bin/python

from gsm_call_fsm import GsmCallFsm, GsmCallConnector
from mncc_sock import MnccSocket
from thread import start_new_thread
import pykka
import logging
import signal, sys
import readline, code

# MnccActor provides an interface for GsmCallFsm to send MNCC messages
class MnccActor(pykka.ThreadingActor):
    def __init__(self, mncc_sock):
        super(MnccActor, self).__init__()
        self.mncc_sock = mncc_sock

    def on_receive(self, message):
        print 'MnccActor Received %s' % message
        if message['type'] == 'send':
            mncc_sock.send(message['msg'])

# MNCC receive thread, broadcasting received MNCC packets to GsmCallFsm
def mncc_rx_thread(mncc_sock):
    while 1:
        msg = mncc_sock.recv()
        print "Received %s from MNCC, broadcasting to Call FSMs" % msg
        # we simply broadcast to all calls
        pykka.ActorRegistry.broadcast({'type': 'mncc', 'msg': msg}, GsmCallFsm)

# capture SIGINT (Ctrl+C) and stop all actors
def sigint_handler(signum, frame):
    pykka.ActorRegistry.stop_all()
    sys.exit(0)

logging.basicConfig(level=logging.DEBUG)

signal.signal(signal.SIGINT, sigint_handler)

# start the MnccSocket and associated pykka actor + rx thread
mncc_sock = MnccSocket()
mncc_act = MnccActor.start(mncc_sock)
start_new_thread(mncc_rx_thread, (mncc_sock,))

# start a first bogus call
call_conn = GsmCallConnector.start(mncc_act).proxy()
call_conn.start_call_ab("1234", "6789")

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
