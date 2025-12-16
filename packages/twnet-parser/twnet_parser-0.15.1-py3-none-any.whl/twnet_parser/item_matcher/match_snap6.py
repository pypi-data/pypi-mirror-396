from typing import Optional

from twnet_parser.packer import Unpacker
from twnet_parser.snap.unknown import ObjUnknown
from twnet_parser.snap_item import SnapItem

import twnet_parser.obj6

from twnet_parser.snap6.player_input import ObjPlayerInput
from twnet_parser.snap6.projectile import ObjProjectile
from twnet_parser.snap6.laser import ObjLaser
from twnet_parser.snap6.pickup import ObjPickup
from twnet_parser.snap6.flag import ObjFlag
from twnet_parser.snap6.game_info import ObjGameInfo
from twnet_parser.snap6.game_data import ObjGameData
from twnet_parser.snap6.character_core import ObjCharacterCore
from twnet_parser.snap6.character import ObjCharacter
from twnet_parser.snap6.player_info import ObjPlayerInfo
from twnet_parser.snap6.client_info import ObjClientInfo
from twnet_parser.snap6.spectator_info import ObjSpectatorInfo
from twnet_parser.snap6.common import ObjCommon
from twnet_parser.snap6.explosion import ObjExplosion
from twnet_parser.snap6.spawn import ObjSpawn
from twnet_parser.snap6.hammer_hit import ObjHammerHit
from twnet_parser.snap6.death import ObjDeath
from twnet_parser.snap6.sound_global import ObjSoundGlobal
from twnet_parser.snap6.sound_world import ObjSoundWorld
from twnet_parser.snap6.damage_ind import ObjDamageInd

def match_item(unpacker: Unpacker) -> Optional[SnapItem]:
    item_type = unpacker.get_int()
    item: SnapItem
    if item_type == twnet_parser.obj6.PLAYER_INPUT:
        item = ObjPlayerInput()
    elif item_type == twnet_parser.obj6.PROJECTILE:
        item = ObjProjectile()
    elif item_type == twnet_parser.obj6.LASER:
        item = ObjLaser()
    elif item_type == twnet_parser.obj6.PICKUP:
        item = ObjPickup()
    elif item_type == twnet_parser.obj6.FLAG:
        item = ObjFlag()
    elif item_type == twnet_parser.obj6.GAME_INFO:
        item = ObjGameInfo()
    elif item_type == twnet_parser.obj6.GAME_DATA:
        item = ObjGameData()
    elif item_type == twnet_parser.obj6.CHARACTER_CORE:
        item = ObjCharacterCore()
    elif item_type == twnet_parser.obj6.CHARACTER:
        item = ObjCharacter()
    elif item_type == twnet_parser.obj6.PLAYER_INFO:
        item = ObjPlayerInfo()
    elif item_type == twnet_parser.obj6.CLIENT_INFO:
        item = ObjClientInfo()
    elif item_type == twnet_parser.obj6.SPECTATOR_INFO:
        item = ObjSpectatorInfo()
    elif item_type == twnet_parser.obj6.COMMON:
        item = ObjCommon()
    elif item_type == twnet_parser.obj6.EXPLOSION:
        item = ObjExplosion()
    elif item_type == twnet_parser.obj6.SPAWN:
        item = ObjSpawn()
    elif item_type == twnet_parser.obj6.HAMMERHIT:
        item = ObjHammerHit()
    elif item_type == twnet_parser.obj6.DEATH:
        item = ObjDeath()
    elif item_type == twnet_parser.obj6.SOUND_GLOBAL:
        item = ObjSoundGlobal()
    elif item_type == twnet_parser.obj6.SOUND_WORLD:
        item = ObjSoundWorld()
    elif item_type == twnet_parser.obj6.DAMAGE_INDICATOR:
        item = ObjDamageInd()
    else:
        item = ObjUnknown()
        item.type_id = item_type
    return item

