from typing import Literal, Optional

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.chunk_header import ChunkHeader

class MsgDDNetUuid(PrettyPrint):
    def __init__(
            self,
            chunk_header: Optional[ChunkHeader] = None,
            payload: bytes = b''
    ) -> None:
        self.message_type: Literal['system', 'game'] = 'system'
        self.message_name: str = 'ddnet_uuid'
        self.system_message: bool = True
        self.message_id: int = 0
        if not chunk_header:
            chunk_header = ChunkHeader(version = '0.6')
        self.header: ChunkHeader = chunk_header

        self.payload: bytes = payload

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'system_message', self.system_message
        yield 'message_id', self.message_id
        yield 'header', dict(self.header)

        yield 'payload', self.payload

    # first byte of data
    # has to be the first byte of the message payload
    # NOT the chunk header and NOT the message id
    def unpack(self, data: bytes) -> bool:
        self.payload = data
        return True

    def pack(self) -> bytes:
        return self.payload
