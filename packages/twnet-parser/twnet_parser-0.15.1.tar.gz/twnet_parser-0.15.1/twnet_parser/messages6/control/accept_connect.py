from typing import Literal

from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker
import twnet_parser.msg6

"""
Sent by the server in response to the connect message
"""
class CtrlAcceptConnect(PrettyPrint):
    def __init__(
            self,
            response_token: bytes = b'\xff\xff\xff\xff'
    ) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'connect_accept'
        self.message_id: int = twnet_parser.msg6.CTRL_CONNECT_ACCEPT

        self.response_token: bytes = response_token

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

        yield 'response_token', self.response_token

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        self.response_token = unpacker.get_raw(4)
        return True

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return self.response_token
