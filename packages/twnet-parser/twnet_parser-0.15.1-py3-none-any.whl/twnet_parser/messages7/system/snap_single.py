from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
from twnet_parser.chunk_header import ChunkHeader
from twnet_parser.packer import pack_int
from typing import Literal, Optional

from twnet_parser.snapshot import Snapshot

class MsgSnapSingle(PrettyPrint):
    def __init__(
            self,
            chunk_header: Optional[ChunkHeader] = None,
            tick: int = 0,
            delta_tick: int = 0,
            crc: int = 0,
            data_size: Optional[int] = None,
            data: bytes = b'\x00'
    ) -> None:
        self.message_type: Literal['system', 'game'] = 'system'
        self.message_name: str = 'snap_single'
        self.system_message: bool = True
        self.message_id: int = 8
        if not chunk_header:
            chunk_header = ChunkHeader(version = '0.7')
        self.header: ChunkHeader = chunk_header

        self.tick: int = tick
        self.delta_tick: int = delta_tick
        self.crc: int = crc
        self.data_size: int = data_size if data_size else len(data)
        self.data: bytes = data
        self.snapshot = Snapshot(version='0.7')

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'system_message', self.system_message
        yield 'message_id', self.message_id
        yield 'header', dict(self.header)

        yield 'tick', self.tick
        yield 'delta_tick', self.delta_tick
        yield 'crc', self.crc
        yield 'data', self.data

        # TODO: dict snapshot
        # yield 'snapshot', 'TODO'

    # first byte of data
    # has to be the first byte of the message payload
    # NOT the chunk header and NOT the message id
    def unpack(self, data: bytes) -> bool:
        unpacker = Unpacker(data)
        self.tick = unpacker.get_int()
        self.delta_tick = unpacker.get_int()
        self.crc = unpacker.get_int()
        self.data_size = unpacker.get_int()
        self.data = unpacker.get_raw(self.data_size)
        self.snapshot.unpack(self.data)
        return True

    def pack(self) -> bytes:
        return pack_int(self.tick) + \
            pack_int(self.delta_tick) + \
            pack_int(self.crc) + \
            pack_int(self.data_size) + \
            self.data
