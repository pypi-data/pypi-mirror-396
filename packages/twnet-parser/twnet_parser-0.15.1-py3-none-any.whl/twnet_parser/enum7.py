# pylint: disable=duplicate-code
from enum import Enum

class Pickup(Enum):
    HEALTH = 0
    ARMOR = 1
    GRENADE = 2
    SHOTGUN = 3
    LASER = 4
    NINJA = 5
    GUN = 6
    HAMMER = 7

class Emote(Enum):
    NORMAL = 0
    PAIN = 1
    HAPPY = 2
    SURPRISE = 3
    ANGRY = 4
    BLINK = 5

class Emoticon(Enum):
    OOP = 0
    EXCLAMATION = 1
    HEARTS = 2
    DROP = 3
    DOTDOT = 4
    MUSIC = 5
    SORRY = 6
    GHOST = 7
    SUSHI = 8
    SPLATTEE = 9
    DEVILTEE = 10
    ZOMG = 11
    ZZZ = 12
    WTF = 13
    EYES = 14
    QUESTION = 15

class Vote(Enum):
    UNKNOWN = 0
    START_OP = 1
    START_KICK = 2
    START_SPEC = 3
    END_ABORT = 4
    END_PASS = 5
    END_FAIL = 6

class Chat(Enum):
    NONE = 0
    ALL = 1
    TEAM = 2
    WHISPER = 3

class Gamemsg(Enum):
    TEAM_SWAP = 0
    SPEC_INVALIDID = 1
    TEAM_SHUFFLE = 2
    TEAM_BALANCE = 3
    CTF_DROP = 4
    CTF_RETURN = 5
    TEAM_ALL = 6
    TEAM_BALANCE_VICTIM = 7
    CTF_GRAB = 8
    CTF_CAPTURE = 9
    GAME_PAUSED = 10

class Weapon(Enum):
    HAMMER = 0
    PISTOL = 1
    SHOTGUN = 2
    GRENADE = 3
    RIFLE = 4
    NINJA = 5

class Team(Enum):
    SPECTATORS = -1
    RED = 0
    BLUE = 1

class Sound(Enum):
    GUN_FIRE = 0
    SHOTGUN_FIRE = 1
    GRENADE_FIRE = 2
    HAMMER_FIRE = 3
    HAMMER_HIT = 4
    NINJA_FIRE = 5
    GRENADE_EXPLODE = 6
    NINJA_HIT = 7
    RIFLE_FIRE = 8
    RIFLE_BOUNCE = 9
    WEAPON_SWITCH = 10
    PLAYER_PAIN_SHORT = 11
    PLAYER_PAIN_LONG = 12
    BODY_LAND = 13
    PLAYER_AIRJUMP = 14
    PLAYER_JUMP = 15
    PLAYER_DIE = 16
    PLAYER_SPAWN = 17
    PLAYER_SKID = 18
    TEE_CRY = 19
    HOOK_LOOP = 20
    HOOK_ATTACH_GROUND = 21
    HOOK_ATTACH_PLAYER = 22
    HOOK_NOATTACH = 23
    PICKUP_HEALTH = 24
    PICKUP_ARMOR = 25
    PICKUP_GRENADE = 26
    PICKUP_SHOTGUN = 27
    PICKUP_NINJA = 28
    WEAPON_SPAWN = 29
    WEAPON_NOAMMO = 30
    HIT = 31
    CHAT_SERVER = 32
    CHAT_CLIENT = 33
    CHAT_HIGHLIGHT = 34
    CTF_DROP = 35
    CTF_RETURN = 36
    CTF_GRAB_PL = 37
    CTF_GRAB_EN = 38
    CTF_CAPTURE = 39
    MENU = 40

class Spec(Enum):
    FREEVIEW = 0
    PLAYER = 1
    FLAGRED = 2
    FLAGBLUE = 3

class Skinpart(Enum):
    BODY = 0
    MARKING = 1
    DECORATION = 2
    HANDS = 3
    FEET = 4
    EYES = 5
