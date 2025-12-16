from typing import Optional, Literal

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
from twnet_parser.packer import pack_str

class CtrlClose(PrettyPrint):
    def __init__(
            self,
            reason: Optional[str] = None
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'close'
        self.message_id: int = 4

        self.reason: Optional[str] = reason

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

        yield 'reason', self.reason

    # first byte of data
    # has to be the first byte of the message payload
    # NOT the chunk header and NOT the message id
    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        self.reason = unpacker.get_optional_str()
        return True

    def pack(self, we_are_a_client: bool = True) -> bytes:
        if self.reason:
            return pack_str(self.reason)
        return b''
