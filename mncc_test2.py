#!/usr/bin/python

from gsm_call_fsm import GsmCallFsm
from mncc_sock import MnccSocket
import pykka
import logging
import signal
import sys

class MnccActor(pykka.ThreadingActor):
    def __init__(self, mncc_sock):
        super(MnccActor, self).__init__()
        self.mncc_sock = mncc_sock

    def on_receive(self, message):
        print 'MnccActor Received %s' % message
        if message['type'] == 'send':
            mncc_sock.send(message['msg'])


def sigint_handler(signum, frame):
    pykka.ActorRegistry.stop_all()
    sys.exit(0)

logging.basicConfig(level=logging.DEBUG)

signal.signal(signal.SIGINT, sigint_handler)

mncc_sock = MnccSocket()
mncc_act = MnccActor.start(mncc_sock)

call_proxy = GsmCallFsm.start('foo', mncc_act).proxy()
call_proxy.start_mt_call("1234", "6789")

while 1:
    msg = mncc_sock.recv()
    print "Received %s from MNCC, broadcasting to Call FSMs" % msg
    # FIXME: we simply broadcast to all calls
    pykka.ActorRegistry.broadcast({'type': 'mncc', 'msg': msg}, GsmCallFsm)
    #pykka.ActorRegistry.broadcast({'type': 'mncc', 'msg': msg})
