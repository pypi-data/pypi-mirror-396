# pylint: disable=duplicate-code
from enum import Enum

class Emote(Enum):
    NORMAL = 0
    PAIN = 1
    HAPPY = 2
    SURPRISE = 3
    ANGRY = 4
    BLINK = 5

class Powerup(Enum):
    HEALTH = 0
    ARMOR = 1
    WEAPON = 2
    NINJA = 3

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
