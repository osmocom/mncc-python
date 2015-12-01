#!/usr/bin/python

import os, sys
from twisted.python.log import startLogging
from twisted.python.filepath import FilePath
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory, BaseProtocol
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor

import mncc
import ctypes

class mncc_msg(mncc.gsm_mncc):
    def send(self):
        return buffer(self)[:]
    def receive(self, bytes):
        fit = min(len(bytes), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes, fit)

def mncc_number(number, num_type = 0, num_plan = 0, num_present = 1, num_screen = 0):
    return mncc.gsm_mncc_number(number = number, type = num_type,
                                plan = num_plan, present = num_present,
                                screen = num_screen)

class MnccProtocol(BaseProtocol):

    def __init__(self):
        self.whenDisconnected = Deferred()

    def dataReceived(self, data):
        print 'received "%s"' % data
        ms = mncc_msg()
        ms.receive(data)

    def connectionLost(self, reason):
        self.whenDisconnected.callback(None)


def main():
    address = FilePath('/tmp/bsc_mncc')
    startLogging(sys.stdout)

    factory = Factory()
    factory.protocol = MnccProtocol
    factory.quiet = True

    endpoint = UnixClientEndpoint(reactor, address.path)
    connected = endpoint.connect(factory)

    def succeded(client):
        print "succeeded"
        return client.whenDisconnected
    def failed(reason):
        print "Could not connect:", reason.getErrorMessage()
    def disconnected(ignored):
        print "disconnected"
        reactor.stop()

    connected.addCallbacks(succeeded, failed)
    connected.addCallback(disconnected)

    reactor.run()
