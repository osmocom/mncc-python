#!/usr/bin/python

import mncc
import ctypes
import pykka

from fysom import Fysom
from mncc_sock import mncc_msg, mncc_number

class GsmCallFsm(pykka.ThreadingActor):
    last_callref = 0

    def _get_next_callref(self):
        GsmCallFsm.last_callref = GsmCallFsm.last_callref + 1
        return GsmCallFsm.last_callref;

    def _printstatechange(self, e):
        print 'GsmCallFsm(%u/%s): event: %s, %s -> %s' % (self.callref, self.called, e.event, e.src, e.dst)
        if self.ctrl_ref != None:
            self.ctrl_ref.tell({'type':'call_state_change', 'called':self.called, 'old_state':e.src, 'new_state':e.dst})

    def _onmncc_setup_req(self, e):
        msg = mncc_msg(msg_type = mncc.MNCC_SETUP_REQ, callref = self.callref,
                       fields = mncc.MNCC_F_CALLED | mncc.MNCC_F_CALLING,
                       calling = mncc_number(self.calling),
                       called = mncc_number(self.called))
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def _onmncc_setup_cnf(self, e):
        # send MNCC_SETUP_COMPL_REQ to MNCC interface, causing
        # CC-CONNECT-ACK to be sent to MS
        msg = mncc_msg(msg_type = mncc.MNCC_SETUP_COMPL_REQ, callref = self.callref)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def _onmncc_disc_ind(self, e):
        # send MNCC_RELEASE_REQ
        msg = mncc_msg(msg_type = mncc.MNCC_REL_REQ, callref = self.callref)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def _onenter_NULL(self, e):
        if e.event != 'startup':
            self.stop()

    def __init__(self, mncc_ref, ctrl_ref = None):
        super(GsmCallFsm, self).__init__()
        self.mncc_ref = mncc_ref;
        self.callref = self._get_next_callref()
        self.ctrl_ref = ctrl_ref
        self.fsm = Fysom(initial = 'NULL',
            events = [
                # MT call setup
                    ('mncc_setup_req', 'NULL', 'CALL_PRESENT'),
                    ('mncc_rel_ind', 'CALL_PRESENT', 'NULL'),
                    ('mncc_call_conf_ind', 'CALL_PRESENT', 'MT_CALL_CONFIRMED'),
                    ('mncc_alert_ind', 'MT_CALL_CONFIRMED', 'CALL_RECEIVED'),
                    ('mncc_setup_cnf', 'CALL_RECEIVED', 'CONNECT_REQUEST'),
                    ('mncc_setup_cnf', 'MT_CALL_CONFIRMED', 'CONNECT_REQUEST'),
                    ('mncc_setup_compl_req', 'CONNECT_REQUEST', 'ACTIVE'),

                # MO call setup
                    # SETUP INDICATION (MS->MNCC)
                    ('mncc_setup_ind', 'NULL', 'CALL_INIT'),
                    # CALL PROCEEDING REQ (MNCC->MS)
                    ('mncc_call_proc_req', 'CALL_INIT', 'MO_CALL_PROC'),
                    # SETUP RESPONSE (MS->MNCC)
                    ('mncc_setup_resp', 'MO_CALL_PROC', 'CONNECT_INDICATION'),
                    # ALERT REQ (MNCC->MS)
                    ('mncc_alert_req', 'MO_CALL_PROC', 'CALL_DELIVERED'),
                    # SETUP RESPONSE (MS->MNCC)
                    ('mncc_setup_resp', 'CALL_DELIVERED', 'CONNECT_INDICATION'),
                    # PROGRESS REQ (MNCC->MS)
                    ('mncc_progress_req', 'MO_CALL_PROC', 'MO_CALL_PROC'),
                    # SETUP COMPL IND (MS->MNCC)
                    ('mncc_setup_compl_ind', 'CONNECT_INDICATION', 'ACTIVE'),

                    ('mncc_disc_ind', ['CALL_INIT', 'MO_CALL_PROC',
                                       'CALL_RECEIVED', 'CONNECT_REQUEST',
                                       'MT_CALL_CONFIRMED', 'ACTIVE',
                                        'CONNECT_INDICATION'], 'RELEASE_REQUEST'),

                    ('mncc_disc_req', ['CALL_INIT', 'MO_CALL_PROC',
                                       'CALL_RECEIVED', 'CONNECT_REQUEST',
                                       'MT_CALL_CONFIRMED', 'ACTIVE',
                                        'CONNECT_INDICATION'], 'DISCONNECT_INDICATION'),

                    ('mncc_rel_ind', '*', 'NULL'),
                    ('mncc_disc_ind', 'DISCONNECT_INDICATION', 'RELEASE_REQUEST'),

                    ('mncc_rel_cnf', 'RELEASE_REQUEST', 'NULL')
                    ],
            callbacks = [('onmncc_setup_req', self._onmncc_setup_req),
                         ('onmncc_setup_cnf', self._onmncc_setup_cnf),
                         ('onmncc_disc_ind', self._onmncc_disc_ind),
                         ('onenterNULL', self._onenter_NULL),
                         ],
            )
        self.fsm.onchangestate = self._printstatechange

    def start_mt_call(self, calling, called):
        self.calling = calling
        self.called = called
        self.fsm.mncc_setup_req()

    # MT call
    def _do_mncc_rel_ind(self, mncc_msg):
        self.fsm.mncc_rel_ind(mncc_msg)
    def _do_mncc_call_conf_ind(self, mncc_msg):
        self.fsm.mncc_call_conf_ind(mncc_msg)
    def _do_mncc_alert_ind(self, mncc_msg):
        self.fsm.mncc_alert_ind(mncc_msg)
    def _do_mncc_setup_cnf(self, mncc_msg):
        self.fsm.mncc_setup_cnf(mncc_msg)

    # MO call
    def _do_mncc_setup_ind(self, mncc_msg):
        self.fsm.mncc_setup_ind(mncc_msg)
    def _do_mncc_setup_compl_ind(self, mncc_msg):
        self.fsm.mncc_setup_compl_ind(mncc_msg)

    # Misc
    def _do_mncc_disc_ind(self, mncc_msg):
        self.fsm.mncc_disc_ind(mncc_msg)
    def _do_mncc_rel_ind(self, mncc_msg):
        self.fsm.mncc_rel_ind(mncc_msg)
    def _do_mncc_rel_cnf(self, mncc_msg):
        self.fsm.mncc_rel_cnf(mncc_msg)

    _func_by_type = {
            # MT call
            mncc.MNCC_REL_IND: _do_mncc_rel_ind,
            mncc.MNCC_CALL_CONF_IND: _do_mncc_call_conf_ind,
            mncc.MNCC_ALERT_IND: _do_mncc_alert_ind,
            mncc.MNCC_SETUP_CNF: _do_mncc_setup_cnf,

            # MO call
            mncc.MNCC_SETUP_IND: _do_mncc_setup_ind,
            mncc.MNCC_SETUP_COMPL_IND: _do_mncc_setup_compl_ind,

            # misc
            mncc.MNCC_DISC_IND: _do_mncc_disc_ind,
            mncc.MNCC_REL_IND: _do_mncc_rel_ind,
            mncc.MNCC_REL_CNF: _do_mncc_rel_cnf,
            }

    def _lookup_method(self, mncc_msg_type):
        return self._func_by_type[mncc_msg_type]

    def _handle_mncc(self, mncc_msg):
        if mncc_msg.callref != self.callref:
            raise Exception('mncc', 'Callref not for this GsmCallFsm')
        self._lookup_method(mncc_msg.msg_type)(self, mncc_msg)

    # pykka Actor message receiver
    def on_receive(self, message):
        if message['type'] == 'mncc':
            msg = message['msg']
            print 'GsmCallFsm(%u):on_receive(mncc, %s)' % (self.callref, msg)
            if msg.callref == self.callref:
                return self._handle_mncc(msg)
        elif message['type'] == 'start_mt_call':
            self.start_mt_call(message['calling'], message['called'])
        else:
            raise Exception('mncc', 'Unknown message %s' % message)


class GsmCallConnector(pykka.ThreadingActor):
    def __init__(self, mncc_act):
        super(GsmCallConnector, self).__init__()
        self.mncc_act = mncc_act
        print 'Starting Call A actor'
        self.call_a = GsmCallFsm.start(self.mncc_act, self.actor_ref)
        print 'Starting Call B actor'
        self.call_b = GsmCallFsm.start(self.mncc_act, self.actor_ref)

    def start_call_ab(self, msisdn_a, msisdn_b):
        print 'Starting calls for A and B'
        self.msisdn_a = msisdn_a
        self.msisdn_b = msisdn_b

        # start MT call A->B
        print 'Starting Call A->B'
        self.call_a.tell({'type':'start_mt_call', 'calling':self.msisdn_a, 'called':self.msisdn_b})

        # start MT call B->A
        print 'Starting Call B->A'
        self.call_b.tell({'type':'start_mt_call', 'calling':self.msisdn_b, 'called':self.msisdn_a})

    def call_state_change(self, msisdn, old_state, new_state):
        print 'CallConnector:leg_state_change(%s) %s -> %s' % (msisdn, old_state, new_state)

    def on_receive(self, message):
        if message['type'] == 'call_state_change':
            self.call_state_change(message['called'], message['old_state'], message['new_state'])
