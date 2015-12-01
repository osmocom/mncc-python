#!/usr/bin/python

import mncc
import ctypes
import pykka

from fysom import Fysom
from mncc_sock import mncc_msg, mncc_number, mncc_rtp_msg

class RtpEndpointData(object):
    def __init__(self):
        self.ip = self.port = self.payload_type = self.payload_msg_type = None

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
        # ask to create the RTP socket in RTP bridge mode
        if self.rtp_bridge:
            msg = mncc_rtp_msg(msg_type = mncc.MNCC_RTP_CREATE, callref = self.callref)
            self.mncc_ref.tell({'type': 'send', 'msg': msg})
        # directly transition into the ACTIVE state
        self.fsm.mncc_setup_compl_req()

    def _onmncc_disc_ind(self, e):
        # send MNCC_RELEASE_REQ
        msg = mncc_msg(msg_type = mncc.MNCC_REL_REQ, callref = self.callref)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def _onenter_NULL(self, e):
        if e.event != 'startup':
            self.stop()

    def __init__(self, mncc_ref, ctrl_ref = None, rtp_bridge = True):
        super(GsmCallFsm, self).__init__()
        self.mncc_ref = mncc_ref;
        self.callref = self._get_next_callref()
        self.ctrl_ref = ctrl_ref
        self.rtp_bridge = rtp_bridge
        self.rtp = None
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

                    ('mncc_rel_cnf', 'RELEASE_REQUEST', 'NULL'),
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

    def connect_rtp(self, rtp):
        rtp.msg_type = mncc.MNCC_RTP_CONNECT
        rtp.callref = self.callref
        self.mncc_ref.tell({'type': 'send', 'msg': rtp})

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

    # RTP
    def _do_mncc_rtp_create_ind(self, mncc_msg):
        if self.rtp_bridge == False:
            raise Exception('GsmCallFsm', 'rtp_create_ind but not in RTP bridge mode')
        self.rtp = mncc_msg
        # notify the call controller about this
        self.ctrl_ref.tell({'type':'rtp_create_ind', 'called':self.called, 'rtp':self.rtp})

    def _do_mncc_rtp_connect_ind(self, mncc_msg):
        # FIXME
        return

    def _do_mncc_rtp_free_ind(self, mncc_msg):
        # FIXME
        return

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

            # RTP
            mncc.MNCC_RTP_CREATE: _do_mncc_rtp_create_ind,
            mncc.MNCC_RTP_CONNECT: _do_mncc_rtp_connect_ind,
            mncc.MNCC_RTP_FREE: _do_mncc_rtp_free_ind,
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
            if msg.callref == self.callref:
                print 'GsmCallFsm(%u):on_receive(mncc, %s)' % (self.callref, msg)
                return self._handle_mncc(msg)
        elif message['type'] == 'start_mt_call':
            self.start_mt_call(message['calling'], message['called'])
        elif message['type'] == 'connect_rtp':
            self.connect_rtp(message['rtp'])
        else:
            raise Exception('mncc', 'Unknown message %s' % message)


class GsmCallConnector(pykka.ThreadingActor):
    def __init__(self, mncc_act, rtp_bridge = True):
        super(GsmCallConnector, self).__init__()
        self.mncc_act = mncc_act
        self.rtp_bridge = rtp_bridge
        print 'Starting Call A actor'
        self.call_a = GsmCallFsm.start(self.mncc_act, self.actor_ref, self.rtp_bridge)
        print 'Starting Call B actor'
        self.call_b = GsmCallFsm.start(self.mncc_act, self.actor_ref, self.rtp_bridge)
        self.state_a = self_state_b = 'NULL'
        self.rtp_a = self.rtp_b = None

    def start_call_ab(self, msisdn_a, msisdn_b):
        print 'Starting calls for A and B'
        self.msisdn_a = msisdn_a
        self.msisdn_b = msisdn_b

        # start MT call B->A
        print 'Starting MT Call to A'
        self.call_a.tell({'type':'start_mt_call', 'calling':self.msisdn_b, 'called':self.msisdn_a})

        # start MT call A->B
        print 'Starting Call to B'
        self.call_b.tell({'type':'start_mt_call', 'calling':self.msisdn_a, 'called':self.msisdn_b})

    def rtp_created(self, msisdn, rtp):
        print 'CallConnector:rtp_created(%s) %s' % (msisdn, rtp)
        if self.rtp_bridge == False:
            raise Exception('GsmCallConnector', 'rtp_created but not in RTP bridge mode')
        if msisdn == self.msisdn_a:     # A->B leg
            self.rtp_a = rtp
        elif msisdn == self.msisdn_b:   # B->A leg
            self.rtp_b = rtp
        if self.rtp_a and self.rtp_b:
            self.call_a.tell({'type':'connect_rtp', 'rtp':self.rtp_b})
            self.call_b.tell({'type':'connect_rtp', 'rtp':self.rtp_a})

    def call_state_change(self, msisdn, old_state, new_state):
        print 'CallConnector:leg_state_change(%s) %s -> %s' % (msisdn, old_state, new_state)
        if msisdn == self.msisdn_a:     # A->B leg
            self.state_a = new_state
        elif msisdn == self.msisdn_b:   # B->A leg
            self.state_b = new_state
        #if self.rtp_bridge == False and self.state_a == 'ACTIVE' and self.state_b == 'ACTIVE':
        #    self.connect_legs()

    def on_receive(self, message):
        if message['type'] == 'call_state_change':
            self.call_state_change(message['called'], message['old_state'], message['new_state'])
        elif message['type'] == 'rtp_create_ind':
            self.rtp_created(message['called'], message['rtp'])
        #else:
        #    raise Exception('mncc', 'GsmCallConnector Rx Unknown message %s' % message)
