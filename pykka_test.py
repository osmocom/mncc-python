#!/usr/bin/python

import pykka

class Greeter(pykka.ThreadingActor):
    def on_receive(self, message):
        print('Hi there, you sent %s' % message)

actor_ref = Greeter.start()

actor_ref.tell({'msg': 'Hi!'})

actor_ref.stop()
