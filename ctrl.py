# Simple class for synchronous/blocking interface with a remote
# Osmocom program via the CTRL interface

# (C) 2020 by Harald Welte <laforge@gnumonks.org>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.

from osmopy.osmo_ipa import Ctrl
import socket

class OsmoCtrlSimple:
    '''Simple class for synchronous/blocking interface with a remote
       Osmocom program via the CTRL interface'''
    remote_host = "127.0.0.1"
    remote_port = 0
    sock = None

    def __init__(self, host=None, port=None):
        self.remote_host = host
        self.remote_port = port

    def connect(self, host=None, port=None):
        if host:
            self.remote_host = host
        if port:
            self.remote_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.sock.connect((self.remote_host, self.remote_port))
        return self.sock

    def disconnect(self):
        self.sock.close()
        self.sock = None

    def _leftovers(self, fl):
        """
        Read outstanding data if any according to flags
        """
        try:
                data = self.sock.recv(1024, fl)
        except socket.error as _:
                return False
        if len(data) != 0:
                tail = data
                while True:
                        (head, tail) = Ctrl().split_combined(tail)
                        print("Got message:", Ctrl().rem_header(head))
                        if len(tail) == 0:
                                break
                return True
        return False

    def do_set_get(self, var, value = None):
        self._leftovers(socket.MSG_DONTWAIT)
        (r, c) = Ctrl().cmd(var, value)
        self.sock.send(c)
        while True:
                ret = self.sock.recv(4096)
                # handle multiple messages, ignore TRAPs
                ret = Ctrl().skip_traps(ret)
                if ret != None:
                    (i, k, v) = Ctrl().parse(ret)
                    break;
        return (Ctrl().rem_header(ret),) + Ctrl().verify(ret, r, var, value)

    def set_var(self, var, val):
        (a, _, _) = self.do_set_get(var, val)
        return a
