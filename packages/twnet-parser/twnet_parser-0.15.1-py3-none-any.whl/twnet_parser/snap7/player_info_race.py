from typing import Any, Dict

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
from twnet_parser.packer import pack_int

class ObjPlayerInfoRace(PrettyPrint):
    def __init__(
            self,
            race_start_tick: int = 0
    ) -> None:
        self.item_name: str = 'obj.player_info_race'
        self.type_id: int = 23
        self.id: int = 0
        self.size: int = 1

        self.race_start_tick: int = race_start_tick

    def __iter__(self):
        yield 'item_name', self.item_name
        yield 'type_id', self.type_id
        yield 'id', self.id
        yield 'size', self.size

        yield 'race_start_tick', self.race_start_tick

    def to_dict_payload_only(self) -> Dict[str, Any]:
        return {
            'race_start_tick': self.race_start_tick
        }

    # first byte of data
    # has to be the first byte of the message payload
    # NOT the chunk header and NOT the message id
    def unpack(self, unpacker: Unpacker) -> bool:
        # TODO: it is weird to unpack the size here because
        #       it is not really part of the payload
        #       but this is one of the two edge cases messages
        #       this patch is also why it has to be excluded from the generation script
        self.size = unpacker.get_int()

        self.race_start_tick = unpacker.get_int()
        return True

    def pack(self) -> bytes:
        return pack_int(self.size) + \
            pack_int(self.race_start_tick)
