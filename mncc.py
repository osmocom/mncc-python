# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass





GSM_MAX_FACILITY = 128 # macro
GSM_MAX_SSVERSION = 128 # macro
GSM_MAX_USERUSER = 128 # macro
MNCC_SETUP_REQ = 0x0101 # macro
MNCC_SETUP_IND = 0x0102 # macro
MNCC_SETUP_RSP = 0x0103 # macro
MNCC_SETUP_CNF = 0x0104 # macro
MNCC_SETUP_COMPL_REQ = 0x0105 # macro
MNCC_SETUP_COMPL_IND = 0x0106 # macro
MNCC_CALL_CONF_IND = 0x0107 # macro
MNCC_CALL_PROC_REQ = 0x0108 # macro
MNCC_PROGRESS_REQ = 0x0109 # macro
MNCC_ALERT_REQ = 0x010a # macro
MNCC_ALERT_IND = 0x010b # macro
MNCC_NOTIFY_REQ = 0x010c # macro
MNCC_NOTIFY_IND = 0x010d # macro
MNCC_DISC_REQ = 0x010e # macro
MNCC_DISC_IND = 0x010f # macro
MNCC_REL_REQ = 0x0110 # macro
MNCC_REL_IND = 0x0111 # macro
MNCC_REL_CNF = 0x0112 # macro
MNCC_FACILITY_REQ = 0x0113 # macro
MNCC_FACILITY_IND = 0x0114 # macro
MNCC_START_DTMF_IND = 0x0115 # macro
MNCC_START_DTMF_RSP = 0x0116 # macro
MNCC_START_DTMF_REJ = 0x0117 # macro
MNCC_STOP_DTMF_IND = 0x0118 # macro
MNCC_STOP_DTMF_RSP = 0x0119 # macro
MNCC_MODIFY_REQ = 0x011a # macro
MNCC_MODIFY_IND = 0x011b # macro
MNCC_MODIFY_RSP = 0x011c # macro
MNCC_MODIFY_CNF = 0x011d # macro
MNCC_MODIFY_REJ = 0x011e # macro
MNCC_HOLD_IND = 0x011f # macro
MNCC_HOLD_CNF = 0x0120 # macro
MNCC_HOLD_REJ = 0x0121 # macro
MNCC_RETRIEVE_IND = 0x0122 # macro
MNCC_RETRIEVE_CNF = 0x0123 # macro
MNCC_RETRIEVE_REJ = 0x0124 # macro
MNCC_USERINFO_REQ = 0x0125 # macro
MNCC_USERINFO_IND = 0x0126 # macro
MNCC_REJ_REQ = 0x0127 # macro
MNCC_REJ_IND = 0x0128 # macro
MNCC_BRIDGE = 0x0200 # macro
MNCC_FRAME_RECV = 0x0201 # macro
MNCC_FRAME_DROP = 0x0202 # macro
MNCC_LCHAN_MODIFY = 0x0203 # macro
MNCC_RTP_CREATE = 0x0204 # macro
MNCC_RTP_CONNECT = 0x0205 # macro
MNCC_RTP_FREE = 0x0206 # macro
GSM_TCHF_FRAME = 0x0300 # macro
GSM_TCHF_FRAME_EFR = 0x0301 # macro
GSM_TCHH_FRAME = 0x0302 # macro
GSM_TCH_FRAME_AMR = 0x0303 # macro
GSM_BAD_FRAME = 0x03ff # macro
MNCC_SOCKET_HELLO = 0x0400 # macro
MNCC_F_BEARER_CAP = 0x0001 # macro
MNCC_F_CALLED = 0x0002 # macro
MNCC_F_CALLING = 0x0004 # macro
MNCC_F_REDIRECTING = 0x0008 # macro
MNCC_F_CONNECTED = 0x0010 # macro
MNCC_F_CAUSE = 0x0020 # macro
MNCC_F_USERUSER = 0x0040 # macro
MNCC_F_PROGRESS = 0x0080 # macro
MNCC_F_EMERGENCY = 0x0100 # macro
MNCC_F_FACILITY = 0x0200 # macro
MNCC_F_SSVERSION = 0x0400 # macro
MNCC_F_CCCAP = 0x0800 # macro
MNCC_F_KEYPAD = 0x1000 # macro
MNCC_F_SIGNAL = 0x2000 # macro
MNCC_SOCK_VERSION = 7 # macro

# values for enumeration 'gsm48_bcap_itcap'
gsm48_bcap_itcap__enumvalues = {
    0: 'GSM48_BCAP_ITCAP_SPEECH',
    1: 'GSM48_BCAP_ITCAP_UNR_DIG_INF',
    2: 'GSM48_BCAP_ITCAP_3k1_AUDIO',
    3: 'GSM48_BCAP_ITCAP_FAX_G3',
    5: 'GSM48_BCAP_ITCAP_OTHER',
    7: 'GSM48_BCAP_ITCAP_RESERVED',
}
GSM48_BCAP_ITCAP_SPEECH = 0
GSM48_BCAP_ITCAP_UNR_DIG_INF = 1
GSM48_BCAP_ITCAP_3k1_AUDIO = 2
GSM48_BCAP_ITCAP_FAX_G3 = 3
GSM48_BCAP_ITCAP_OTHER = 5
GSM48_BCAP_ITCAP_RESERVED = 7
gsm48_bcap_itcap = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_tmod'
gsm48_bcap_tmod__enumvalues = {
    0: 'GSM48_BCAP_TMOD_CIRCUIT',
    1: 'GSM48_BCAP_TMOD_PACKET',
}
GSM48_BCAP_TMOD_CIRCUIT = 0
GSM48_BCAP_TMOD_PACKET = 1
gsm48_bcap_tmod = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_coding'
gsm48_bcap_coding__enumvalues = {
    0: 'GSM48_BCAP_CODING_GSM_STD',
}
GSM48_BCAP_CODING_GSM_STD = 0
gsm48_bcap_coding = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_rrq'
gsm48_bcap_rrq__enumvalues = {
    1: 'GSM48_BCAP_RRQ_FR_ONLY',
    2: 'GSM48_BCAP_RRQ_DUAL_HR',
    3: 'GSM48_BCAP_RRQ_DUAL_FR',
}
GSM48_BCAP_RRQ_FR_ONLY = 1
GSM48_BCAP_RRQ_DUAL_HR = 2
GSM48_BCAP_RRQ_DUAL_FR = 3
gsm48_bcap_rrq = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_ra'
gsm48_bcap_ra__enumvalues = {
    0: 'GSM48_BCAP_RA_NONE',
    1: 'GSM48_BCAP_RA_V110_X30',
    2: 'GSM48_BCAP_RA_X31',
    3: 'GSM48_BCAP_RA_OTHER',
}
GSM48_BCAP_RA_NONE = 0
GSM48_BCAP_RA_V110_X30 = 1
GSM48_BCAP_RA_X31 = 2
GSM48_BCAP_RA_OTHER = 3
gsm48_bcap_ra = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_sig_access'
gsm48_bcap_sig_access__enumvalues = {
    1: 'GSM48_BCAP_SA_I440_I450',
    2: 'GSM48_BCAP_SA_X21',
    3: 'GSM48_BCAP_SA_X28_DP_IN',
    4: 'GSM48_BCAP_SA_X28_DP_UN',
    5: 'GSM48_BCAP_SA_X28_NDP',
    6: 'GSM48_BCAP_SA_X32',
}
GSM48_BCAP_SA_I440_I450 = 1
GSM48_BCAP_SA_X21 = 2
GSM48_BCAP_SA_X28_DP_IN = 3
GSM48_BCAP_SA_X28_DP_UN = 4
GSM48_BCAP_SA_X28_NDP = 5
GSM48_BCAP_SA_X32 = 6
gsm48_bcap_sig_access = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_user_rate'
gsm48_bcap_user_rate__enumvalues = {
    1: 'GSM48_BCAP_UR_300',
    2: 'GSM48_BCAP_UR_1200',
    3: 'GSM48_BCAP_UR_2400',
    4: 'GSM48_BCAP_UR_4800',
    5: 'GSM48_BCAP_UR_9600',
    6: 'GSM48_BCAP_UR_12000',
    7: 'GSM48_BCAP_UR_1200_75',
}
GSM48_BCAP_UR_300 = 1
GSM48_BCAP_UR_1200 = 2
GSM48_BCAP_UR_2400 = 3
GSM48_BCAP_UR_4800 = 4
GSM48_BCAP_UR_9600 = 5
GSM48_BCAP_UR_12000 = 6
GSM48_BCAP_UR_1200_75 = 7
gsm48_bcap_user_rate = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_parity'
gsm48_bcap_parity__enumvalues = {
    0: 'GSM48_BCAP_PAR_ODD',
    2: 'GSM48_BCAP_PAR_EVEN',
    3: 'GSM48_BCAP_PAR_NONE',
    4: 'GSM48_BCAP_PAR_ZERO',
    5: 'GSM48_BCAP_PAR_ONE',
}
GSM48_BCAP_PAR_ODD = 0
GSM48_BCAP_PAR_EVEN = 2
GSM48_BCAP_PAR_NONE = 3
GSM48_BCAP_PAR_ZERO = 4
GSM48_BCAP_PAR_ONE = 5
gsm48_bcap_parity = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_interm_rate'
gsm48_bcap_interm_rate__enumvalues = {
    2: 'GSM48_BCAP_IR_8k',
    3: 'GSM48_BCAP_IR_16k',
}
GSM48_BCAP_IR_8k = 2
GSM48_BCAP_IR_16k = 3
gsm48_bcap_interm_rate = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_transp'
gsm48_bcap_transp__enumvalues = {
    0: 'GSM48_BCAP_TR_TRANSP',
    1: 'GSM48_BCAP_TR_RLP',
    2: 'GSM48_BCAP_TR_TR_PREF',
    3: 'GSM48_BCAP_TR_RLP_PREF',
}
GSM48_BCAP_TR_TRANSP = 0
GSM48_BCAP_TR_RLP = 1
GSM48_BCAP_TR_TR_PREF = 2
GSM48_BCAP_TR_RLP_PREF = 3
gsm48_bcap_transp = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_modem_type'
gsm48_bcap_modem_type__enumvalues = {
    0: 'GSM48_BCAP_MT_NONE',
    1: 'GSM48_BCAP_MT_V21',
    2: 'GSM48_BCAP_MT_V22',
    3: 'GSM48_BCAP_MT_V22bis',
    4: 'GSM48_BCAP_MT_V23',
    5: 'GSM48_BCAP_MT_V26ter',
    6: 'GSM48_BCAP_MT_V32',
    7: 'GSM48_BCAP_MT_UNDEF',
    8: 'GSM48_BCAP_MT_AUTO_1',
}
GSM48_BCAP_MT_NONE = 0
GSM48_BCAP_MT_V21 = 1
GSM48_BCAP_MT_V22 = 2
GSM48_BCAP_MT_V22bis = 3
GSM48_BCAP_MT_V23 = 4
GSM48_BCAP_MT_V26ter = 5
GSM48_BCAP_MT_V32 = 6
GSM48_BCAP_MT_UNDEF = 7
GSM48_BCAP_MT_AUTO_1 = 8
gsm48_bcap_modem_type = ctypes.c_uint32 # enum

# values for enumeration 'gsm48_bcap_speech_ver'
gsm48_bcap_speech_ver__enumvalues = {
    0: 'GSM48_BCAP_SV_FR',
    1: 'GSM48_BCAP_SV_HR',
    2: 'GSM48_BCAP_SV_EFR',
    4: 'GSM48_BCAP_SV_AMR_F',
    5: 'GSM48_BCAP_SV_AMR_H',
    6: 'GSM48_BCAP_SV_AMR_OFW',
    7: 'GSM48_BCAP_SV_AMR_OHW',
    8: 'GSM48_BCAP_SV_AMR_FW',
    11: 'GSM48_BCAP_SV_AMR_OH',
}
GSM48_BCAP_SV_FR = 0
GSM48_BCAP_SV_HR = 1
GSM48_BCAP_SV_EFR = 2
GSM48_BCAP_SV_AMR_F = 4
GSM48_BCAP_SV_AMR_H = 5
GSM48_BCAP_SV_AMR_OFW = 6
GSM48_BCAP_SV_AMR_OHW = 7
GSM48_BCAP_SV_AMR_FW = 8
GSM48_BCAP_SV_AMR_OH = 11
gsm48_bcap_speech_ver = ctypes.c_uint32 # enum
class struct_gsm_mncc_bearer_cap(Structure):
    pass

class struct_gsm_mncc_bearer_cap_data(Structure):
    pass

struct_gsm_mncc_bearer_cap_data._pack_ = 1 # source:False
struct_gsm_mncc_bearer_cap_data._fields_ = [
    ('rate_adaption', gsm48_bcap_ra),
    ('sig_access', gsm48_bcap_sig_access),
    ('async', ctypes.c_int32),
    ('nr_stop_bits', ctypes.c_int32),
    ('nr_data_bits', ctypes.c_int32),
    ('user_rate', gsm48_bcap_user_rate),
    ('parity', gsm48_bcap_parity),
    ('interm_rate', gsm48_bcap_interm_rate),
    ('transp', gsm48_bcap_transp),
    ('modem_type', gsm48_bcap_modem_type),
]

struct_gsm_mncc_bearer_cap._pack_ = 1 # source:False
struct_gsm_mncc_bearer_cap._fields_ = [
    ('transfer', ctypes.c_int32),
    ('mode', ctypes.c_int32),
    ('coding', ctypes.c_int32),
    ('radio', ctypes.c_int32),
    ('speech_ctm', ctypes.c_int32),
    ('speech_ver', ctypes.c_int32 * 8),
    ('data', struct_gsm_mncc_bearer_cap_data),
]

class struct_gsm_mncc_number(Structure):
    pass

struct_gsm_mncc_number._pack_ = 1 # source:False
struct_gsm_mncc_number._fields_ = [
    ('type', ctypes.c_int32),
    ('plan', ctypes.c_int32),
    ('present', ctypes.c_int32),
    ('screen', ctypes.c_int32),
    ('number', ctypes.c_char * 33),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_gsm_mncc_cause(Structure):
    pass

struct_gsm_mncc_cause._pack_ = 1 # source:False
struct_gsm_mncc_cause._fields_ = [
    ('location', ctypes.c_int32),
    ('coding', ctypes.c_int32),
    ('rec', ctypes.c_int32),
    ('rec_val', ctypes.c_int32),
    ('value', ctypes.c_int32),
    ('diag_len', ctypes.c_int32),
    ('diag', ctypes.c_char * 32),
]

class struct_gsm_mncc_useruser(Structure):
    pass

struct_gsm_mncc_useruser._pack_ = 1 # source:False
struct_gsm_mncc_useruser._fields_ = [
    ('proto', ctypes.c_int32),
    ('info', ctypes.c_char * 129),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_gsm_mncc_progress(Structure):
    pass

struct_gsm_mncc_progress._pack_ = 1 # source:False
struct_gsm_mncc_progress._fields_ = [
    ('coding', ctypes.c_int32),
    ('location', ctypes.c_int32),
    ('descr', ctypes.c_int32),
]

class struct_gsm_mncc_facility(Structure):
    pass

struct_gsm_mncc_facility._pack_ = 1 # source:False
struct_gsm_mncc_facility._fields_ = [
    ('len', ctypes.c_int32),
    ('info', ctypes.c_char * 128),
]

class struct_gsm_mncc_ssversion(Structure):
    pass

struct_gsm_mncc_ssversion._pack_ = 1 # source:False
struct_gsm_mncc_ssversion._fields_ = [
    ('len', ctypes.c_int32),
    ('info', ctypes.c_char * 128),
]

class struct_gsm_mncc_cccap(Structure):
    pass

struct_gsm_mncc_cccap._pack_ = 1 # source:False
struct_gsm_mncc_cccap._fields_ = [
    ('dtmf', ctypes.c_int32),
    ('pcp', ctypes.c_int32),
]


# values for enumeration 'gsm_mncc_bcap'
gsm_mncc_bcap__enumvalues = {
    0: 'GSM_MNCC_BCAP_SPEECH',
    1: 'GSM_MNCC_BCAP_UNR_DIG',
    2: 'GSM_MNCC_BCAP_AUDIO',
    3: 'GSM_MNCC_BCAP_FAX_G3',
    5: 'GSM_MNCC_BCAP_OTHER_ITC',
    7: 'GSM_MNCC_BCAP_RESERVED',
}
GSM_MNCC_BCAP_SPEECH = 0
GSM_MNCC_BCAP_UNR_DIG = 1
GSM_MNCC_BCAP_AUDIO = 2
GSM_MNCC_BCAP_FAX_G3 = 3
GSM_MNCC_BCAP_OTHER_ITC = 5
GSM_MNCC_BCAP_RESERVED = 7
gsm_mncc_bcap = ctypes.c_uint32 # enum
class struct_gsm_mncc(Structure):
    pass

class struct_gsm_mncc_clir(Structure):
    pass

struct_gsm_mncc_clir._pack_ = 1 # source:False
struct_gsm_mncc_clir._fields_ = [
    ('sup', ctypes.c_int32),
    ('inv', ctypes.c_int32),
]

struct_gsm_mncc._pack_ = 1 # source:False
struct_gsm_mncc._fields_ = [
    ('msg_type', ctypes.c_uint32),
    ('callref', ctypes.c_uint32),
    ('fields', ctypes.c_uint32),
    ('bearer_cap', struct_gsm_mncc_bearer_cap),
    ('called', struct_gsm_mncc_number),
    ('calling', struct_gsm_mncc_number),
    ('redirecting', struct_gsm_mncc_number),
    ('connected', struct_gsm_mncc_number),
    ('cause', struct_gsm_mncc_cause),
    ('progress', struct_gsm_mncc_progress),
    ('useruser', struct_gsm_mncc_useruser),
    ('facility', struct_gsm_mncc_facility),
    ('cccap', struct_gsm_mncc_cccap),
    ('ssversion', struct_gsm_mncc_ssversion),
    ('clir', struct_gsm_mncc_clir),
    ('signal', ctypes.c_int32),
    ('keypad', ctypes.c_int32),
    ('more', ctypes.c_int32),
    ('notify', ctypes.c_int32),
    ('emergency', ctypes.c_int32),
    ('imsi', ctypes.c_char * 16),
    ('lchan_type', ctypes.c_ubyte),
    ('lchan_mode', ctypes.c_ubyte),
    ('sdp', ctypes.c_char * 1024),
    ('PADDING_0', ctypes.c_ubyte * 2),
]

class struct_gsm_data_frame(Structure):
    pass

struct_gsm_data_frame._pack_ = 1 # source:False
struct_gsm_data_frame._fields_ = [
    ('msg_type', ctypes.c_uint32),
    ('callref', ctypes.c_uint32),
    ('data', ctypes.c_ubyte * 0),
]

class struct_gsm_mncc_hello(Structure):
    pass

struct_gsm_mncc_hello._pack_ = 1 # source:False
struct_gsm_mncc_hello._fields_ = [
    ('msg_type', ctypes.c_uint32),
    ('version', ctypes.c_uint32),
    ('mncc_size', ctypes.c_uint32),
    ('data_frame_size', ctypes.c_uint32),
    ('called_offset', ctypes.c_uint32),
    ('signal_offset', ctypes.c_uint32),
    ('emergency_offset', ctypes.c_uint32),
    ('lchan_type_offset', ctypes.c_uint32),
]

class struct_gsm_mncc_rtp(Structure):
    pass

class struct_sockaddr_storage(Structure):
    pass

struct_sockaddr_storage._pack_ = 1 # source:False
struct_sockaddr_storage._fields_ = [
    ('ss_family', ctypes.c_uint16),
    ('__ss_padding', ctypes.c_char * 118),
    ('__ss_align', ctypes.c_uint64),
]

struct_gsm_mncc_rtp._pack_ = 1 # source:False
struct_gsm_mncc_rtp._fields_ = [
    ('msg_type', ctypes.c_uint32),
    ('callref', ctypes.c_uint32),
    ('addr', struct_sockaddr_storage),
    ('payload_type', ctypes.c_uint32),
    ('payload_msg_type', ctypes.c_uint32),
    ('sdp', ctypes.c_char * 1024),
]

class struct_gsm_mncc_bridge(Structure):
    pass

struct_gsm_mncc_bridge._pack_ = 1 # source:False
struct_gsm_mncc_bridge._fields_ = [
    ('msg_type', ctypes.c_uint32),
    ('callref', ctypes.c_uint32 * 2),
]

__all__ = \
    ['GSM48_BCAP_CODING_GSM_STD', 'GSM48_BCAP_IR_16k',
    'GSM48_BCAP_IR_8k', 'GSM48_BCAP_ITCAP_3k1_AUDIO',
    'GSM48_BCAP_ITCAP_FAX_G3', 'GSM48_BCAP_ITCAP_OTHER',
    'GSM48_BCAP_ITCAP_RESERVED', 'GSM48_BCAP_ITCAP_SPEECH',
    'GSM48_BCAP_ITCAP_UNR_DIG_INF', 'GSM48_BCAP_MT_AUTO_1',
    'GSM48_BCAP_MT_NONE', 'GSM48_BCAP_MT_UNDEF', 'GSM48_BCAP_MT_V21',
    'GSM48_BCAP_MT_V22', 'GSM48_BCAP_MT_V22bis', 'GSM48_BCAP_MT_V23',
    'GSM48_BCAP_MT_V26ter', 'GSM48_BCAP_MT_V32',
    'GSM48_BCAP_PAR_EVEN', 'GSM48_BCAP_PAR_NONE',
    'GSM48_BCAP_PAR_ODD', 'GSM48_BCAP_PAR_ONE', 'GSM48_BCAP_PAR_ZERO',
    'GSM48_BCAP_RA_NONE', 'GSM48_BCAP_RA_OTHER',
    'GSM48_BCAP_RA_V110_X30', 'GSM48_BCAP_RA_X31',
    'GSM48_BCAP_RRQ_DUAL_FR', 'GSM48_BCAP_RRQ_DUAL_HR',
    'GSM48_BCAP_RRQ_FR_ONLY', 'GSM48_BCAP_SA_I440_I450',
    'GSM48_BCAP_SA_X21', 'GSM48_BCAP_SA_X28_DP_IN',
    'GSM48_BCAP_SA_X28_DP_UN', 'GSM48_BCAP_SA_X28_NDP',
    'GSM48_BCAP_SA_X32', 'GSM48_BCAP_SV_AMR_F',
    'GSM48_BCAP_SV_AMR_FW', 'GSM48_BCAP_SV_AMR_H',
    'GSM48_BCAP_SV_AMR_OFW', 'GSM48_BCAP_SV_AMR_OH',
    'GSM48_BCAP_SV_AMR_OHW', 'GSM48_BCAP_SV_EFR', 'GSM48_BCAP_SV_FR',
    'GSM48_BCAP_SV_HR', 'GSM48_BCAP_TMOD_CIRCUIT',
    'GSM48_BCAP_TMOD_PACKET', 'GSM48_BCAP_TR_RLP',
    'GSM48_BCAP_TR_RLP_PREF', 'GSM48_BCAP_TR_TRANSP',
    'GSM48_BCAP_TR_TR_PREF', 'GSM48_BCAP_UR_1200',
    'GSM48_BCAP_UR_12000', 'GSM48_BCAP_UR_1200_75',
    'GSM48_BCAP_UR_2400', 'GSM48_BCAP_UR_300', 'GSM48_BCAP_UR_4800',
    'GSM48_BCAP_UR_9600', 'GSM_BAD_FRAME', 'GSM_MAX_FACILITY',
    'GSM_MAX_SSVERSION', 'GSM_MAX_USERUSER', 'GSM_MNCC_BCAP_AUDIO',
    'GSM_MNCC_BCAP_FAX_G3', 'GSM_MNCC_BCAP_OTHER_ITC',
    'GSM_MNCC_BCAP_RESERVED', 'GSM_MNCC_BCAP_SPEECH',
    'GSM_MNCC_BCAP_UNR_DIG', 'GSM_TCHF_FRAME', 'GSM_TCHF_FRAME_EFR',
    'GSM_TCHH_FRAME', 'GSM_TCH_FRAME_AMR', 'MNCC_ALERT_IND',
    'MNCC_ALERT_REQ', 'MNCC_BRIDGE', 'MNCC_CALL_CONF_IND',
    'MNCC_CALL_PROC_REQ', 'MNCC_DISC_IND', 'MNCC_DISC_REQ',
    'MNCC_FACILITY_IND', 'MNCC_FACILITY_REQ', 'MNCC_FRAME_DROP',
    'MNCC_FRAME_RECV', 'MNCC_F_BEARER_CAP', 'MNCC_F_CALLED',
    'MNCC_F_CALLING', 'MNCC_F_CAUSE', 'MNCC_F_CCCAP',
    'MNCC_F_CONNECTED', 'MNCC_F_EMERGENCY', 'MNCC_F_FACILITY',
    'MNCC_F_KEYPAD', 'MNCC_F_PROGRESS', 'MNCC_F_REDIRECTING',
    'MNCC_F_SIGNAL', 'MNCC_F_SSVERSION', 'MNCC_F_USERUSER',
    'MNCC_HOLD_CNF', 'MNCC_HOLD_IND', 'MNCC_HOLD_REJ',
    'MNCC_LCHAN_MODIFY', 'MNCC_MODIFY_CNF', 'MNCC_MODIFY_IND',
    'MNCC_MODIFY_REJ', 'MNCC_MODIFY_REQ', 'MNCC_MODIFY_RSP',
    'MNCC_NOTIFY_IND', 'MNCC_NOTIFY_REQ', 'MNCC_PROGRESS_REQ',
    'MNCC_REJ_IND', 'MNCC_REJ_REQ', 'MNCC_REL_CNF', 'MNCC_REL_IND',
    'MNCC_REL_REQ', 'MNCC_RETRIEVE_CNF', 'MNCC_RETRIEVE_IND',
    'MNCC_RETRIEVE_REJ', 'MNCC_RTP_CONNECT', 'MNCC_RTP_CREATE',
    'MNCC_RTP_FREE', 'MNCC_SETUP_CNF', 'MNCC_SETUP_COMPL_IND',
    'MNCC_SETUP_COMPL_REQ', 'MNCC_SETUP_IND', 'MNCC_SETUP_REQ',
    'MNCC_SETUP_RSP', 'MNCC_SOCKET_HELLO', 'MNCC_SOCK_VERSION',
    'MNCC_START_DTMF_IND', 'MNCC_START_DTMF_REJ',
    'MNCC_START_DTMF_RSP', 'MNCC_STOP_DTMF_IND', 'MNCC_STOP_DTMF_RSP',
    'MNCC_USERINFO_IND', 'MNCC_USERINFO_REQ', 'gsm48_bcap_coding',
    'gsm48_bcap_interm_rate', 'gsm48_bcap_itcap',
    'gsm48_bcap_modem_type', 'gsm48_bcap_parity', 'gsm48_bcap_ra',
    'gsm48_bcap_rrq', 'gsm48_bcap_sig_access',
    'gsm48_bcap_speech_ver', 'gsm48_bcap_tmod', 'gsm48_bcap_transp',
    'gsm48_bcap_user_rate', 'gsm_mncc_bcap', 'struct_gsm_data_frame',
    'struct_gsm_mncc', 'struct_gsm_mncc_bearer_cap',
    'struct_gsm_mncc_bearer_cap_data', 'struct_gsm_mncc_bridge',
    'struct_gsm_mncc_cause', 'struct_gsm_mncc_cccap',
    'struct_gsm_mncc_clir', 'struct_gsm_mncc_facility',
    'struct_gsm_mncc_hello', 'struct_gsm_mncc_number',
    'struct_gsm_mncc_progress', 'struct_gsm_mncc_rtp',
    'struct_gsm_mncc_ssversion', 'struct_gsm_mncc_useruser',
    'struct_sockaddr_storage']
