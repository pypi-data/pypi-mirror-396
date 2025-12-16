# connless
# pylint: disable=duplicate-code

CONNLESS_HEARTBEAT = b'\xff\xff\xff\xffbea2'
CONNLESS_REQUEST_LIST = b'\xff\xff\xff\xffreq2'
CONNLESS_LIST = b'\xff\xff\xff\xfflis2'
CONNLESS_REQUEST_COUNT = b'\xff\xff\xff\xffcou2'
CONNLESS_COUNT = b'\xff\xff\xff\xffsiz2'
CONNLESS_REQUEST_INFO = b'\xff\xff\xff\xffgie3'
CONNLESS_INFO = b'\xff\xff\xff\xffinf3'
CONNLESS_FORWARD_CHECK = b'\xff\xff\xff\xfffw??'
CONNLESS_FORWARD_RESPONSE = b'\xff\xff\xff\xfffw!!'
CONNLESS_FORWARD_OK = b'\xff\xff\xff\xfffwok'
CONNLESS_FORWARD_ERROR = b'\xff\xff\xff\xfffwer'

# control

CTRL_KEEPALIVE = 0
CTRL_CONNECT = 1
CTRL_CONNECT_ACCEPT = 2
CTRL_ACCEPT = 3 # got remove in 0.6.5
CTRL_CLOSE = 4

# system
INFO = 1
MAP_CHANGE = 2 # sent when client should switch map
MAP_DATA = 3 # map transfer, contains a chunk of the map file
CON_READY = 4 # connection is ready, client should send start info
SNAP = 5 # normal snapshot, multiple parts
SNAP_EMPTY = 6 # empty snapshot
SNAP_SINGLE = 7
SNAP_SMALL = 8
INPUT_TIMING = 9	# reports how off the input was
RCON_AUTH_STATUS = 10# result of the authentication
RCON_LINE = 11 # line that should be printed to the remote console
AUTH_CHALLANGE = 12
AUTH_RESULT = 13
READY = 14
ENTER_GAME = 15
INPUT = 16 # contains the inputdata from the client
RCON_CMD = 17
RCON_AUTH = 18
REQUEST_MAP_DATA = 19
AUTH_START = 20
AUTH_RESPONSE = 21
PING = 22
PING_REPLY = 23
ERROR = 24
RCON_CMD_ADD = 25
RCON_CMD_REMOVE = 26

# game
INVALID = 0
SV_MOTD = 1
SV_BROADCAST = 2
SV_CHAT = 3
SV_KILL_MSG = 4
SV_SOUND_GLOBAL = 5
SV_TUNE_PARAMS = 6
SV_EXTRA_PROJECTILE = 7
SV_READY_TO_ENTER = 8
SV_WEAPON_PICKUP = 9
SV_EMOTICON = 10
SV_VOTE_CLEAR_OPTIONS = 11
SV_VOTE_OPTION_LIST_ADD = 12
SV_VOTE_OPTION_ADD = 13
SV_VOTE_OPTION_REMOVE = 14
SV_VOTE_SET = 15
SV_VOTE_STATUS = 16
CL_SAY = 17
CL_SET_TEAM = 18
CL_SET_SPECTATOR_MODE = 19
CL_START_INFO = 20
CL_CHANGE_INFO = 21
CL_KILL = 22
CL_EMOTICON = 23
CL_VOTE = 24
CL_CALL_VOTE = 25
NUM_GAME_MESSAGES = 26

