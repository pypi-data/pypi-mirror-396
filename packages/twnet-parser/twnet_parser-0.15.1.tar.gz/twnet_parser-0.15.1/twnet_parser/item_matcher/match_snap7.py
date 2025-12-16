from typing import Optional

from twnet_parser.packer import Unpacker
from twnet_parser.snap.unknown import ObjUnknown
from twnet_parser.snap_item import SnapItem

import twnet_parser.obj7

from twnet_parser.snap7.player_input import ObjPlayerInput
from twnet_parser.snap7.projectile import ObjProjectile
from twnet_parser.snap7.laser import ObjLaser
from twnet_parser.snap7.pickup import ObjPickup
from twnet_parser.snap7.flag import ObjFlag
from twnet_parser.snap7.game_data import ObjGameData
from twnet_parser.snap7.game_data_team import ObjGameDataTeam
from twnet_parser.snap7.game_data_flag import ObjGameDataFlag
from twnet_parser.snap7.character_core import ObjCharacterCore
from twnet_parser.snap7.character import ObjCharacter
from twnet_parser.snap7.player_info import ObjPlayerInfo
from twnet_parser.snap7.spectator_info import ObjSpectatorInfo
from twnet_parser.snap7.de_client_info import ObjDeClientInfo
from twnet_parser.snap7.de_game_info import ObjDeGameInfo
from twnet_parser.snap7.de_tune_params import ObjDeTuneParams
from twnet_parser.snap7.common import ObjCommon
from twnet_parser.snap7.explosion import ObjExplosion
from twnet_parser.snap7.spawn import ObjSpawn
from twnet_parser.snap7.hammer_hit import ObjHammerHit
from twnet_parser.snap7.death import ObjDeath
from twnet_parser.snap7.sound_world import ObjSoundWorld
from twnet_parser.snap7.damage import ObjDamage
from twnet_parser.snap7.player_info_race import ObjPlayerInfoRace
from twnet_parser.snap7.game_data_race import ObjGameDataRace

def match_item(unpacker: Unpacker) -> Optional[SnapItem]:
    item_type = unpacker.get_int()
    item: SnapItem
    if item_type == twnet_parser.obj7.PLAYER_INPUT:
        item = ObjPlayerInput()
    elif item_type == twnet_parser.obj7.PROJECTILE:
        item = ObjProjectile()
    elif item_type == twnet_parser.obj7.LASER:
        item = ObjLaser()
    elif item_type == twnet_parser.obj7.PICKUP:
        item = ObjPickup()
    elif item_type == twnet_parser.obj7.FLAG:
        item = ObjFlag()
    elif item_type == twnet_parser.obj7.GAME_DATA:
        item = ObjGameData()
    elif item_type == twnet_parser.obj7.GAME_DATA_TEAM:
        item = ObjGameDataTeam()
    elif item_type == twnet_parser.obj7.GAME_DATA_FLAG:
        item = ObjGameDataFlag()
    elif item_type == twnet_parser.obj7.CHARACTER_CORE:
        item = ObjCharacterCore()
    elif item_type == twnet_parser.obj7.CHARACTER:
        item = ObjCharacter()
    elif item_type == twnet_parser.obj7.PLAYER_INFO:
        item = ObjPlayerInfo()
    elif item_type == twnet_parser.obj7.SPECTATOR_INFO:
        item = ObjSpectatorInfo()
    elif item_type == twnet_parser.obj7.DE_CLIENT_INFO:
        item = ObjDeClientInfo()
    elif item_type == twnet_parser.obj7.DE_GAME_INFO:
        item = ObjDeGameInfo()
    elif item_type == twnet_parser.obj7.DE_TUNE_PARAMS:
        item = ObjDeTuneParams()
    elif item_type == twnet_parser.obj7.COMMON:
        item = ObjCommon()
    elif item_type == twnet_parser.obj7.EXPLOSION:
        item = ObjExplosion()
    elif item_type == twnet_parser.obj7.SPAWN:
        item = ObjSpawn()
    elif item_type == twnet_parser.obj7.HAMMERHIT:
        item = ObjHammerHit()
    elif item_type == twnet_parser.obj7.DEATH:
        item = ObjDeath()
    elif item_type == twnet_parser.obj7.SOUND_WORLD:
        item = ObjSoundWorld()
    elif item_type == twnet_parser.obj7.DAMAGE:
        item = ObjDamage()
    elif item_type == twnet_parser.obj7.PLAYER_INFO_RACE:
        item = ObjPlayerInfoRace()
    elif item_type == twnet_parser.obj7.GAME_DATA_RACE:
        item = ObjGameDataRace()
    else:
        item = ObjUnknown()
        item.type_id = item_type
    return item

