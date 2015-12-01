#!/usr/bin/python

from gsm_call_fsm import GsmCallFsm
from mncc_sock import MnccSocket

mncc_sock = MnccSocket()

call = GsmCallFsm('foo', mncc_sock)
#call.fsm.mncc_setup_req()
call.start_mt_call("1234", "6789")

while 1:
    msg = mncc_sock.recv()
    # FIXME: look-up the call based on msg.callref
    call.handle_mncc(msg)
