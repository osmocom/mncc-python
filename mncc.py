from ctypes import *



GSM48_BCAP_UR_300 = 1
GSM48_BCAP_MT_AUTO_1 = 8
GSM48_BCAP_PAR_EVEN = 2
GSM48_BCAP_PAR_ONE = 5
GSM48_BCAP_UR_4800 = 4
GSM48_BCAP_TR_TR_PREF = 2
GSM48_BCAP_SA_X32 = 6
GSM48_BCAP_SA_X28_NDP = 5
GSM48_BCAP_SA_X28_DP_UN = 4
GSM48_BCAP_PAR_ODD = 0
GSM48_BCAP_SA_X28_DP_IN = 3
GSM48_BCAP_SA_X21 = 2
GSM48_BCAP_UR_2400 = 3
GSM48_BCAP_SA_I440_I450 = 1
GSM48_BCAP_IR_16k = 3
GSM48_BCAP_MT_V26ter = 5
GSM_MNCC_BCAP_SPEECH = 0
GSM48_BCAP_MT_V32 = 6
GSM48_BCAP_MT_V22bis = 3
GSM48_BCAP_TR_RLP = 1
GSM48_BCAP_MT_V22 = 2
GSM48_BCAP_MT_UNDEF = 7
GSM48_BCAP_MT_V23 = 4
GSM48_BCAP_TR_RLP_PREF = 3
GSM48_BCAP_TR_TRANSP = 0
GSM48_BCAP_PAR_ZERO = 4
GSM48_BCAP_MT_V21 = 1
GSM_MNCC_BCAP_AUDIO = 2
GSM48_BCAP_MT_NONE = 0
GSM48_BCAP_UR_1200_75 = 7
GSM48_BCAP_UR_12000 = 6
GSM_MNCC_BCAP_FAX_G3 = 3
GSM48_BCAP_UR_9600 = 5
GSM48_BCAP_IR_8k = 2
GSM_MNCC_BCAP_UNR_DIG = 1
GSM48_BCAP_PAR_NONE = 3
GSM48_BCAP_RA_OTHER = 3
GSM48_BCAP_RA_X31 = 2
GSM48_BCAP_RA_V110_X30 = 1
GSM48_BCAP_RA_NONE = 0
GSM_MNCC_BCAP_RESERVED = 7
GSM_MNCC_BCAP_OTHER_ITC = 5
GSM48_BCAP_UR_1200 = 2

# values for enumeration 'gsm48_bcap_ra'
gsm48_bcap_ra = c_int # enum

# values for enumeration 'gsm48_bcap_sig_access'
gsm48_bcap_sig_access = c_int # enum

# values for enumeration 'gsm48_bcap_user_rate'
gsm48_bcap_user_rate = c_int # enum

# values for enumeration 'gsm48_bcap_parity'
gsm48_bcap_parity = c_int # enum

# values for enumeration 'gsm48_bcap_interm_rate'
gsm48_bcap_interm_rate = c_int # enum

# values for enumeration 'gsm48_bcap_transp'
gsm48_bcap_transp = c_int # enum

# values for enumeration 'gsm48_bcap_modem_type'
gsm48_bcap_modem_type = c_int # enum
class gsm_mncc_bearer_cap(Structure):
    pass
class N19gsm_mncc_bearer_cap3DOT_0E(Structure):
    pass
N19gsm_mncc_bearer_cap3DOT_0E._fields_ = [
    ('rate_adaption', gsm48_bcap_ra),
    ('sig_access', gsm48_bcap_sig_access),
    ('async', c_int),
    ('nr_stop_bits', c_int),
    ('nr_data_bits', c_int),
    ('user_rate', gsm48_bcap_user_rate),
    ('parity', gsm48_bcap_parity),
    ('interm_rate', gsm48_bcap_interm_rate),
    ('transp', gsm48_bcap_transp),
    ('modem_type', gsm48_bcap_modem_type),
]
gsm_mncc_bearer_cap._fields_ = [
    ('transfer', c_int),
    ('mode', c_int),
    ('coding', c_int),
    ('radio', c_int),
    ('speech_ctm', c_int),
    ('speech_ver', c_int * 8),
    ('data', N19gsm_mncc_bearer_cap3DOT_0E),
]
class gsm_mncc_number(Structure):
    pass
gsm_mncc_number._fields_ = [
    ('type', c_int),
    ('plan', c_int),
    ('present', c_int),
    ('screen', c_int),
    ('number', c_char * 33),
]
class gsm_mncc_cause(Structure):
    pass
gsm_mncc_cause._fields_ = [
    ('location', c_int),
    ('coding', c_int),
    ('rec', c_int),
    ('rec_val', c_int),
    ('value', c_int),
    ('diag_len', c_int),
    ('diag', c_char * 32),
]
class gsm_mncc_useruser(Structure):
    pass
gsm_mncc_useruser._fields_ = [
    ('proto', c_int),
    ('info', c_char * 129),
]
class gsm_mncc_progress(Structure):
    pass
gsm_mncc_progress._fields_ = [
    ('coding', c_int),
    ('location', c_int),
    ('descr', c_int),
]
class gsm_mncc_facility(Structure):
    pass
gsm_mncc_facility._fields_ = [
    ('len', c_int),
    ('info', c_char * 128),
]
class gsm_mncc_ssversion(Structure):
    pass
gsm_mncc_ssversion._fields_ = [
    ('len', c_int),
    ('info', c_char * 128),
]
class gsm_mncc_cccap(Structure):
    pass
gsm_mncc_cccap._fields_ = [
    ('dtmf', c_int),
    ('pcp', c_int),
]

# values for unnamed enumeration
class gsm_mncc(Structure):
    pass
uint32_t = c_uint32
class N8gsm_mncc3DOT_2E(Structure):
    pass
N8gsm_mncc3DOT_2E._fields_ = [
    ('sup', c_int),
    ('inv', c_int),
]
gsm_mncc._fields_ = [
    ('msg_type', uint32_t),
    ('callref', uint32_t),
    ('fields', uint32_t),
    ('bearer_cap', gsm_mncc_bearer_cap),
    ('called', gsm_mncc_number),
    ('calling', gsm_mncc_number),
    ('redirecting', gsm_mncc_number),
    ('connected', gsm_mncc_number),
    ('cause', gsm_mncc_cause),
    ('progress', gsm_mncc_progress),
    ('useruser', gsm_mncc_useruser),
    ('facility', gsm_mncc_facility),
    ('cccap', gsm_mncc_cccap),
    ('ssversion', gsm_mncc_ssversion),
    ('clir', N8gsm_mncc3DOT_2E),
    ('signal', c_int),
    ('keypad', c_int),
    ('more', c_int),
    ('notify', c_int),
    ('emergency', c_int),
    ('imsi', c_char * 16),
    ('lchan_type', c_ubyte),
    ('lchan_mode', c_ubyte),
]
class gsm_data_frame(Structure):
    pass
gsm_data_frame._fields_ = [
    ('msg_type', uint32_t),
    ('callref', uint32_t),
    ('data', c_ubyte * 0),
]
class gsm_mncc_hello(Structure):
    pass
gsm_mncc_hello._fields_ = [
    ('msg_type', uint32_t),
    ('version', uint32_t),
    ('mncc_size', uint32_t),
    ('data_frame_size', uint32_t),
    ('called_offset', uint32_t),
    ('signal_offset', uint32_t),
    ('emergency_offset', uint32_t),
    ('lchan_type_offset', uint32_t),
]
class gsm_mncc_rtp(Structure):
    pass
uint16_t = c_uint16
gsm_mncc_rtp._fields_ = [
    ('msg_type', uint32_t),
    ('callref', uint32_t),
    ('ip', uint32_t),
    ('port', uint16_t),
    ('payload_type', uint32_t),
    ('payload_msg_type', uint32_t),
]
INT_LEAST8_MAX = 127 # Variable c_int '127'
_ATFILE_SOURCE = 1 # Variable c_int '1'
MNCC_SETUP_CNF = 260 # Variable c_int '260'
GSM_TCHH_FRAME = 770 # Variable c_int '770'
UINT8_MAX = 255 # Variable c_int '255'
MNCC_F_CAUSE = 32 # Variable c_int '32'
INT_LEAST32_MIN = -2147483648 # Variable c_int '-0x00000000080000000'
__GNU_LIBRARY__ = 6 # Variable c_int '6'
MNCC_REL_CNF = 274 # Variable c_int '274'
__USE_XOPEN = 1 # Variable c_int '1'
__USE_LARGEFILE64 = 1 # Variable c_int '1'
MNCC_RTP_CREATE = 516 # Variable c_int '516'
__USE_XOPEN2KXSI = 1 # Variable c_int '1'
MNCC_STOP_DTMF_RSP = 281 # Variable c_int '281'
MNCC_PROGRESS_REQ = 265 # Variable c_int '265'
__USE_POSIX2 = 1 # Variable c_int '1'
GSM_TCH_FRAME_AMR = 771 # Variable c_int '771'
__USE_XOPEN2K8XSI = 1 # Variable c_int '1'
MNCC_FACILITY_IND = 276 # Variable c_int '276'
MNCC_LCHAN_MODIFY = 515 # Variable c_int '515'
GSM_MAX_FACILITY = 128 # Variable c_int '128'
UINTMAX_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
INT_FAST16_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
__USE_XOPEN_EXTENDED = 1 # Variable c_int '1'
UINT64_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
__USE_ATFILE = 1 # Variable c_int '1'
MNCC_START_DTMF_REJ = 279 # Variable c_int '279'
INT_LEAST16_MAX = 32767 # Variable c_int '32767'
MNCC_SETUP_COMPL_IND = 262 # Variable c_int '262'
MNCC_SOCK_VERSION = 5 # Variable c_int '5'
INTMAX_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
INT32_MAX = 2147483647 # Variable c_int '2147483647'
INTMAX_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
MNCC_USERINFO_IND = 294 # Variable c_int '294'
_POSIX_SOURCE = 1 # Variable c_int '1'
_ISOC95_SOURCE = 1 # Variable c_int '1'
INT64_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
MNCC_REL_REQ = 272 # Variable c_int '272'
_ISOC99_SOURCE = 1 # Variable c_int '1'
UINT_FAST8_MAX = 255 # Variable c_int '255'
MNCC_NOTIFY_IND = 269 # Variable c_int '269'
MNCC_HOLD_CNF = 288 # Variable c_int '288'
INT_LEAST8_MIN = -128 # Variable c_int '-0x00000000000000080'
MNCC_REL_IND = 273 # Variable c_int '273'
MNCC_F_SIGNAL = 8192 # Variable c_int '8192'
INT_FAST64_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
INT_FAST64_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
INT_LEAST64_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
MNCC_BRIDGE = 512 # Variable c_int '512'
MNCC_F_CALLED = 2 # Variable c_int '2'
UINT_LEAST32_MAX = 4294967295L # Variable c_uint '4294967295u'
__USE_POSIX199309 = 1 # Variable c_int '1'
MNCC_RTP_CONNECT = 517 # Variable c_int '517'
__SYSCALL_WORDSIZE = 64 # Variable c_int '64'
_SVID_SOURCE = 1 # Variable c_int '1'
MNCC_SOCKET_HELLO = 1024 # Variable c_int '1024'
UINT32_MAX = 4294967295L # Variable c_uint '4294967295u'
MNCC_F_PROGRESS = 128 # Variable c_int '128'
MNCC_HOLD_REJ = 289 # Variable c_int '289'
GSM_MAX_USERUSER = 128 # Variable c_int '128'
INT64_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
MNCC_SETUP_REQ = 257 # Variable c_int '257'
MNCC_F_USERUSER = 64 # Variable c_int '64'
MNCC_REJ_REQ = 295 # Variable c_int '295'
__USE_XOPEN2K = 1 # Variable c_int '1'
__WORDSIZE_TIME64_COMPAT32 = 1 # Variable c_int '1'
__USE_POSIX = 1 # Variable c_int '1'
__USE_XOPEN2K8 = 1 # Variable c_int '1'
MNCC_USERINFO_REQ = 293 # Variable c_int '293'
MNCC_RTP_FREE = 518 # Variable c_int '518'
__USE_GNU = 1 # Variable c_int '1'
__USE_BSD = 1 # Variable c_int '1'
MNCC_F_REDIRECTING = 8 # Variable c_int '8'
UINTPTR_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
MNCC_ALERT_IND = 267 # Variable c_int '267'
MNCC_ALERT_REQ = 266 # Variable c_int '266'
MNCC_MODIFY_IND = 283 # Variable c_int '283'
MNCC_CALL_CONF_IND = 263 # Variable c_int '263'
_POSIX_C_SOURCE = 200809 # Variable c_long '200809l'
INT16_MIN = -32768 # Variable c_int '-0x00000000000008000'
_ISOC11_SOURCE = 1 # Variable c_int '1'
MNCC_RETRIEVE_REJ = 292 # Variable c_int '292'
INT8_MAX = 127 # Variable c_int '127'
INT16_MAX = 32767 # Variable c_int '32767'
INT_LEAST64_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
__USE_SVID = 1 # Variable c_int '1'
__USE_UNIX98 = 1 # Variable c_int '1'
__USE_MISC = 1 # Variable c_int '1'
__GLIBC__ = 2 # Variable c_int '2'
MNCC_DISC_IND = 271 # Variable c_int '271'
_DEFAULT_SOURCE = 1 # Variable c_int '1'
MNCC_FACILITY_REQ = 275 # Variable c_int '275'
INT8_MIN = -128 # Variable c_int '-0x00000000000000080'
MNCC_RETRIEVE_IND = 290 # Variable c_int '290'
INTPTR_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
UINT_LEAST64_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
MNCC_F_CONNECTED = 16 # Variable c_int '16'
UINT_FAST64_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
_STDINT_H = 1 # Variable c_int '1'
MNCC_STOP_DTMF_IND = 280 # Variable c_int '280'
__USE_FORTIFY_LEVEL = 2 # Variable c_int '2'
PTRDIFF_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
MNCC_F_CCCAP = 2048 # Variable c_int '2048'
MNCC_MODIFY_CNF = 285 # Variable c_int '285'
INT32_MIN = -2147483648 # Variable c_int '-0x00000000080000000'
UINT16_MAX = 65535 # Variable c_int '65535'
MNCC_F_KEYPAD = 4096 # Variable c_int '4096'
INT_LEAST32_MAX = 2147483647 # Variable c_int '2147483647'
UINT_LEAST8_MAX = 255 # Variable c_int '255'
MNCC_HOLD_IND = 287 # Variable c_int '287'
__USE_LARGEFILE = 1 # Variable c_int '1'
__USE_EXTERN_INLINES = 1 # Variable c_int '1'
PTRDIFF_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
UINT_FAST32_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
_FEATURES_H = 1 # Variable c_int '1'
GSM_MAX_SSVERSION = 128 # Variable c_int '128'
MNCC_REJ_IND = 296 # Variable c_int '296'
MNCC_START_DTMF_RSP = 278 # Variable c_int '278'
SIG_ATOMIC_MIN = -2147483648 # Variable c_int '-0x00000000080000000'
__USE_POSIX199506 = 1 # Variable c_int '1'
MNCC_MODIFY_REQ = 282 # Variable c_int '282'
MNCC_F_FACILITY = 512 # Variable c_int '512'
SIG_ATOMIC_MAX = 2147483647 # Variable c_int '2147483647'
INT_FAST32_MIN = -9223372036854775808 # Variable c_long '-0x08000000000000000l'
MNCC_CALL_PROC_REQ = 264 # Variable c_int '264'
MNCC_SETUP_COMPL_REQ = 261 # Variable c_int '261'
MNCC_MODIFY_REJ = 286 # Variable c_int '286'
GSM_TCHF_FRAME = 768 # Variable c_int '768'
INT_FAST16_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
MNCC_START_DTMF_IND = 277 # Variable c_int '277'
_XOPEN_SOURCE_EXTENDED = 1 # Variable c_int '1'
MNCC_SETUP_IND = 258 # Variable c_int '258'
MNCC_NOTIFY_REQ = 268 # Variable c_int '268'
UINT_FAST16_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
INT_LEAST16_MIN = -32768 # Variable c_int '-0x00000000000008000'
__WORDSIZE = 64 # Variable c_int '64'
MNCC_FRAME_DROP = 514 # Variable c_int '514'
_SYS_CDEFS_H = 1 # Variable c_int '1'
INT_FAST8_MIN = -128 # Variable c_int '-0x00000000000000080'
MNCC_RETRIEVE_CNF = 291 # Variable c_int '291'
MNCC_F_EMERGENCY = 256 # Variable c_int '256'
_LARGEFILE64_SOURCE = 1 # Variable c_int '1'
MNCC_MODIFY_RSP = 284 # Variable c_int '284'
_XOPEN_SOURCE = 700 # Variable c_int '700'
MNCC_DISC_REQ = 270 # Variable c_int '270'
MNCC_SETUP_RSP = 259 # Variable c_int '259'
SIZE_MAX = 18446744073709551615L # Variable c_ulong '-1ul'
INT_FAST8_MAX = 127 # Variable c_int '127'
WINT_MIN = 0L # Variable c_uint '0u'
__USE_ISOC95 = 1 # Variable c_int '1'
MNCC_FRAME_RECV = 513 # Variable c_int '513'
UINT_LEAST16_MAX = 65535 # Variable c_int '65535'
INTPTR_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
GSM_TCHF_FRAME_EFR = 769 # Variable c_int '769'
__USE_ISOC99 = 1 # Variable c_int '1'
_BITS_WCHAR_H = 1 # Variable c_int '1'
__GLIBC_MINOR__ = 19 # Variable c_int '19'
MNCC_F_CALLING = 4 # Variable c_int '4'
INT_FAST32_MAX = 9223372036854775807 # Variable c_long '9223372036854775807l'
MNCC_F_SSVERSION = 1024 # Variable c_int '1024'
MNCC_F_BEARER_CAP = 1 # Variable c_int '1'
__USE_ISOC11 = 1 # Variable c_int '1'
WINT_MAX = 4294967295L # Variable c_uint '4294967295u'
_BSD_SOURCE = 1 # Variable c_int '1'
_LARGEFILE_SOURCE = 1 # Variable c_int '1'
GSM_BAD_FRAME = 1023 # Variable c_int '1023'
int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint8_t = c_uint8
uint64_t = c_uint64
int_least8_t = c_byte
int_least16_t = c_short
int_least32_t = c_int
int_least64_t = c_long
uint_least8_t = c_ubyte
uint_least16_t = c_ushort
uint_least32_t = c_uint
uint_least64_t = c_ulong
int_fast8_t = c_byte
int_fast16_t = c_long
int_fast32_t = c_long
int_fast64_t = c_long
uint_fast8_t = c_ubyte
uint_fast16_t = c_ulong
uint_fast32_t = c_ulong
uint_fast64_t = c_ulong
intptr_t = c_long
uintptr_t = c_ulong
intmax_t = c_long
uintmax_t = c_ulong
__all__ = ['GSM48_BCAP_SA_X28_DP_UN', 'gsm_mncc_number',
           'GSM48_BCAP_UR_9600', '_POSIX_C_SOURCE', '_ATFILE_SOURCE',
           'MNCC_SETUP_CNF', 'GSM48_BCAP_PAR_ONE', 'GSM_TCHH_FRAME',
           'UINT8_MAX', '__USE_ATFILE', 'INT_LEAST8_MAX',
           'MNCC_F_CAUSE', 'INT32_MIN', 'int_fast32_t',
           '__GNU_LIBRARY__', 'MNCC_REL_CNF', 'WINT_MIN',
           '__USE_XOPEN', '__USE_LARGEFILE64', 'MNCC_NOTIFY_REQ',
           'MNCC_RTP_CREATE', 'MNCC_REJ_IND', '__USE_XOPEN2KXSI',
           'MNCC_STOP_DTMF_RSP', 'UINT_FAST16_MAX',
           'MNCC_PROGRESS_REQ', 'uint8_t', '__USE_POSIX2',
           'GSM_TCH_FRAME_AMR', 'GSM48_BCAP_TR_RLP_PREF',
           'INT_LEAST16_MIN', 'MNCC_SETUP_COMPL_IND',
           'uint_least16_t', 'MNCC_FACILITY_IND', 'MNCC_LCHAN_MODIFY',
           'GSM_MAX_FACILITY', 'UINTMAX_MAX', 'GSM48_BCAP_SA_X21',
           '_LARGEFILE_SOURCE', 'INT_FAST16_MIN', 'MNCC_F_KEYPAD',
           'GSM_MNCC_BCAP_UNR_DIG', 'UINT64_MAX',
           'gsm_mncc_ssversion', 'GSM48_BCAP_TR_TR_PREF',
           'MNCC_START_DTMF_REJ', 'GSM48_BCAP_MT_AUTO_1',
           'INT_LEAST16_MAX', 'N19gsm_mncc_bearer_cap3DOT_0E',
           'MNCC_SOCK_VERSION', 'INTMAX_MIN', 'INT_LEAST32_MAX',
           'GSM48_BCAP_IR_16k', 'GSM48_BCAP_UR_12000',
           'GSM48_BCAP_PAR_EVEN', 'int_least16_t', 'INTMAX_MAX',
           'GSM48_BCAP_TR_RLP', 'MNCC_USERINFO_IND', '_POSIX_SOURCE',
           '_ISOC95_SOURCE', 'uint_fast16_t', 'INT64_MIN',
           '_ISOC99_SOURCE', 'uint_least8_t', 'UINT_FAST8_MAX',
           '__USE_POSIX', '__USE_SVID', 'MNCC_HOLD_CNF',
           'INT_LEAST8_MIN', 'MNCC_REL_IND', 'GSM48_BCAP_UR_1200',
           'GSM48_BCAP_MT_V26ter', 'MNCC_F_SIGNAL',
           'GSM48_BCAP_SA_X32', 'INT_FAST64_MIN', 'gsm_mncc_cause',
           'MNCC_DISC_REQ', 'MNCC_BRIDGE', 'int16_t',
           'GSM48_BCAP_UR_2400', 'uintmax_t', 'MNCC_F_CALLED',
           'UINT_LEAST32_MAX', 'MNCC_REL_REQ', 'MNCC_RTP_CONNECT',
           'GSM48_BCAP_TR_TRANSP', '__SYSCALL_WORDSIZE',
           '__GLIBC_MINOR__', 'int_least8_t', 'MNCC_SOCKET_HELLO',
           'UINT32_MAX', 'MNCC_F_PROGRESS', 'MNCC_HOLD_REJ',
           'GSM48_BCAP_SA_I440_I450', 'int64_t', 'GSM_MAX_USERUSER',
           'GSM48_BCAP_PAR_ODD', 'GSM48_BCAP_PAR_NONE', 'INT64_MAX',
           'MNCC_F_FACILITY', 'MNCC_SETUP_REQ', 'GSM48_BCAP_RA_X31',
           'gsm_mncc_bearer_cap', 'MNCC_F_USERUSER', '_SVID_SOURCE',
           '__USE_XOPEN2K', '__WORDSIZE_TIME64_COMPAT32',
           'gsm_data_frame', 'MNCC_HOLD_IND', 'GSM48_BCAP_UR_1200_75',
           'GSM48_BCAP_MT_V22bis', 'GSM_MNCC_BCAP_SPEECH',
           'MNCC_USERINFO_REQ', 'MNCC_RTP_FREE', '__USE_GNU',
           '__USE_BSD', 'gsm_mncc_cccap', 'GSM48_BCAP_PAR_ZERO',
           'MNCC_F_REDIRECTING', 'UINTPTR_MAX', 'GSM48_BCAP_RA_NONE',
           'UINT_LEAST16_MAX', 'gsm48_bcap_user_rate', 'uint16_t',
           'MNCC_MODIFY_IND', 'uint_fast8_t',
           'gsm48_bcap_interm_rate', 'gsm_mncc', 'INT16_MIN',
           '_ISOC11_SOURCE', 'MNCC_RETRIEVE_REJ', 'INT8_MAX',
           'GSM48_BCAP_MT_UNDEF', 'int32_t', 'uint_least64_t',
           'INT16_MAX', 'GSM48_BCAP_UR_4800', 'INT_LEAST64_MAX',
           'GSM48_BCAP_SA_X28_DP_IN', 'GSM_MNCC_BCAP_FAX_G3',
           '__USE_MISC', 'INTPTR_MAX', 'MNCC_DISC_IND',
           '_DEFAULT_SOURCE', 'MNCC_FACILITY_REQ',
           'gsm_mncc_useruser', 'INT8_MIN', 'MNCC_RETRIEVE_IND',
           'GSM48_BCAP_RA_V110_X30', 'gsm_mncc_progress',
           'gsm48_bcap_transp', 'INTPTR_MIN', '__USE_ISOC99',
           'UINT_LEAST64_MAX', 'MNCC_F_CONNECTED',
           'GSM_MNCC_BCAP_AUDIO', 'int_least64_t', 'UINT_FAST64_MAX',
           'uintptr_t', 'INT_FAST64_MAX', '_STDINT_H',
           'MNCC_STOP_DTMF_IND', '__USE_FORTIFY_LEVEL',
           'gsm48_bcap_parity', 'int8_t', 'PTRDIFF_MAX',
           '__USE_XOPEN2K8', 'gsm48_bcap_sig_access', 'MNCC_F_CCCAP',
           'int_fast8_t', 'MNCC_MODIFY_CNF', 'gsm_mncc_rtp',
           'INT_LEAST32_MIN', 'uint_least32_t', 'UINT16_MAX',
           'GSM48_BCAP_MT_V32', '__USE_XOPEN_EXTENDED', 'INT32_MAX',
           '__USE_UNIX98', 'UINT_LEAST8_MAX', 'uint_fast64_t',
           'INT_LEAST64_MIN', '__USE_LARGEFILE',
           '__USE_EXTERN_INLINES', 'PTRDIFF_MIN', 'UINT_FAST32_MAX',
           '_FEATURES_H', 'GSM_MNCC_BCAP_OTHER_ITC', 'gsm_mncc_hello',
           'uint64_t', 'GSM_MAX_SSVERSION', 'MNCC_ALERT_REQ',
           'GSM48_BCAP_RA_OTHER', 'MNCC_START_DTMF_RSP',
           'SIG_ATOMIC_MIN', '__USE_POSIX199506', 'MNCC_MODIFY_REQ',
           'gsm_mncc_facility', 'GSM_MNCC_BCAP_RESERVED',
           'SIG_ATOMIC_MAX', 'intptr_t', 'SIZE_MAX', 'uint_fast32_t',
           'INT_FAST32_MIN', '__USE_ISOC11', 'gsm48_bcap_modem_type',
           'int_fast16_t', 'GSM48_BCAP_UR_300',
           'MNCC_SETUP_COMPL_REQ', 'MNCC_MODIFY_REJ',
           'GSM_TCHF_FRAME', 'INT_FAST16_MAX', 'GSM48_BCAP_MT_V21',
           'GSM48_BCAP_MT_V22', 'GSM48_BCAP_MT_V23',
           'MNCC_START_DTMF_IND', '_XOPEN_SOURCE_EXTENDED',
           'MNCC_SETUP_IND', '__USE_POSIX199309', 'MNCC_NOTIFY_IND',
           '__USE_XOPEN2K8XSI', '__WORDSIZE', 'int_fast64_t',
           'MNCC_FRAME_DROP', '_SYS_CDEFS_H', 'INT_FAST8_MIN',
           'MNCC_RETRIEVE_CNF', 'MNCC_F_EMERGENCY',
           '_LARGEFILE64_SOURCE', 'MNCC_MODIFY_RSP', '_XOPEN_SOURCE',
           'MNCC_SETUP_RSP', 'MNCC_REJ_REQ', 'INT_FAST8_MAX',
           'GSM48_BCAP_MT_NONE', '__USE_ISOC95', 'MNCC_FRAME_RECV',
           'MNCC_ALERT_IND', 'intmax_t', '__GLIBC__',
           'GSM_TCHF_FRAME_EFR', 'GSM48_BCAP_SA_X28_NDP',
           '_BITS_WCHAR_H', 'N8gsm_mncc3DOT_2E', 'int_least32_t',
           'GSM48_BCAP_IR_8k', 'MNCC_F_CALLING', 'INT_FAST32_MAX',
           'MNCC_F_SSVERSION', 'MNCC_F_BEARER_CAP',
           'MNCC_CALL_PROC_REQ', 'WINT_MAX', '_BSD_SOURCE',
           'uint32_t', 'gsm48_bcap_ra', 'MNCC_CALL_CONF_IND',
           'GSM_BAD_FRAME']
