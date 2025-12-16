from typing import Any, Dict

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
from twnet_parser.packer import pack_int

# special meta item that represents unknown items
class ObjUnknown(PrettyPrint):
    def __init__(self) -> None:
        self.item_name: str = 'obj.unknown'
        self.type_id: int = 0
        self.id: int = 0
        self.size: int = 0

        self.fields: list[int] = []

    def __iter__(self):
        yield 'item_name', self.item_name
        yield 'type_id', self.type_id
        yield 'id', self.id
        yield 'size', self.size

        yield 'fields', self.fields

    def to_dict_payload_only(self) -> Dict[str, Any]:
        return {
            'fields': self.fields
        }

    # first byte of data
    # has to be the first byte of the message payload
    # NOT the chunk header and NOT the message id
    def unpack(self, unpacker: Unpacker) -> bool:
        # TODO: this is a bit weird
        #       the size is kinda part of the "header"
        #       but only for unknown items
        #       so the unknown item uses the same interface
        #       which promises to unpack the "payload" only
        #       is the size now header or payload?
        self.size = unpacker.get_int()

        self.fields = []
        for _ in range(0, self.size):
            self.fields.append(unpacker.get_int())
        return True

    def pack(self) -> bytes:
        data = pack_int(self.size)
        for i in range(0, self.size):
            data += pack_int(self.fields[i])
        return data
