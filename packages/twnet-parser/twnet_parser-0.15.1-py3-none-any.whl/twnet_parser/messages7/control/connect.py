from typing import Literal
from twnet_parser.packer import Unpacker
from twnet_parser.pretty_print import PrettyPrint

class CtrlConnect(PrettyPrint):
    def __init__(
            self,
            response_token: bytes = b'\xff\xff\xff\xff'
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'connect'
        self.message_id: int = 1

        self.response_token: bytes = response_token

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

        yield 'response_token', self.response_token

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        # anti reflection attack
        if len(unpacker.data()) < 512:
            return False
        self.response_token = unpacker.data()[0:4]
        return True

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return self.response_token + b'\xba\xbe\xbe\x77\x00\x66\x66\x66' + bytes(500)
