from typing import Literal
from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker

import twnet_parser.msg6

"""
CtrlConnect65

with security token from 0.6.5
not compatible with 0.6.4 or earlier
also not compatible with 0.7 or later
"""
class CtrlConnect65(PrettyPrint):
    def __init__(
            self,
            response_token: bytes = b'\xff\xff\xff\xff'
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'connect'
        self.message_id: int = twnet_parser.msg6.CTRL_CONNECT

        self.response_token: bytes = response_token

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

        yield 'response_token', self.response_token

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        # reflection attack protection in 0.6 is unused
        if len(unpacker.data()) < 512:
            return False
        data = unpacker.get_raw(512)
        self.response_token = data[4:8]
        return True

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return bytes(4) + self.response_token + b'\xba\xbe\xbe\x77\x00\x66\x66\x66' + bytes(496)

class CtrlConnect64(PrettyPrint):
    def __init__(
            self
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'connect'
        self.message_id: int = twnet_parser.msg6.CTRL_CONNECT

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        return True

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return b''

class CtrlConnectDDNet(PrettyPrint):
    def __init__(
            self
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'connect'
        self.message_id: int = twnet_parser.msg6.CTRL_CONNECT

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        # TODO: we could throw some errors here

        # reflection attack protection in 0.6 is unused
        if len(unpacker.data()) != 8:
            return False
        data = unpacker.get_raw(8)
        return data == b'TKEN\xff\xff\xff\xff'

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return b'TKEN\xff\xff\xff\xff'
