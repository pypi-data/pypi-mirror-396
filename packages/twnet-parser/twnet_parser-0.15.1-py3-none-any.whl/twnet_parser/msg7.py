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
CTRL_ACCEPT = 2
# yes control message 3 is missing in 0.7
CTRL_CLOSE = 4
CTRL_TOKEN = 5

# system
NULL = 0
INFO = 1
MAP_CHANGE = 2 # sent when client should switch map
MAP_DATA = 3   # map transfer, contains a chunk of the map file
SERVER_INFO = 4
CON_READY = 5  # connection is ready, client should send start info
SNAP = 6       # normal snapshot, multiple parts
SNAP_EMPTY = 7  # empty snapshot
SNAP_SINGLE = 8 # ?
SNAP_SMALL = 9
INPUT_TIMING = 10   # reports how off the input was
RCON_AUTH_ON = 11  # rcon authentication enabled
RCON_AUTH_OFF = 12 # rcon authentication disabled
RCON_LINE = 13     # line that should be printed to the remote console
RCON_CMD_ADD = 14
RCON_CMD_REM = 15
AUTH_CHALLENGE = 16
AUTH_RESULT = 17
READY = 18
ENTER_GAME = 19
INPUT = 20
RCON_CMD = 21
RCON_AUTH = 22
REQUEST_MAP_DATA = 23
AUTH_START = 24
AUTH_RESPONSE = 25
PING = 26
PING_REPLY = 27
ERROR = 28
MAPLIST_ENTRY_ADD = 29
MAPLIST_ENTRY_REM = 30

# game
INVALID = 0
SV_MOTD = 1
SV_BROADCAST = 2
SV_CHAT = 3
SV_TEAM = 4
SV_KILL_MSG = 5
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
SV_SERVER_SETTINGS = 17
SV_CLIENT_INFO = 18
SV_GAME_INFO = 19
SV_CLIENT_DROP = 20
SV_GAME_MSG = 21
DE_CLIENT_ENTER = 22
DE_CLIENT_LEAVE = 23
CL_SAY = 24
CL_SET_TEAM = 25
CL_SET_SPECTATOR_MODE = 26
CL_START_INFO = 27
CL_KILL = 28
CL_READY_CHANGE = 29
CL_EMOTICON = 30
CL_VOTE = 31
CL_CALL_VOTE = 32
SV_SKIN_CHANGE = 33
CL_SKIN_CHANGE = 34
SV_RACE_FINISH = 35
SV_CHECKPOINT = 36
SV_COMMAND_INFO = 37
SV_COMMAND_INFO_REMOVE = 38
CL_COMMAND = 39
NUM_GAME_MESSAGES = 40
