#!/usr/bin/env python2

# Python implementation of GSM 04.08 call state machine for use with
# OsmoNITB MNCC interface
#
# (C) 2015 by Harald Welte <laforge@gnumonks.org>
#
# Licensed under GNU General Public License, Version 2 or at your
# option, any later version.


import mncc
import ctypes
import pykka

from fysom import Fysom
from mncc_sock import mncc_msg, mncc_number, mncc_rtp_msg, mncc_bridge_msg, mncc_bearer_cap

Uint32Array2 = mncc.uint32_t * 2

class GSM48:
    class BCAP_SV(object):
        # GSM 04.08 bearer capability speech version
        FR    = 0
        HR    = 1
        EFR   = 2
        AMR_F = 4
        AMR_H = 5

        def __init__(self, codec):
            self.codec = codec;

        def __str__(self):
            if self.codec == GSM48.BCAP_SV.FR:
                return 'FR'
            elif self.codec == GSM48.BCAP_SV.HR:
                return 'HR'
            elif self.codec == GSM48.BCAP_SV.EFR:
                return 'EFR'
            elif self.codec == GSM48.BCAP_SV.AMR_F:
                return 'AMR-FR'
            elif self.codec == GSM48.BCAP_SV.AMR_H:
                return 'AMR-HR'
            else:
                return 'Unknown'

        def to_lchan_mode(self):
            if self.codec == GSM48.BCAP_SV.FR:
                return GSM48.ChanMode.SPEECH_V1
            elif self.codec == GSM48.BCAP_SV.HR:
                return GSM48.ChanMode.SPEECH_V1
            elif self.codec == GSM48.BCAP_SV.EFR:
                return GSM48.ChanMode.SPEECH_EFR
            elif self.codec == GSM48.BCAP_SV.AMR_F:
                return GSM48.ChanMode.SPEECH_AMR
            elif self.codec == GSM48.BCAP_SV.AMR_H:
                return GSM48.ChanMode.SPEECH_AMR

    AllCodecs = (BCAP_SV.FR, BCAP_SV.HR, BCAP_SV.EFR, BCAP_SV.AMR_F, BCAP_SV.AMR_H)

    class ChanMode:
        # GSM 04.08 Channel Mode
        CMODE_SIGN  = 0x00
        SPEECH_V1   = 0x01
        SPEECH_EFR  = 0x21
        SPEECH_AMR  = 0x41

class GsmCallFsm(pykka.ThreadingActor):
    last_callref = 0

    def __str__(self):
        return 'GsmCallFsm(%u/%s->%s/%s)' % (self.callref, self.calling, self.called, self.fsm.current)

    def _get_next_callref(self):
        GsmCallFsm.last_callref = GsmCallFsm.last_callref + 1
        return GsmCallFsm.last_callref;

    def _printstatechange(self, e):
        print '%s: event: %s, %s -> %s' % (self, e.event, e.src, e.dst)
        if self.ctrl_ref != None:
            self.ctrl_ref.tell({'type':'call_state_change', 'called':self.called, 'old_state':e.src, 'new_state':e.dst})

    def _onmncc_setup_req(self, e):
        msg = mncc_msg(msg_type = mncc.MNCC_SETUP_REQ, callref = self.callref,
                       fields = mncc.MNCC_F_CALLED | mncc.MNCC_F_CALLING | mncc.MNCC_F_BEARER_CAP,
                       calling = mncc_number(self.calling),
                       called = mncc_number(self.called),
                       bearer_cap = mncc_bearer_cap(self.codecs_permitted))
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def find_matching_codec(self, ms_codecs):
        # find common denominator of permitted codecs and MS codecs
        for i in self.codecs_permitted:
            if i in ms_codecs:
                return GSM48.BCAP_SV(i)
        return None

    def _onmncc_call_conf_ind(self, e):
        msg_in = e.args[0]
        codec = self.find_matching_codec(msg_in.bearer_cap.speech_ver)
        print '%s: CALL-CONF.ind(selected codec = %s)' % (self, codec)
        # select the according lchan_mode
        lchan_mode = codec.to_lchan_mode()
        msg = mncc_msg(msg_type = mncc.MNCC_LCHAN_MODIFY, callref = msg_in.callref, lchan_mode = lchan_mode)
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

    def __init__(self, mncc_ref, ctrl_ref = None, rtp_bridge = True, codecs_permitted = GSM48.AllCodecs):
        super(GsmCallFsm, self).__init__()
        self.mncc_ref = mncc_ref;
        self.calling = self.called = None
        self.callref = self._get_next_callref()
        self.ctrl_ref = ctrl_ref
        self.rtp_bridge = rtp_bridge
        self.rtp = None
        self.codecs_permitted = codecs_permitted
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
                         ('onmncc_call_conf_ind', self._onmncc_call_conf_ind),
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

    # DTMF
    def _do_mncc_start_dtmf_ind(self, msg_in):
        msg = mncc_msg(msg_type = mncc.MNCC_START_DTMF_RSP, callref = self.callref, fields = mncc.MNCC_F_KEYPAD, keypad = msg_in.keypad)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    def _do_mncc_stop_dtmf_ind(self, msg_in):
        msg = mncc_msg(msg_type = mncc.MNCC_STOP_DTMF_RSP, callref = self.callref, fields = mncc.MNCC_F_KEYPAD, keypad = msg_in.keypad)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

    # HOLD
    def _do_mncc_hold_ind(self, msg_in):
        # reject any hold requests
        msg = mncc_msg(msg_type = mncc.MNCC_HOLD_REJ, callref= self.callref)
        self.mncc_ref.tell({'type': 'send', 'msg': msg})

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

            # DTMF
            mncc.MNCC_START_DTMF_IND: _do_mncc_start_dtmf_ind,
            mncc.MNCC_STOP_DTMF_IND: _do_mncc_stop_dtmf_ind,

            # HOLD
            mncc.MNCC_HOLD_IND: _do_mncc_hold_ind,
            }

    def _lookup_method(self, mncc_msg_type):
        return self._func_by_type[mncc_msg_type]

    def _handle_mncc(self, mncc_msg):
        if mncc_msg.callref != self.callref:
            raise Exception('mncc', '%s: Callref not for this GsmCallFsm' % self)
        self._lookup_method(mncc_msg.msg_type)(self, mncc_msg)

    # pykka Actor message receiver
    def on_receive(self, message):
        if message['type'] == 'mncc':
            msg = message['msg']
            if msg.callref == self.callref:
                print '%s: on_receive(mncc, %s)' % (self, msg)
                return self._handle_mncc(msg)
        elif message['type'] == 'start_mt_call':
            self.start_mt_call(message['calling'], message['called'])
        elif message['type'] == 'connect_rtp':
            self.connect_rtp(message['rtp'])
        elif message['type'] == 'get_callref':
            return self.callref
        else:
            raise Exception('mncc', '%s: Unknown message %s' % (self, message))


class GsmCallConnector(pykka.ThreadingActor):
    def __init__(self, mncc_act, rtp_bridge = True, codecs_permitted = GSM48.AllCodecs):
        super(GsmCallConnector, self).__init__()
        self.mncc_act = mncc_act
        self.rtp_bridge = rtp_bridge
        self.codecs_permitted = codecs_permitted
        self.call_a = GsmCallFsm.start(self.mncc_act, self.actor_ref, self.rtp_bridge, self.codecs_permitted)
        self.call_b = GsmCallFsm.start(self.mncc_act, self.actor_ref, self.rtp_bridge, self.codecs_permitted)
        self.callref_a = self.call_a.ask({'type':'get_callref'})
        self.callref_b = self.call_b.ask({'type':'get_callref'})
        self.state_a = self_state_b = 'NULL'
        self.rtp_a = self.rtp_b = None

    def start_call_ab(self, msisdn_a, msisdn_b):
        self.msisdn_a = msisdn_a
        self.msisdn_b = msisdn_b
        # start MT call B->A
        self.call_a.tell({'type':'start_mt_call', 'calling':self.msisdn_b, 'called':self.msisdn_a})
        # start MT call A->B
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

    def bridge_legs(self):
        # bridge the voice channels of both call legs in the classic way
        if self.rtp_bridge:
            raise Exception('GsmCallConnector', 'bridge_legs but in RTP bridge mode')
        msg = mncc_bridge_msg(msg_type = mncc.MNCC_BRIDGE, callref = Uint32Array2(self.callref_a, self.callref_b))
        self.mncc_act.tell({'type': 'send', 'msg': msg})

    def call_state_change(self, msisdn, old_state, new_state):
        print 'CallConnector:leg_state_change(%s) %s -> %s' % (msisdn, old_state, new_state)
        if msisdn == self.msisdn_a:     # A->B leg
            self.state_a = new_state
        elif msisdn == self.msisdn_b:   # B->A leg
            self.state_b = new_state
        if self.rtp_bridge == False and self.state_a == 'ACTIVE' and self.state_b == 'ACTIVE':
            self.bridge_legs()
        if self.state_a == 'NULL' and self.state_b == 'NULL':
            print 'Both A and B in state NULL -> Terminating'
            self.stop()

    def on_receive(self, message):
        if message['type'] == 'call_state_change':
            self.call_state_change(message['called'], message['old_state'], message['new_state'])
        elif message['type'] == 'rtp_create_ind':
            self.rtp_created(message['called'], message['rtp'])
        #else:
        #    raise Exception('mncc', 'GsmCallConnector Rx Unknown message %s' % message)
