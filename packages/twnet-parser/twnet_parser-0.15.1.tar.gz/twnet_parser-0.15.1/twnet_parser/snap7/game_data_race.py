from typing import Any, Dict

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
from twnet_parser.packer import pack_int

class ObjGameDataRace(PrettyPrint):
    def __init__(
            self,
            best_time: int = 0,
            precision: int = 0,
            race_flags: int = 0
    ) -> None:
        self.item_name: str = 'obj.game_data_race'
        self.type_id: int = 24
        self.id: int = 0
        self.size: int = 3

        self.best_time: int = best_time
        self.precision: int = precision
        self.race_flags: int = race_flags

    def __iter__(self):
        yield 'item_name', self.item_name
        yield 'type_id', self.type_id
        yield 'id', self.id
        yield 'size', self.size

        yield 'best_time', self.best_time
        yield 'precision', self.precision
        yield 'race_flags', self.race_flags

    def to_dict_payload_only(self) -> Dict[str, Any]:
        return {
            'best_time': self.best_time,
            'precision': self.precision,
            'race_flags': self.race_flags
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

        self.best_time = unpacker.get_int()
        self.precision = unpacker.get_int()
        self.race_flags = unpacker.get_int() # TODO: this is a flag
        return True

    def pack(self) -> bytes:
        return pack_int(self.size) + \
            pack_int(self.best_time) + \
            pack_int(self.precision) + \
            pack_int(self.race_flags)
